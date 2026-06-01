"""
Endpoints do dashboard e conversas.

Métricas e listagem de conversas para o dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from src.api.middleware.auth import get_current_user
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Dashboard"])


# ========================================
# Dependencies
# ========================================

def _get_bot_repo():
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository
    return MongoBotRepository(MongoDB.get_database())


def _get_conversation_repo():
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.conversation_repository_impl import MongoConversationRepository
    return MongoConversationRepository(MongoDB.get_database())


# ========================================
# Dashboard Metrics
# ========================================

@router.get(
    "/dashboard/metrics",
    summary="Métricas do dashboard",
    description="Retorna métricas agregadas para o dashboard do usuário.",
)
async def get_dashboard_metrics(
    current_user=Depends(get_current_user),
):
    """Retorna métricas do dashboard."""
    try:
        bot_repo = _get_bot_repo()
        usuario_id = str(current_user.id)

        bots = await bot_repo.listar_por_usuario(usuario_id)
        total_bots = len(bots)
        active_bots = sum(1 for b in bots if b.status.value == "active")
        paused_bots = sum(1 for b in bots if b.status.value == "paused")
        total_messages = sum(b.estatisticas.total_mensagens for b in bots)
        total_conversations = sum(b.estatisticas.total_conversas for b in bots)
        ia_active = sum(1 for b in bots if b.llm_config.ativado)

        return {
            "bots": {
                "total": total_bots,
                "ativos": active_bots,
                "pausados": paused_bots,
            },
            "mensagens": {
                "total": total_messages,
            },
            "conversas": {
                "total": total_conversations,
            },
            "ia": {
                "ativa": ia_active > 0,
                "bots_com_ia": ia_active,
            },
        }
    except Exception as e:
        logger.error(f"Erro ao buscar métricas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar métricas"}},
        )


# ========================================
# Conversas
# ========================================

@router.get(
    "/conversations",
    summary="Listar conversas",
    description="Lista conversas dos bots do usuário.",
)
async def list_conversations(
    bot_id: Optional[str] = Query(None, description="Filtrar por bot"),
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    """Lista conversas do usuário."""
    try:
        conv_repo = _get_conversation_repo()
        bot_repo = _get_bot_repo()
        usuario_id = str(current_user.id)

        # Buscar bots do usuário
        bots = await bot_repo.listar_por_usuario(usuario_id)
        bot_ids = [str(b.id) for b in bots]

        # Filtrar por bot_id específico se fornecido
        if bot_id and bot_id not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Bot não pertence a este usuário"}},
            )

        # Buscar conversas
        all_conversations = []
        target_bot_ids = [bot_id] if bot_id else bot_ids

        for bid in target_bot_ids:
            convs = await conv_repo.find_by_bot(bid, limit=100)
            all_conversations.extend(convs)

        # Filtrar por status
        if status_filter:
            all_conversations = [
                c for c in all_conversations
                if c.status.value == status_filter
            ]

        # Paginação
        total = len(all_conversations)
        start = (pagina - 1) * tamanho_pagina
        page_conversations = all_conversations[start:start + tamanho_pagina]

        return {
            "data": [
                {
                    "id": c.id,
                    "bot_id": c.bot_id,
                    "cliente": {
                        "id": c.cliente.id,
                        "nome": c.cliente.obter_nome_exibicao(),
                        "telefone": c.cliente.telefone,
                    },
                    "status": c.status.value,
                    "ultima_mensagem_em": c.ultima_mensagem_em,
                    "criado_em": c.criado_em,
                }
                for c in page_conversations
            ],
            "total": total,
            "pagina": pagina,
            "tamanho_pagina": tamanho_pagina,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao listar conversas"}},
        )


@router.get(
    "/conversations/{conversation_id}",
    summary="Buscar conversa",
    description="Busca uma conversa específica.",
)
async def get_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
):
    """Busca uma conversa por ID."""
    try:
        conv_repo = _get_conversation_repo()
        conversation = await conv_repo.find_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Conversa não encontrada"}},
            )

        # Verificar pertencimento ao usuário
        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_ids = [str(b.id) for b in bots]

        if conversation.bot_id not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Conversa não pertence a este usuário"}},
            )

        return {
            "id": conversation.id,
            "bot_id": conversation.bot_id,
            "cliente": {
                "id": conversation.cliente.id,
                "nome": conversation.cliente.obter_nome_exibicao(),
                "telefone": conversation.cliente.telefone,
            },
            "status": conversation.status.value,
            "primeira_mensagem_em": conversation.primeira_mensagem_em,
            "ultima_mensagem_em": conversation.ultima_mensagem_em,
            "criado_em": conversation.criado_em,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar conversa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar conversa"}},
        )


# ========================================
# Contatos
# ========================================

def _get_contact_repo():
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.contact_repository_impl import MongoContactRepository
    return MongoContactRepository(MongoDB.get_database())


@router.get(
    "/contacts",
    summary="Listar contatos",
    description="Lista contatos/leads dos bots do usuário.",
)
async def list_contacts(
    bot_id: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Buscar por nome"),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    """Lista contatos do usuário."""
    try:
        contact_repo = _get_contact_repo()
        usuario_id = str(current_user.id)

        if search:
            contacts = await contact_repo.buscar_por_nome(usuario_id, search, limit=100)
        elif tag:
            contacts = await contact_repo.listar_por_tag(usuario_id, tag)
        elif bot_id:
            contacts = await contact_repo.listar_por_bot(bot_id)
        else:
            contacts = await contact_repo.listar_por_usuario(usuario_id)

        total = len(contacts)
        start = (pagina - 1) * tamanho_pagina
        page_contacts = contacts[start:start + tamanho_pagina]

        return {
            "data": [
                {
                    "id": c.id,
                    "bot_id": c.bot_id,
                    "nome": c.nome,
                    "telefone": c.telefone,
                    "email": c.email,
                    "origem": c.origem if isinstance(c.origem, str) else c.origem.value,
                    "tags": c.tags,
                    "status": c.status if isinstance(c.status, str) else c.status.value,
                    "ultima_mensagem_em": c.ultima_mensagem_em,
                    "total_mensagens": c.total_mensagens,
                    "total_conversas": c.total_conversas,
                    "criado_em": c.criado_em,
                }
                for c in page_contacts
            ],
            "total": total,
            "pagina": pagina,
            "tamanho_pagina": tamanho_pagina,
        }
    except Exception as e:
        logger.error(f"Erro ao listar contatos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao listar contatos"}},
        )


@router.delete(
    "/contacts/{contact_id}",
    summary="Deletar contato",
    description="Remove um contato.",
)
async def delete_contact(
    contact_id: str,
    current_user=Depends(get_current_user),
):
    """Deleta um contato."""
    try:
        contact_repo = _get_contact_repo()
        contact = await contact_repo.buscar_por_id(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Contato não encontrado"}},
            )

        if str(contact.usuario_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Contato não pertence a este usuário"}},
            )

        await contact_repo.deletar(contact_id)
        return {"message": "Contato removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar contato: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao deletar contato"}},
        )

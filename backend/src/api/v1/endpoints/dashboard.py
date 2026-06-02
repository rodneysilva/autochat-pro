"""
Endpoints do dashboard e conversas.

Métricas e listagem de conversas para o dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.api.middleware.auth import get_current_user
from src.shared.utils.logger import get_logger

from src.infrastructure.database.seeds import PLANS_CONFIG
from src.infrastructure.database.mongodb import MongoDB

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

        # Métricas avançadas
        db = MongoDB.get_database()
        bot_object_ids = [b.id for b in bots]

        # Mensagens de hoje
        from datetime import datetime, timezone
        hoje_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        mensagens_hoje = await db.messages.count_documents({
            "bot_id": {"$in": bot_object_ids},
            "created_at": {"$gte": hoje_inicio},
        })

        # Conversas ativas
        conversas_ativas = await db.conversations.count_documents({
            "bot_id": {"$in": bot_object_ids},
            "status": "active",
        })

        return {
            "bots": {
                "total": total_bots,
                "ativos": active_bots,
                "pausados": paused_bots,
            },
            "mensagens": {
                "total": total_messages,
                "hoje": mensagens_hoje,
            },
            "conversas": {
                "total": total_conversations,
                "ativas": conversas_ativas,
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
# Dashboard — Timeline de mensagens
# ========================================

@router.get(
    "/dashboard/metrics/timeline",
    summary="Timeline de mensagens",
    description="Retorna contagem de mensagens por dia nos últimos 30 dias.",
)
async def get_message_timeline(
    current_user=Depends(get_current_user),
):
    """Retorna mensagens agrupadas por dia (últimos 30 dias)."""
    try:
        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_object_ids = [b.id for b in bots]

        from datetime import datetime, timezone, timedelta
        db = MongoDB.get_database()

        trinta_dias_atras = datetime.now(timezone.utc) - timedelta(days=30)

        pipeline = [
            {
                "$match": {
                    "bot_id": {"$in": bot_object_ids},
                    "created_at": {"$gte": trinta_dias_atras},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"},
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = await db.messages.aggregate(pipeline).to_list(31)

        return [
            {"date": r["_id"], "count": r["count"]}
            for r in results
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar timeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar timeline"}},
        )


# ========================================
# Dashboard — Top contatos
# ========================================

@router.get(
    "/dashboard/metrics/top-contacts",
    summary="Top contatos por volume",
    description="Retorna top 10 contatos com mais mensagens.",
)
async def get_top_contacts(
    current_user=Depends(get_current_user),
):
    """Retorna top 10 contatos por volume de mensagens."""
    try:
        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_object_ids = [b.id for b in bots]

        db = MongoDB.get_database()

        pipeline = [
            {
                "$match": {
                    "bot_id": {"$in": bot_object_ids},
                    "role": "customer",
                }
            },
            {
                "$group": {
                    "_id": "$customer_id",
                    "count": {"$sum": 1},
                    "lastMessage": {"$last": "$content"},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]

        results = await db.messages.aggregate(pipeline).to_list(10)

        contacts = []
        for r in results:
            customer_id = r["_id"]
            # Buscar nome do contato se disponível
            nome = customer_id
            conv = await db.conversations.find_one({
                "customer.id": customer_id,
                "bot_id": {"$in": bot_object_ids},
            }, sort=[("created_at", -1)])
            if conv and conv.get("customer"):
                nome = conv["customer"].get("name", customer_id)
                if not nome:
                    nome = conv["customer"].get("push_name", customer_id)

            contacts.append({
                "id": customer_id,
                "name": nome,
                "count": r["count"],
                "lastMessage": (r["lastMessage"] or "")[:100],
            })

        return contacts
    except Exception as e:
        logger.error(f"Erro ao buscar top contatos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar top contatos"}},
        )


# ========================================
# Conversas — Ações
# ========================================

class AssignRequest(BaseModel):
    user_id: str


@router.get(
    "/conversations/{conversation_id}/messages",
    summary="Mensagens da conversa",
    description="Retorna todas as mensagens de uma conversa.",
)
async def get_conversation_messages(
    conversation_id: str,
    current_user=Depends(get_current_user),
):
    """Retorna mensagens de uma conversa."""
    try:
        from bson import ObjectId
        db = MongoDB.get_database()

        # Verificar permissão
        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Conversa não encontrada"}},
            )

        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_ids = [str(b.id) for b in bots]

        if str(conv.get("bot_id", "")) not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Conversa não pertence a este usuário"}},
            )

        messages = await db.messages.find(
            {"conversation_id": ObjectId(conversation_id)}
        ).sort("created_at", 1).to_list(200)

        return [
            {
                "id": str(m["_id"]),
                "role": m.get("role", "unknown"),
                "content": m.get("content", ""),
                "media_type": m.get("media_type"),
                "created_at": m.get("created_at").isoformat() if m.get("created_at") else None,
            }
            for m in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens da conversa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar mensagens da conversa"}},
        )


@router.put(
    "/conversations/{conversation_id}/assign",
    summary="Atribuir conversa a humano",
    description="Atribui uma conversa a um atendente humano.",
)
async def assign_conversation(
    conversation_id: str,
    body: AssignRequest,
    current_user=Depends(get_current_user),
):
    """Atribui conversa a atendente humano."""
    try:
        from bson import ObjectId
        db = MongoDB.get_database()

        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Conversa não encontrada"}},
            )

        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_ids = [str(b.id) for b in bots]
        if str(conv.get("bot_id", "")) not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Conversa não pertence a este usuário"}},
            )

        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "status": "waiting",
                    "assigned_to": body.user_id,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # Emitir evento WebSocket
        try:
            from src.api.v1.endpoints.websocket import get_ws_manager
            await get_ws_manager().broadcast_to_user(str(current_user.id), {
                "event": "conversation.updated",
                "data": {
                    "conversation_id": conversation_id,
                    "status": "waiting",
                    "assigned_to": body.user_id,
                }
            })
        except Exception:
            pass

        return {"message": "Conversa atribuída com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atribuir conversa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao atribuir conversa"}},
        )


@router.put(
    "/conversations/{conversation_id}/close",
    summary="Fechar conversa",
    description="Fecha uma conversa.",
)
async def close_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
):
    """Fecha uma conversa."""
    try:
        from bson import ObjectId
        db = MongoDB.get_database()

        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Conversa não encontrada"}},
            )

        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_ids = [str(b.id) for b in bots]
        if str(conv.get("bot_id", "")) not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Conversa não pertence a este usuário"}},
            )

        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"status": "closed", "updated_at": datetime.utcnow()}},
        )

        # Emitir evento WebSocket
        try:
            from src.api.v1.endpoints.websocket import get_ws_manager
            await get_ws_manager().broadcast_to_user(str(current_user.id), {
                "event": "conversation.updated",
                "data": {
                    "conversation_id": conversation_id,
                    "status": "closed",
                }
            })
        except Exception:
            pass

        return {"message": "Conversa fechada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fechar conversa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao fechar conversa"}},
        )


@router.put(
    "/conversations/{conversation_id}/reopen",
    summary="Reabrir conversa",
    description="Reabre uma conversa fechada.",
)
async def reopen_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user),
):
    """Reabre uma conversa."""
    try:
        from bson import ObjectId
        db = MongoDB.get_database()

        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Conversa não encontrada"}},
            )

        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_ids = [str(b.id) for b in bots]
        if str(conv.get("bot_id", "")) not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Conversa não pertence a este usuário"}},
            )

        await db.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"status": "active", "updated_at": datetime.utcnow()}},
        )

        # Emitir evento WebSocket
        try:
            from src.api.v1.endpoints.websocket import get_ws_manager
            await get_ws_manager().broadcast_to_user(str(current_user.id), {
                "event": "conversation.updated",
                "data": {
                    "conversation_id": conversation_id,
                    "status": "active",
                }
            })
        except Exception:
            pass

        return {"message": "Conversa reaberta com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reabrir conversa: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao reabrir conversa"}},
        )


@router.put(
    "/conversations/{conversation_id}/messages/{message_id}/read",
    summary="Marcar mensagem como lida",
    description="Marca uma mensagem específica como lida.",
)
async def mark_message_read(
    conversation_id: str,
    message_id: str,
    current_user=Depends(get_current_user),
):
    """Marca mensagem como lida."""
    try:
        from bson import ObjectId
        db = MongoDB.get_database()

        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Conversa não encontrada"}},
            )

        bot_repo = _get_bot_repo()
        bots = await bot_repo.listar_por_usuario(str(current_user.id))
        bot_ids = [str(b.id) for b in bots]
        if str(conv.get("bot_id", "")) not in bot_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "FORBIDDEN", "mensagem": "Conversa não pertence a este usuário"}},
            )

        result = await db.messages.update_one(
            {"_id": ObjectId(message_id), "conversation_id": ObjectId(conversation_id)},
            {"$set": {"read": True}},
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Mensagem não encontrada"}},
            )

        return {"message": "Mensagem marcada como lida"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao marcar mensagem como lida: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao marcar mensagem como lida"}},
        )


# ========================================
# Contatos
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


# ========================================
# Planos
# ========================================

@router.get(
    "/plans",
    summary="Listar planos",
    description="Retorna planos disponíveis com limites e features.",
)
async def list_plans():
    """Lista planos disponíveis."""
    return {
        "plans": [
            {
                "tipo": plan_type,
                **plan_config,
            }
            for plan_type, plan_config in PLANS_CONFIG.items()
        ]
    }


@router.get(
    "/plan/current",
    summary="Plano atual",
    description="Retorna o plano do usuário atual com usage.",
)
async def get_current_plan(
    current_user=Depends(get_current_user),
):
    """Retorna plano atual do usuário."""
    try:
        bot_repo = _get_bot_repo()
        contact_repo = _get_contact_repo()
        usuario_id = str(current_user.id)

        # Buscar usage
        total_bots = await bot_repo.contar_por_usuario(usuario_id)
        total_contacts = await contact_repo.contar_por_usuario(usuario_id)

        plan = current_user.plano
        return {
            "tipo": plan.tipo.value if hasattr(plan.tipo, 'value') else plan.tipo,
            "max_bots": plan.max_bots,
            "max_mensagens_por_mes": plan.max_mensagens_por_mes,
            "max_contatos": plan.max_contatos,
            "features": plan.features,
            "expira_em": plan.expira_em.isoformat() if plan.expira_em else None,
            "trial_termina_em": plan.trial_termina_em.isoformat() if plan.trial_termina_em else None,
            "trial_utilizado": plan.trial_utilizado,
            "usage": {
                "bots": total_bots,
                "contacts": total_contacts,
            },
        }
    except Exception as e:
        logger.error(f"Erro ao buscar plano: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar plano"}},
        )


@router.post(
    "/plan/upgrade",
    summary="Upgrade de plano",
    description="Faz upgrade do plano do usuário.",
)
async def upgrade_plan(
    plan_type: str = Query(..., description="Novo plano (basic ou pro)"),
    current_user=Depends(get_current_user),
):
    """Faz upgrade do plano."""
    try:
        from src.domain.entities.user import TipoPlano
        from src.infrastructure.database.mongodb import MongoDB
        from src.infrastructure.repositories.user_repository_impl import MongoUserRepository

        if plan_type not in PLANS_CONFIG:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"erro": {"codigo": "INVALID_PLAN", "mensagem": f"Plano inválido. Planos disponíveis: {', '.join(PLANS_CONFIG.keys())}"}},
            )

        novo_tipo = TipoPlano(plan_type)

        # Não permitir downgrade
        atual = current_user.plano.tipo
        if hasattr(atual, 'value'):
            atual = atual.value
        planos_ordem = {"free": 0, "basic": 1, "pro": 2}
        if planos_ordem.get(plan_type, 0) <= planos_ordem.get(atual, 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"erro": {"codigo": "INVALID_UPGRADE", "mensagem": "Só é possível fazer upgrade de plano."}},
            )

        repo = MongoUserRepository(MongoDB.get_database())
        updated = await repo.atualizar_plano(str(current_user.id), novo_tipo)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao atualizar plano"}},
            )

        return {
            "message": f"Plano atualizado para {plan_type} com sucesso!",
            "plan": {
                "tipo": updated.plano.tipo.value if hasattr(updated.plano.tipo, 'value') else updated.plano.tipo,
                "max_bots": updated.plano.max_bots,
                "features": updated.plano.features,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer upgrade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao atualizar plano"}},
        )

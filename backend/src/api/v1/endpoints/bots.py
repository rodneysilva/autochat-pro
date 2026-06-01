"""
Endpoints de gerenciamento de bots.

CRUD de bots com pausa/retomada e verificação de status.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from src.domain.entities.bot import StatusBot
from src.infrastructure.external_services.whatsapp import get_whatsapp_service, EvolutionWhatsAppService
from src.api.middleware.auth import get_current_user
from src.application.use_cases.create_bot_use_case import CreateBotUseCase
from src.application.use_cases.list_bots_use_case import ListBotsUseCase
from src.application.use_cases.get_bot_use_case import GetBotUseCase
from src.application.use_cases.update_bot_use_case import UpdateBotUseCase
from src.application.use_cases.delete_bot_use_case import DeleteBotUseCase
from src.application.dto.bot_dto import CriarBotRequest, AtualizarBotRequest
from src.shared.exceptions import BaseAppException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/bots", tags=["Bots"])


# ========================================
# Dependencies
# ========================================

def _get_bot_repo():
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository
    from src.domain.repositories.bot_repository import BotRepository
    db = MongoDB.get_database()
    return MongoBotRepository(db)


async def get_create_bot_uc() -> CreateBotUseCase:
    return CreateBotUseCase(_get_bot_repo())


async def get_list_bots_uc() -> ListBotsUseCase:
    return ListBotsUseCase(_get_bot_repo())


async def get_get_bot_uc() -> GetBotUseCase:
    return GetBotUseCase(_get_bot_repo())


async def get_update_bot_uc() -> UpdateBotUseCase:
    return UpdateBotUseCase(_get_bot_repo())


async def get_delete_bot_uc() -> DeleteBotUseCase:
    return DeleteBotUseCase(_get_bot_repo())


# ========================================
# Endpoints
# ========================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Criar bot",
    description="Cria um novo bot vinculado ao usuário atual.",
)
async def create_bot(
    request: CriarBotRequest,
    uc: CreateBotUseCase = Depends(get_create_bot_uc),
    current_user=Depends(get_current_user),
):
    """Cria um novo bot."""
    try:
        return await uc.execute(request, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao criar bot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao criar bot"}},
        )


@router.get(
    "",
    summary="Listar bots",
    description="Lista todos os bots do usuário atual.",
)
async def list_bots(
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100),
    uc: ListBotsUseCase = Depends(get_list_bots_uc),
    current_user=Depends(get_current_user),
):
    """Lista bots do usuário."""
    try:
        return await uc.execute(str(current_user.id), pagina, tamanho_pagina)
    except Exception as e:
        logger.error(f"Erro ao listar bots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao listar bots"}},
        )


@router.get(
    "/{bot_id}",
    summary="Buscar bot",
    description="Busca um bot específico por ID.",
)
async def get_bot(
    bot_id: str,
    uc: GetBotUseCase = Depends(get_get_bot_uc),
    current_user=Depends(get_current_user),
):
    """Busca um bot por ID."""
    try:
        return await uc.execute(bot_id, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao buscar bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar bot"}},
        )


@router.put(
    "/{bot_id}",
    summary="Atualizar bot",
    description="Atualiza configuração de um bot.",
)
async def update_bot(
    bot_id: str,
    request: AtualizarBotRequest,
    uc: UpdateBotUseCase = Depends(get_update_bot_uc),
    current_user=Depends(get_current_user),
):
    """Atualiza configuração do bot."""
    try:
        return await uc.execute(bot_id, request, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao atualizar bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao atualizar bot"}},
        )


@router.delete(
    "/{bot_id}",
    summary="Deletar bot",
    description="Remove um bot e sua instância WhatsApp.",
)
async def delete_bot(
    bot_id: str,
    uc: DeleteBotUseCase = Depends(get_delete_bot_uc),
    current_user=Depends(get_current_user),
):
    """Deleta um bot."""
    try:
        return await uc.execute(bot_id, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao deletar bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao deletar bot"}},
        )


@router.post(
    "/{bot_id}/pause",
    summary="Pausar bot",
    description="Pausa o bot, interrompendo respostas automáticas.",
)
async def pause_bot(
    bot_id: str,
    current_user=Depends(get_current_user),
):
    """Pausa um bot."""
    try:
        from src.infrastructure.database.mongodb import MongoDB
        from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository

        repo = MongoBotRepository(MongoDB.get_database())
        bot = await repo.buscar_por_id(bot_id)
        if not bot or str(bot.usuario_id) != str(current_user.id):
            raise HTTPException(status_code=404, detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Bot não encontrado"}})

        bot.pausar()
        updated = await repo.salvar(bot)
        from src.application.dto.bot_dto import bot_to_response
        return bot_to_response(updated)
    except BaseAppException as e:
        raise e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao pausar bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao pausar bot"}},
        )


@router.post(
    "/{bot_id}/resume",
    summary="Retomar bot",
    description="Retoma o bot, voltando a responder automaticamente.",
)
async def resume_bot(
    bot_id: str,
    current_user=Depends(get_current_user),
):
    """Retoma um bot pausado."""
    try:
        from src.infrastructure.database.mongodb import MongoDB
        from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository

        repo = MongoBotRepository(MongoDB.get_database())
        bot = await repo.buscar_por_id(bot_id)
        if not bot or str(bot.usuario_id) != str(current_user.id):
            raise HTTPException(status_code=404, detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Bot não encontrado"}})

        bot.retomar()
        updated = await repo.salvar(bot)
        from src.application.dto.bot_dto import bot_to_response
        return bot_to_response(updated)
    except BaseAppException as e:
        raise e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao retomar bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao retomar bot"}},
        )

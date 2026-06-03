"""
Endpoints de webhook e configuração do Telegram.

Recebe updates do Telegram via webhook e processa mensagens.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Optional
from pydantic import BaseModel, Field

from src.api.middleware.auth import get_current_user
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/telegram", tags=["Telegram"])


# ========================================
# Request DTOs
# ========================================

class SetupWebhookRequest(BaseModel):
    bot_id: str = Field(..., description="ID do bot Telegram")


class ValidateTokenRequest(BaseModel):
    bot_token: str = Field(..., description="Token do bot Telegram do @BotFather")


# ========================================
# Helpers
# ========================================

def _get_bot_repo():
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.bot_repository_impl import MongoBotRepository
    return MongoBotRepository(MongoDB.get_database())


async def _find_bot_by_token(bot_token: str):
    """Busca um bot pelo telegram_config.bot_token."""
    from src.infrastructure.database.mongodb import MongoDB
    db = MongoDB.get_database()
    doc = await db.bots.find_one({"telegram_config.bot_token": bot_token})
    return doc


# ========================================
# Webhook Endpoint (SEM auth - chamado pelo Telegram)
# ========================================

@router.post(
    "/webhook/{bot_token}",
    summary="Webhook do Telegram",
    description="Recebe updates do Telegram. Não requer autenticação.",
)
async def telegram_webhook(bot_token: str, request: Request):
    """
    Recebe updates do Telegram e processa mensagens.

    O Telegram envia updates para esta URL quando o webhook está configurado.
    """
    try:
        update = await request.json()
    except Exception:
        return {"ok": True}

    # Validação rápida: tem message?
    message = update.get("message") or update.get("edited_message")
    if not message:
        return {"ok": True}

    # Busca bot pelo token
    doc = await _find_bot_by_token(bot_token)
    if not doc:
        logger.warning(f"Webhook Telegram: bot não encontrado para token=...{bot_token[-6:]}")
        return {"ok": True}

    # Verifica se o bot está ativo
    bot_status = doc.get("status", "")
    if bot_status != "active":
        logger.info(f"Webhook Telegram: bot inativo (status={bot_status}), ignorando")
        return {"ok": True}

    # Processa a mensagem
    try:
        from src.application.services.message_processor import get_message_processor
        processor = get_message_processor()
        if processor:
            await processor.process_telegram_message(bot_token, update)
    except Exception as e:
        logger.error(f"Erro ao processar mensagem Telegram: {e}", exc_info=True)

    return {"ok": True}


# ========================================
# Setup/Config Endpoints (COM auth)
# ========================================

@router.post(
    "/setup-webhook",
    summary="Configurar webhook do Telegram",
    description="Registra o webhook no Telegram para um bot específico.",
)
async def setup_telegram_webhook(
    request_body: SetupWebhookRequest,
    current_user=Depends(get_current_user),
):
    """Configura webhook do Telegram para um bot."""
    from src.infrastructure.external_services.telegram import get_telegram_service

    repo = _get_bot_repo()
    bot = await repo.buscar_por_id(request_body.bot_id)

    if not bot or str(bot.usuario_id) != str(current_user.id):
        raise HTTPException(
            status_code=404,
            detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Bot não encontrado"}},
        )

    if not bot.telegram_config.bot_token:
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "INVALID_CONFIG", "mensagem": "Bot sem token do Telegram configurado"}},
        )

    telegram_svc = get_telegram_service()
    try:
        result = await telegram_svc.set_webhook(bot.telegram_config.bot_token)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "TELEGRAM_ERROR", "mensagem": str(e)}},
        )

    # Atualiza webhook_url no bot
    webhook_url = telegram_svc.build_webhook_url(bot.telegram_config.bot_token)
    bot.telegram_config.webhook_url = webhook_url
    bot.status = bot.status  # mantém status
    if bot.status.value == "disconnected":
        bot.marcar_como_conectado()
    await repo.salvar(bot)

    return {"ok": True, "webhook_url": webhook_url, "telegram_response": result}


@router.delete(
    "/webhook",
    summary="Remover webhook do Telegram",
    description="Remove o webhook do Telegram para um bot específico.",
)
async def delete_telegram_webhook(
    bot_id: str,
    current_user=Depends(get_current_user),
):
    """Remove webhook do Telegram para um bot."""
    from src.infrastructure.external_services.telegram import get_telegram_service

    repo = _get_bot_repo()
    bot = await repo.buscar_por_id(bot_id)

    if not bot or str(bot.usuario_id) != str(current_user.id):
        raise HTTPException(
            status_code=404,
            detail={"erro": {"codigo": "NOT_FOUND", "mensagem": "Bot não encontrado"}},
        )

    if not bot.telegram_config.bot_token:
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "INVALID_CONFIG", "mensagem": "Bot sem token do Telegram"}},
        )

    telegram_svc = get_telegram_service()
    try:
        await telegram_svc.delete_webhook(bot.telegram_config.bot_token)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "TELEGRAM_ERROR", "mensagem": str(e)}},
        )

    bot.telegram_config.webhook_url = None
    bot.desconectar("Webhook removido")
    await repo.salvar(bot)

    return {"ok": True}


@router.post(
    "/validate-token",
    summary="Validar token do Telegram",
    description="Valida um token do Telegram e retorna info do bot.",
)
async def validate_telegram_token(
    request_body: ValidateTokenRequest,
    current_user=Depends(get_current_user),
):
    """Valida um token do Telegram via getMe."""
    from src.infrastructure.external_services.telegram import get_telegram_service

    telegram_svc = get_telegram_service()
    try:
        bot_info = await telegram_svc.get_me(request_body.bot_token)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"erro": {"codigo": "INVALID_TOKEN", "mensagem": str(e)}},
        )

    return {
        "ok": True,
        "bot_info": {
            "id": bot_info.get("id"),
            "is_bot": bot_info.get("is_bot"),
            "first_name": bot_info.get("first_name"),
            "username": bot_info.get("username"),
        },
    }

"""
Serviço de integração com Telegram API.

Utiliza python-telegram-bot v20 (async) para interagir com a API do Telegram:
- Registro/remoção de webhooks
- Envio de mensagens
- Validação de tokens
"""

import httpx
from typing import Optional, Dict, Any

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


class TelegramService:
    """Serviço de integração com a API do Telegram."""

    def build_webhook_url(self, bot_token: str) -> str:
        """
        Constrói a URL do webhook para o Telegram.

        Args:
            bot_token: Token do bot Telegram.

        Returns:
            URL completa do webhook.
        """
        base_url = getattr(settings, "TELEGRAM_WEBHOOK_BASE_URL", "").rstrip("/")
        if not base_url:
            base_url = f"http://localhost:{settings.PORT}"
        return f"{base_url}/api/v1/telegram/webhook/{bot_token}"

    async def set_webhook(
        self,
        bot_token: str,
        webhook_url: Optional[str] = None,
        allowed_updates: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Registra um webhook no Telegram.

        Args:
            bot_token: Token do bot Telegram.
            webhook_url: URL do webhook. Se None, constrói automaticamente.
            allowed_updates: Lista de updates permitidos.

        Returns:
            Resposta da API do Telegram.

        Raises:
            Exception: Se o registro falhar.
        """
        if webhook_url is None:
            webhook_url = self.build_webhook_url(bot_token)

        if allowed_updates is None:
            allowed_updates = ["message", "edited_message"]

        url = f"{TELEGRAM_API_BASE}{bot_token}/setWebhook"
        payload = {
            "url": webhook_url,
            "allowed_updates": allowed_updates,
            "drop_pending_updates": True,
        }

        logger.info(f"Registrando webhook Telegram: {webhook_url}")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            data = response.json()

            if not data.get("ok"):
                error_msg = data.get("description", "Erro desconhecido")
                logger.error(f"Erro ao registrar webhook Telegram: {error_msg}")
                raise Exception(f"Telegram API error: {error_msg}")

            logger.info(f"Webhook Telegram registrado com sucesso para bot_token=...{bot_token[-6:]}")
            return data

    async def delete_webhook(self, bot_token: str) -> Dict[str, Any]:
        """
        Remove o webhook do Telegram.

        Args:
            bot_token: Token do bot Telegram.

        Returns:
            Resposta da API do Telegram.
        """
        url = f"{TELEGRAM_API_BASE}{bot_token}/deleteWebhook"
        payload = {"drop_pending_updates": True}

        logger.info(f"Removendo webhook Telegram para bot_token=...{bot_token[-6:]}")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            data = response.json()

            if not data.get("ok"):
                error_msg = data.get("description", "Erro desconhecido")
                logger.error(f"Erro ao remover webhook Telegram: {error_msg}")
                raise Exception(f"Telegram API error: {error_msg}")

            logger.info("Webhook Telegram removido com sucesso")
            return data

    async def send_message(
        self,
        bot_token: str,
        chat_id: str,
        text: str,
        parse_mode: str = "Markdown",
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem via Telegram.

        Args:
            bot_token: Token do bot Telegram.
            chat_id: ID do chat (ou telefone).
            text: Texto da mensagem.
            parse_mode: Modo de parse (HTML, Markdown).

        Returns:
            Resposta da API do Telegram.

        Raises:
            Exception: Se o envio falhar.
        """
        url = f"{TELEGRAM_API_BASE}{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        logger.info(f"Enviando mensagem Telegram para chat_id={chat_id}")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            data = response.json()

            if not data.get("ok"):
                error_msg = data.get("description", "Erro desconhecido")
                logger.error(f"Erro ao enviar mensagem Telegram: {error_msg}")
                raise Exception(f"Telegram API error: {error_msg}")

            logger.info(f"Mensagem Telegram enviada para chat_id={chat_id}")
            return data

    async def get_me(self, bot_token: str) -> Dict[str, Any]:
        """
        Obtém informações do bot (username, nome, etc.).

        Args:
            bot_token: Token do bot Telegram.

        Returns:
            Dados do bot da API do Telegram.

        Raises:
            Exception: Se a chamada falhar.
        """
        url = f"{TELEGRAM_API_BASE}{bot_token}/getMe"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            data = response.json()

            if not data.get("ok"):
                error_msg = data.get("description", "Erro desconhecido")
                logger.error(f"Erro ao validar token Telegram: {error_msg}")
                raise Exception(f"Token inválido: {error_msg}")

            logger.info(f"Bot Telegram validado: @{data['result']['username']}")
            return data.get("result", {})

"""
Serviço de integração com Telegram.

"""

from src.infrastructure.external_services.telegram.telegram_service import TelegramService

_telegram_service: TelegramService | None = None


def get_telegram_service() -> TelegramService:
    """Retorna instância singleton do TelegramService."""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service


__all__ = ["TelegramService", "get_telegram_service"]

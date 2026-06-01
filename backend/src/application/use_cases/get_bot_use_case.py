"""
Caso de uso para buscar um bot.
"""

from uuid import UUID

from src.domain.repositories.bot_repository import BotRepository
from src.application.dto.bot_dto import BotResponse, bot_to_response
from src.shared.exceptions import EntityNotFoundException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class GetBotUseCase:
    """Caso de uso para buscar um bot por ID."""

    def __init__(self, bot_repository: BotRepository):
        self._repository = bot_repository

    async def execute(self, bot_id: str, usuario_id: str) -> BotResponse:
        """Busca um bot e verifica pertencimento ao usuário."""
        bot = await self._repository.buscar_por_id(bot_id)

        if not bot:
            raise EntityNotFoundException("Bot", bot_id)

        # Verificar se o bot pertence ao usuário
        if str(bot.usuario_id) != usuario_id:
            raise EntityNotFoundException("Bot", bot_id)

        return bot_to_response(bot)

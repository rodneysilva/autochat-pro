"""
Caso de uso para deletar um bot.
"""

from uuid import UUID

from src.domain.repositories.bot_repository import BotRepository
from src.shared.exceptions import EntityNotFoundException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class DeleteBotUseCase:
    """Caso de uso para deletar um bot."""

    def __init__(self, bot_repository: BotRepository):
        self._repository = bot_repository

    async def execute(self, bot_id: str, usuario_id: str) -> dict:
        """Deleta um bot e sua instância na Evolution API."""
        bot = await self._repository.buscar_por_id(bot_id)

        if not bot:
            raise EntityNotFoundException("Bot", bot_id)

        if str(bot.usuario_id) != usuario_id:
            raise EntityNotFoundException("Bot", bot_id)

        # Deletar do MongoDB
        await self._repository.deletar(bot_id)

        # Tentar deletar instância da Evolution API
        try:
            from src.infrastructure.external_services.whatsapp import get_whatsapp_service
            whatsapp = get_whatsapp_service()
            await whatsapp.delete_instance(bot.nome)
        except Exception as e:
            logger.warning(f"Erro ao deletar instância Evolution API: {e}")

        logger.info(f"Bot deletado: {bot.nome} ({bot_id})")

        return {"message": f"Bot '{bot.nome}' removido com sucesso"}

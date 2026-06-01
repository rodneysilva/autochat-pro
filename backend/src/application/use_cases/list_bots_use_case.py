"""
Caso de uso para listagem de bots.
"""

from math import ceil


from src.domain.repositories.bot_repository import BotRepository
from src.application.dto.bot_dto import ListaBotsResponse, bot_to_response
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ListBotsUseCase:
    """Caso de uso para listagem de bots."""

    def __init__(self, bot_repository: BotRepository):
        self._repository = bot_repository

    async def execute(
        self,
        usuario_id: str,
        pagina: int = 1,
        tamanho_pagina: int = 20,
    ) -> ListaBotsResponse:
        """Lista bots do usuário com paginação."""
        pulo = (pagina - 1) * tamanho_pagina

        bots = await self._repository.listar_por_usuario(
            usuario_id,
            limite=tamanho_pagina,
            pulo=pulo,
        )
        total = await self._repository.contar_por_usuario(usuario_id)

        logger.info(f"Listando {len(bots)} bots do usuário {usuario_id} (página {pagina})")

        return ListaBotsResponse(
            data=[bot_to_response(bot) for bot in bots],
            total=total,
            pagina=pagina,
            tamanho_pagina=tamanho_pagina,
        )

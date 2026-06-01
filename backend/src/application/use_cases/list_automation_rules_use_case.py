"""
Caso de uso para listagem de regras de automação.
"""

from src.domain.repositories.automation_rule_repository import AutomationRuleRepository
from src.application.dto.automation_rule_dto import regra_to_response, ListaRegrasResponse
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ListAutomationRulesUseCase:
    """Caso de uso para listagem de regras de automação."""

    def __init__(self, repository: AutomationRuleRepository):
        self._repo = repository

    async def execute(self, bot_id: str, pagina: int = 1, tamanho_pagina: int = 20):
        """Lista regras de automação de um bot."""
        from uuid import UUID
        bot_uuid = UUID(bot_id)

        pulo = (pagina - 1) * tamanho_pagina
        rules = await self._repo.listar_por_bot(bot_uuid, limite=tamanho_pagina, pulo=pulo)
        total = await self._repo.contar_por_bot(bot_uuid)

        return ListaRegrasResponse(
            data=[regra_to_response(r) for r in rules],
            total=total,
        )

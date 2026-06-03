"""
Caso de uso para ativar/desativar regra de automação.
"""

from src.domain.repositories.automation_rule_repository import AutomationRuleRepository
from src.application.dto.automation_rule_dto import regra_to_response
from src.shared.exceptions import EntityNotFoundException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ToggleAutomationRuleUseCase:
    """Caso de uso para toggle de ativação de regras."""

    def __init__(self, repository: AutomationRuleRepository):
        self._repo = repository

    async def execute(self, rule_id: str, usuario_id: str):
        """Ativa ou desativa uma regra."""
        rule = await self._repo.buscar_por_id(rule_id)
        if not rule:
            raise EntityNotFoundException("Regra não encontrada", code="RULE_NOT_FOUND")

        new_status = not rule.ativado
        updated = await self._repo.atualizar_status_ativacao(rule_id, new_status)

        logger.info(f"Regra '{rule.nome}' {'ativada' if new_status else 'desativada'}")
        return regra_to_response(updated)

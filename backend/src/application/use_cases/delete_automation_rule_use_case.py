"""
Caso de uso para deleção de regra de automação.
"""

from src.domain.repositories.automation_rule_repository import AutomationRuleRepository
from src.shared.exceptions import EntityNotFoundException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class DeleteAutomationRuleUseCase:
    """Caso de uso para deleção de regras de automação."""

    def __init__(self, repository: AutomationRuleRepository):
        self._repo = repository

    async def execute(self, rule_id: str, usuario_id: str):
        """Deleta uma regra de automação."""
        rule = await self._repo.buscar_por_id(rule_id)
        if not rule:
            raise EntityNotFoundException("Regra não encontrada", code="RULE_NOT_FOUND")

        await self._repo.deletar(rule_id)
        logger.info(f"Regra de automação deletada: {rule.nome} ({rule_id})")
        return {"mensagem": f"Regra '{rule.nome}' deletada com sucesso"}

"""
Caso de uso para atualização de regra de automação.
"""

from uuid import UUID

from src.domain.entities.automation_rule import (
    Condicao, Acao,
    TipoCondicao, OperadorCondicao, TipoAcao,
)
from src.domain.repositories.automation_rule_repository import AutomationRuleRepository
from src.application.dto.automation_rule_dto import AtualizarRegraRequest, regra_to_response
from src.shared.exceptions import EntityNotFoundException, ValidationException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class UpdateAutomationRuleUseCase:
    """Caso de uso para atualização de regras de automação."""

    def __init__(self, repository: AutomationRuleRepository):
        self._repo = repository

    async def execute(self, rule_id: str, request: AtualizarRegraRequest, usuario_id: str):
        """Atualiza uma regra de automação."""
        rule = await self._repo.buscar_por_id(UUID(rule_id))
        if not rule:
            raise EntityNotFoundException("Regra não encontrada", code="RULE_NOT_FOUND")

        # Atualizar campos
        if request.nome is not None:
            rule.nome = request.nome
        if request.descricao is not None:
            rule.descricao = request.descricao
        if request.prioridade is not None:
            rule.prioridade = request.prioridade
        if request.cooldown_seconds is not None:
            rule.cooldown = request.cooldown_seconds
        if request.ativa is not None:
            rule.ativado = request.ativa
            if request.ativa:
                rule.ativar()
            else:
                rule.desativar()

        if request.condicoes is not None:
            condicoes = []
            for c in request.condicoes:
                try:
                    condicoes.append(Condicao(
                        tipo=TipoCondicao(c.tipo),
                        campo=c.campo,
                        operador=OperadorCondicao(c.operador),
                        valor=c.valor,
                        negar=c.negar,
                    ))
                except ValueError:
                    raise ValidationException(f"Tipo de condição inválido: {c.tipo}")
            rule.condicoes = condicoes

        if request.acoes is not None:
            acoes = []
            for a in request.acoes:
                try:
                    acoes.append(Acao(
                        tipo=TipoAcao(a.tipo),
                        delay=a.delay,
                        conteudo=a.conteudo,
                        parametros=a.parametros,
                    ))
                except ValueError:
                    raise ValidationException(f"Tipo de ação inválido: {a.tipo}")
            rule.acoes = acoes

        if not rule.condicoes:
            raise ValidationException("A regra deve ter pelo menos uma condição")
        if not rule.acoes:
            raise ValidationException("A regra deve ter pelo menos uma ação")

        updated = await self._repo.salvar(rule)
        logger.info(f"Regra de automação atualizada: {updated.nome}")
        return regra_to_response(updated)

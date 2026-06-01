"""
Caso de uso para criação de regra de automação.
"""

from uuid import UUID

from src.domain.entities.automation_rule import (
    RegraAutomacao, Condicao, Acao,
    TipoCondicao, OperadorCondicao, TipoAcao,
)
from src.domain.repositories.automation_rule_repository import AutomationRuleRepository
from src.application.dto.automation_rule_dto import CriarRegraRequest, regra_to_response
from src.shared.exceptions import ValidationException, EntityAlreadyExistsException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class CreateAutomationRuleUseCase:
    """Caso de uso para criação de regras de automação."""

    def __init__(self, repository: AutomationRuleRepository):
        self._repo = repository

    async def execute(self, request: CriarRegraRequest, usuario_id: str):
        """Cria uma nova regra de automação."""
        bot_id = UUID(request.bot_id)

        # Verificar se já existe regra com mesmo nome no bot
        existing = await self._repo.buscar_por_nome(bot_id, request.nome)
        if existing:
            raise EntityAlreadyExistsException(
                f"Já existe uma regra com o nome '{request.nome}' neste bot",
                code="RULE_NAME_EXISTS",
            )

        # Converter condicoes
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

        # Converter acoes
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

        if not condicoes:
            raise ValidationException("A regra deve ter pelo menos uma condição")
        if not acoes:
            raise ValidationException("A regra deve ter pelo menos uma ação")

        # Criar entidade
        rule = RegraAutomacao(
            bot_id=bot_id,
            nome=request.nome,
            descricao=request.descricao or "",
            ativado=request.ativa,
            prioridade=request.prioridade,
            condicoes=condicoes,
            acoes=acoes,
            cooldown=request.cooldown_seconds,
        )

        created = await self._repo.salvar(rule)
        logger.info(f"Regra de automação criada: {created.nome} ({created.id})")
        return regra_to_response(created)

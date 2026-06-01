"""
Endpoints de gerenciamento de automações.

CRUD de regras de automação para respostas automáticas.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.middleware.auth import get_current_user
from src.application.dto.automation_rule_dto import (
    CriarRegraRequest, AtualizarRegraRequest, regra_to_response,
)
from src.application.use_cases.create_automation_rule_use_case import CreateAutomationRuleUseCase
from src.application.use_cases.list_automation_rules_use_case import ListAutomationRulesUseCase
from src.application.use_cases.update_automation_rule_use_case import UpdateAutomationRuleUseCase
from src.application.use_cases.delete_automation_rule_use_case import DeleteAutomationRuleUseCase
from src.application.use_cases.toggle_automation_rule_use_case import ToggleAutomationRuleUseCase
from src.shared.exceptions import BaseAppException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/automations", tags=["Automações"])


def _get_repo():
    from src.infrastructure.database.mongodb import MongoDB
    from src.infrastructure.repositories.automation_rule_repository_impl import MongoAutomationRuleRepository
    db = MongoDB.get_database()
    return MongoAutomationRuleRepository(db)


async def _get_create_uc() -> CreateAutomationRuleUseCase:
    return CreateAutomationRuleUseCase(_get_repo())


async def _get_list_uc() -> ListAutomationRulesUseCase:
    return ListAutomationRulesUseCase(_get_repo())


async def _get_update_uc() -> UpdateAutomationRuleUseCase:
    return UpdateAutomationRuleUseCase(_get_repo())


async def _get_delete_uc() -> DeleteAutomationRuleUseCase:
    return DeleteAutomationRuleUseCase(_get_repo())


async def _get_toggle_uc() -> ToggleAutomationRuleUseCase:
    return ToggleAutomationRuleUseCase(_get_repo())


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Criar regra de automação",
    description="Cria uma nova regra de automação para um bot.",
)
async def create_rule(
    request: CriarRegraRequest,
    uc: CreateAutomationRuleUseCase = Depends(_get_create_uc),
    current_user=Depends(get_current_user),
):
    """Cria uma nova regra de automação."""
    try:
        return await uc.execute(request, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao criar regra: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao criar regra"}},
        )


@router.get(
    "",
    summary="Listar regras de automação",
    description="Lista todas as regras de automação de um bot.",
)
async def list_rules(
    bot_id: str = Query(..., description="ID do bot"),
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(20, ge=1, le=100),
    uc: ListAutomationRulesUseCase = Depends(_get_list_uc),
    current_user=Depends(get_current_user),
):
    """Lista regras de automação de um bot."""
    try:
        return await uc.execute(bot_id, pagina, tamanho_pagina)
    except Exception as e:
        logger.error(f"Erro ao listar regras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao listar regras"}},
        )


@router.get(
    "/{rule_id}",
    summary="Buscar regra de automação",
    description="Busca uma regra específica por ID.",
)
async def get_rule(
    rule_id: str,
    current_user=Depends(get_current_user),
):
    """Busca uma regra por ID."""
    try:
        repo = _get_repo()
        from uuid import UUID
        rule = await repo.buscar_por_id(UUID(rule_id))
        if not rule:
            raise HTTPException(
                status_code=404,
                detail={"erro": {"codigo": "RULE_NOT_FOUND", "mensagem": "Regra não encontrada"}},
            )
        return regra_to_response(rule)
    except BaseAppException as e:
        raise e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar regra: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao buscar regra"}},
        )


@router.put(
    "/{rule_id}",
    summary="Atualizar regra de automação",
    description="Atualiza uma regra de automação existente.",
)
async def update_rule(
    rule_id: str,
    request: AtualizarRegraRequest,
    uc: UpdateAutomationRuleUseCase = Depends(_get_update_uc),
    current_user=Depends(get_current_user),
):
    """Atualiza uma regra de automação."""
    try:
        return await uc.execute(rule_id, request, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao atualizar regra: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao atualizar regra"}},
        )


@router.delete(
    "/{rule_id}",
    summary="Deletar regra de automação",
    description="Remove uma regra de automação.",
)
async def delete_rule(
    rule_id: str,
    uc: DeleteAutomationRuleUseCase = Depends(_get_delete_uc),
    current_user=Depends(get_current_user),
):
    """Deleta uma regra de automação."""
    try:
        return await uc.execute(rule_id, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao deletar regra: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao deletar regra"}},
        )


@router.post(
    "/{rule_id}/toggle",
    summary="Ativar/desativar regra",
    description="Alterna o status de ativação de uma regra.",
)
async def toggle_rule(
    rule_id: str,
    uc: ToggleAutomationRuleUseCase = Depends(_get_toggle_uc),
    current_user=Depends(get_current_user),
):
    """Ativa ou desativa uma regra."""
    try:
        return await uc.execute(rule_id, str(current_user.id))
    except BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao toggle regra: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"erro": {"codigo": "INTERNAL_ERROR", "mensagem": "Erro ao alterar status da regra"}},
        )

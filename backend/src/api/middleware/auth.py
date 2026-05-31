"""
Middleware de autenticação JWT.

Fornece funções e dependências para proteger rotas e
validar tokens JWT em requisições.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.application.services.jwt_service import JWTService
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.mongodb import MongoDB
from src.infrastructure.repositories.user_repository_impl import MongoUserRepository
from src.shared.exceptions import TokenExpiredException, InvalidTokenException, UnauthorizedError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer(auto_error=False)


async def get_user_repository() -> UserRepository:
    """Obtém instância do repositório de usuários."""
    database = MongoDB.get_database()
    return MongoUserRepository(database)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    repository: UserRepository = Depends(get_user_repository),
) -> Optional[User]:
    """
    Obtém o usuário atual sem exigir autenticação.

    Returns:
        Usuário autenticado ou None.
    """
    if not credentials:
        return None

    try:
        user = await get_current_user(
            credentials=HTTPAuthorizationCredentials(
                scheme="bearer",
                credentials=credentials.credentials
            ),
            repository=repository
        )
        return user
    except HTTPException:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Obtém o usuário atual a partir do token JWT.

    Esta dependência protege a rota, exigindo um token válido.

    Args:
        credentials: Credenciais HTTP Authorization.
        repository: Repositório de usuários.

    Returns:
        Usuário autenticado.

    Raises:
        HTTPException: Se o token for inválido ou o usuário não existir.
    """
    if not credentials:
        logger.warning("Tentativa de acesso sem token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"erro": {"codigo": "NO_TOKEN", "mensagem": "Token de autenticação não fornecido"}}
        )

    token = credentials.credentials

    try:
        # Decodificar token
        payload = JWTService.decode_token(token)

        # Verificar tipo
        if payload.get("type") != "access":
            logger.warning("Token não é do tipo access")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"erro": {"codigo": "INVALID_TOKEN_TYPE", "mensagem": "Tipo de token inválido"}}
            )

        # Obter ID do usuário
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token sem subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"erro": {"codigo": "INVALID_TOKEN", "mensagem": "Token inválido"}}
            )

        # Buscar usuário
        user = await repository.find_by_id(user_id)
        if not user:
            logger.warning(f"Usuário não encontrado: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"erro": {"codigo": "USER_NOT_FOUND", "mensagem": "Usuário não encontrado"}}
            )

        # Verificar se a conta está ativa
        if user.status != "active":
            logger.warning(f"Conta não ativa: {user.email} - {user.status}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "ACCOUNT_INACTIVE", "mensagem": "Esta conta não está ativa"}}
            )

        logger.debug(f"Usuário autenticado: {user.email}")
        return user

    except (TokenExpiredException, InvalidTokenException) as e:
        logger.warning(f"Token inválido: {e.code}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"erro": {"codigo": e.code, "mensagem": e.message}}
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Obtém o usuário atual, verificando se está ativo.

    Args:
        current_user: Usuário autenticado.

    Returns:
        Usuário ativo.

    Raises:
        HTTPException: Se o usuário não estiver ativo.
    """
    if current_user.status != "active":
        logger.warning(f"Conta não ativa: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"erro": {"codigo": "ACCOUNT_INACTIVE", "mensagem": "Esta conta não está ativa"}}
        )

    return current_user


async def require_email_confirmed(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Exige que o email do usuário esteja confirmado.

    Args:
        current_user: Usuário autenticado.

    Returns:
        Usuário com email confirmado.

    Raises:
        HTTPException: Se o email não estiver confirmado.
    """
    if not current_user.email_confirmed:
        logger.warning(f"Email não confirmado: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"erro": {"codigo": "EMAIL_NOT_CONFIRMED", "mensagem": "Email não confirmado"}}
        )

    return current_user


def require_plan(plan_type: str):
    """
    Factory para criar dependência que exige um plano específico.

    Args:
        plan_type: Tipo de plano exigido.

    Returns:
        Dependência FastAPI.
    """
    async def check_plan(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.plan.type != plan_type:
            logger.warning(f"Plano insuficiente: {current_user.email} tem {current_user.plan.type}, precisa de {plan_type}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "INSUFFICIENT_PLAN", "mensagem": f"Requer plano {plan_type}"}}
            )
        return current_user

    return check_plan


def require_min_plan(min_plan: str):
    """
    Factory para criar dependência que exige no mínimo um plano.

    Hierarquia: free < basic < pro

    Args:
        min_plan: Plano mínimo exigido.

    Returns:
        Dependência FastAPI.
    """
    plan_hierarchy = {"free": 0, "basic": 1, "pro": 2}

    async def check_plan(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_level = plan_hierarchy.get(current_user.plan.type, 0)
        required_level = plan_hierarchy.get(min_plan, 0)

        if user_level < required_level:
            logger.warning(f"Plano insuficiente: {current_user.email} tem {current_user.plan.type}, mínimo {min_plan}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"erro": {"codigo": "INSUFFICIENT_PLAN", "mensagem": f"Requer plano no mínimo {min_plan}"}}
            )
        return current_user

    return check_plan

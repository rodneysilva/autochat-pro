"""
Caso de uso de login de usuário.

Implementa a lógica de negócio para autenticação de usuários,
incluindo verificação de credenciais e geração de tokens.
"""

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.application.dto.auth_dto import LoginRequest, LoginResponse, UserResponse
from src.application.services.password_service import PasswordService
from src.application.services.jwt_service import JWTService
from src.shared.exceptions import ValidationError, UnauthorizedError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class LoginUseCase:
    """Caso de uso para login de usuários."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários.
        """
        self._repository = user_repository

    async def execute(self, request: LoginRequest) -> LoginResponse:
        """
        Executa o login de um usuário.

        Args:
            request: Dados do login.

        Returns:
            Resposta com tokens e dados do usuário.

        Raises:
            ValidationError: Se os dados forem inválidos.
            UnauthorizedError: Se as credenciais estiverem incorretas.
        """
        logger.info(f"Tentativa de login: {request.email}")

        # Buscar usuário por email
        user = await self._repository.find_by_email(request.email)

        if not user:
            logger.warning(f"Usuário não encontrado: {request.email}")
            raise UnauthorizedError("Email ou senha incorretos")

        # Verificar se a conta está ativa
        if user.status != "active":
            logger.warning(f"Conta não ativa: {user.email} - {user.status}")
            raise UnauthorizedError("Esta conta não está ativa")

        # Verificar senha
        if not PasswordService.verify_password(request.password, user.password_hash):
            logger.warning(f"Senha incorreta para: {request.email}")
            raise UnauthorizedError("Email ou senha incorretos")

        logger.info(f"Login bem-sucedido: {user.email}")

        # Gerar tokens
        tokens = JWTService.create_token_pair(user.id)

        # Atualizar último login (opcional)
        # await self._repository.update_last_login(user.id)

        return self._to_response(user, tokens)

    def _to_response(self, user: User, tokens) -> LoginResponse:
        """
        Converte a entidade User para LoginResponse.

        Args:
            user: Entidade do usuário.
            tokens: Par de tokens JWT.

        Returns:
            Response DTO.
        """
        return LoginResponse(
            message="Login realizado com sucesso",
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=JWTService.get_expires_in(),
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                phone=user.phone,
                avatar=user.avatar,
                email_confirmed=user.email_confirmed,
                phone_confirmed=user.phone_confirmed,
                plan_type=user.plan.type,
                plan_max_bots=user.plan.max_bots,
                created_at=user.created_at.isoformat() if user.created_at else "",
            )
        )

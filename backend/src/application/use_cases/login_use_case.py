"""
Caso de uso de login de usuário.

Implementa a lógica de negócio para autenticação de usuários,
incluindo verificação de credenciais e geração de tokens.
"""

from src.domain.entities.user import Usuario, StatusUsuario
from src.domain.repositories.user_repository import UserRepository
from src.application.dto.auth_dto import LoginRequest, LoginResponse, UserResponse
from src.application.services.password_service import PasswordService
from src.application.services.jwt_service import JWTService
from src.shared.exceptions import ValidationException, InvalidCredentialsException
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
            ValidationException: Se os dados forem inválidos.
            InvalidCredentialsException: Se as credenciais estiverem incorretas.
        """
        logger.info(f"Tentativa de login: {request.email}")

        # Buscar usuário por email
        user = await self._repository.find_by_email(request.email)

        if not user:
            logger.warning(f"Usuário não encontrado: {request.email}")
            raise InvalidCredentialsException()

        # Verificar se a conta está ativa
        if user.status != StatusUsuario.ATIVO:
            logger.warning(f"Conta não ativa: {user.email} - {user.status}")
            raise InvalidCredentialsException()

        # Verificar senha
        if not PasswordService.verify_password(request.password, user.senha_hash):
            logger.warning(f"Senha incorreta para: {request.email}")
            raise InvalidCredentialsException()

        logger.info(f"Login bem-sucedido: {user.email}")

        # Gerar tokens
        tokens = JWTService.create_token_pair(str(user.id), role=user.role)

        # Atualizar último login
        user.registrar_login()
        await self._repository.update(user)

        return self._to_response(user, tokens)

    def _to_response(self, user: Usuario, tokens) -> LoginResponse:
        """
        Converte a entidade Usuario para LoginResponse.

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
                id=str(user.id),
                email=user.email,
                nome=user.nome,
                telefone=user.telefone,
                avatar=user.avatar,
                email_confirmado=user.email_confirmado,
                telefone_confirmado=user.telefone_confirmado,
                plano_tipo=user.plano.tipo.value if hasattr(user.plano.tipo, 'value') else user.plano.tipo,
                plano_max_bots=user.plano.max_bots,
                role=getattr(user, 'role', 'user'),
                criado_em=user.criado_em.isoformat() if user.criado_em else "",
            )
        )

"""
Caso de uso de login de usuario.

Implementa a logica de negocio para autenticacao de usuarios,
incluindo verificacao de credenciais, geracao de tokens e lockout.
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
    """Caso de uso para login de usuarios."""

    def __init__(self, user_repository: UserRepository):
        self._repository = user_repository

    async def execute(self, request: LoginRequest) -> LoginResponse:
        """
        Executa o login de um usuario.

        Args:
            request: Dados do login.

        Returns:
            Resposta com tokens e dados do usuario.

        Raises:
            ValidationException: Se os dados forem invalidos ou conta bloqueada.
            InvalidCredentialsException: Se as credenciais estiverem incorretas.
        """
        logger.info(f"Tentativa de login: {request.email}")

        # Verificar account lockout
        from src.application.services.token_blacklist import is_account_locked
        locked, remaining = await is_account_locked(request.email)
        if locked:
            minutes = remaining // 60 + 1
            raise ValidationException(
                f"Conta temporariamente bloqueada. Tente novamente em {minutes} minutos.",
                field="email",
            )

        # Buscar usuario por email
        user = await self._repository.find_by_email(request.email)

        if not user:
            logger.warning(f"Usuario nao encontrado: {request.email}")
            from src.application.services.token_blacklist import record_failed_login
            await record_failed_login(request.email)
            raise InvalidCredentialsException()

        # Verificar se a conta esta ativa
        if user.status != StatusUsuario.ATIVO:
            logger.warning(f"Conta nao ativa: {request.email} - {user.status}")
            raise InvalidCredentialsException()

        # Verificar senha
        if not PasswordService.verify_password(request.password, user.senha_hash):
            logger.warning(f"Senha incorreta para: {request.email}")
            from src.application.services.token_blacklist import record_failed_login
            await record_failed_login(request.email)
            raise InvalidCredentialsException()

        # Resetar tentativas falhas (login bem-sucedido)
        from src.application.services.token_blacklist import reset_login_attempts
        await reset_login_attempts(request.email)

        logger.info(f"Login bem-sucedido: {request.email}")

        # Gerar tokens
        tokens = JWTService.create_token_pair(str(user.id), role=user.role)

        # Atualizar ultimo login
        user.registrar_login()
        await self._repository.update(user)

        return self._to_response(user, tokens)

    def _to_response(self, user: Usuario, tokens) -> LoginResponse:
        """Converte a entidade Usuario para LoginResponse."""
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

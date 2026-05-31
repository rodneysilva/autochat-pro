"""
Caso de uso de confirmação de email.

Implementa a geração de token de confirmação e validação
do link de confirmação enviado por email.
"""

from datetime import timedelta, datetime

from src.domain.repositories.user_repository import UserRepository
from src.application.services.jwt_service import JWTService
from src.shared.exceptions import InvalidTokenException, UnauthorizedError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ConfirmEmailUseCase:
    """Caso de uso para confirmação de email."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários.
        """
        self._repository = user_repository

    def generate_confirmation_token(self, user_id: str) -> str:
        """
        Gera um token para confirmação de email.

        Args:
            user_id: ID do usuário.

        Returns:
            Token de confirmação.
        """
        # Token válido por 24 horas
        expire_time = datetime.utcnow() + timedelta(hours=24)

        import jwt
        from src.shared.config import settings

        token = jwt.encode(
            {
                "sub": user_id,
                "type": "email_confirmation",
                "exp": expire_time.timestamp(),
                "iat": datetime.utcnow().timestamp(),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        logger.info(f"Token de confirmação gerado para usuário: {user_id}")
        return token

    async def confirm_email(self, token: str) -> bool:
        """
        Confirma o email do usuário usando o token.

        Args:
            token: Token de confirmação.

        Returns:
            True se confirmado com sucesso.

        Raises:
            InvalidTokenException: Se o token for inválido.
            UnauthorizedError: Se o usuário não existir.
        """
        try:
            import jwt
            from src.shared.config import settings

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            # Verificar tipo
            if payload.get("type") != "email_confirmation":
                logger.warning("Token não é do tipo email_confirmation")
                raise InvalidTokenException()

            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token sem subject")
                raise InvalidTokenException()

            # Buscar usuário
            user = await self._repository.find_by_id(user_id)
            if not user:
                logger.warning(f"Usuário não encontrado: {user_id}")
                raise UnauthorizedError("Usuário não encontrado")

            # Verificar se já está confirmado
            if user.email_confirmed:
                logger.info(f"Email já confirmado: {user.email}")
                return True

            # Confirmar email
            await self._repository.set_email_confirmed(user_id)

            logger.info(f"Email confirmado com sucesso: {user.email}")
            return True

        except jwt.ExpiredSignatureError:
            logger.warning("Token de confirmação expirado")
            raise InvalidTokenException("Token de confirmação expirado")
        except jwt.InvalidTokenError:
            logger.warning("Token de confirmação inválido")
            raise InvalidTokenException("Token de confirmação inválido")

    def generate_confirmation_link(self, token: str) -> str:
        """
        Gera o link de confirmação para o email.

        Args:
            token: Token de confirmação.

        Returns:
            Link completo de confirmação.
        """
        from src.shared.config import settings
        return f"{settings.FRONTEND_URL}/confirm-email?token={token}"

"""
Caso de uso de recuperação de senha.

Implementa a geração de token de reset e validação
do link de recuperação enviado por email.
"""

from datetime import timedelta, datetime

from src.domain.repositories.user_repository import UserRepository
from src.application.services.password_service import PasswordService
from src.shared.exceptions import InvalidTokenException, UnauthorizedError, ValidationError
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class PasswordResetUseCase:
    """Caso de uso para recuperação de senha."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários.
        """
        self._repository = user_repository

    def generate_reset_token(self, email: str) -> str:
        """
        Gera um token para reset de senha.

        Args:
            email: Email do usuário.

        Returns:
            Token de reset.

        Raises:
            ValidationError: Se o email não existir.
        """
        # Token válido por 1 hora
        expire_time = datetime.utcnow() + timedelta(hours=1)

        import jwt
        from src.shared.config import settings

        token = jwt.encode(
            {
                "email": email,
                "type": "password_reset",
                "exp": expire_time.timestamp(),
                "iat": datetime.utcnow().timestamp(),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        logger.info(f"Token de reset gerado para email: {email}")
        return token

    async def send_reset_email(self, email: str, reset_link: str) -> bool:
        """
        Envia email de recuperação de senha.

        Args:
            email: Email do usuário.
            reset_link: Link de reset.

        Returns:
            True se enviado com sucesso (ou se email não existe, para não revelar).
        """
        from src.infrastructure.external_services.email import get_email_service

        # Buscar usuário
        user = await self._repository.find_by_email(email)

        if not user:
            # Não revelar se o email existe
            logger.warning(f"Tentativa de reset para email inexistente: {email}")
            return True

        # Enviar email
        email_service = get_email_service()
        await email_service.send_password_reset_email(
            to_email=user.email,
            user_name=user.name,
            reset_link=reset_link,
        )

        logger.info(f"Email de reset enviado para: {email}")
        return True

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reseta a senha usando o token.

        Args:
            token: Token de reset.
            new_password: Nova senha.

        Returns:
            True se resetado com sucesso.

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
            if payload.get("type") != "password_reset":
                logger.warning("Token não é do tipo password_reset")
                raise InvalidTokenException()

            email = payload.get("email")
            if not email:
                logger.warning("Token sem email")
                raise InvalidTokenException()

            # Buscar usuário
            user = await self._repository.find_by_email(email)
            if not user:
                logger.warning(f"Usuário não encontrado para email: {email}")
                raise UnauthorizedError("Usuário não encontrado")

            # Validar complexidade da nova senha
            from src.application.use_cases.register_use_case import validate_password_complexity
            validate_password_complexity(new_password)

            # Hash da nova senha
            password_hash = PasswordService.hash_password(new_password)

            # Atualizar senha
            await self._repository.update_password(user.id, password_hash)

            logger.info(f"Senha resetada com sucesso para: {email}")
            return True

        except jwt.ExpiredSignatureError:
            logger.warning("Token de reset expirado")
            raise InvalidTokenException("Token de reset expirado")
        except jwt.InvalidTokenError:
            logger.warning("Token de reset inválido")
            raise InvalidTokenException("Token de reset inválido")

    def generate_reset_link(self, token: str) -> str:
        """
        Gera o link de reset para o email.

        Args:
            token: Token de reset.

        Returns:
            Link completo de reset.
        """
        from src.shared.config import settings
        return f"{settings.FRONTEND_URL}/reset-password?token={token}"

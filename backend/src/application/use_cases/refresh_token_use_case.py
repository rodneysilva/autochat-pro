"""
Caso de uso de refresh de token.

Implementa a lógica de negócio para renovação de tokens de acesso
utilizando um token de refresh válido.
"""

import jwt

from src.domain.repositories.user_repository import UserRepository
from src.domain.entities.user import Usuario, StatusUsuario
from src.application.dto.auth_dto import AuthResponse
from src.application.services.jwt_service import JWTService
from src.shared.exceptions import TokenExpiredException, InvalidTokenException, UnauthorizedException
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class RefreshTokenUseCase:
    """Caso de uso para refresh de tokens."""

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o caso de uso.

        Args:
            user_repository: Repositório de usuários.
        """
        self._repository = user_repository

    async def execute(self, refresh_token: str) -> AuthResponse:
        """
        Executa o refresh do token de acesso.

        Args:
            refresh_token: Token de refresh.

        Returns:
            Novo par de tokens (access + refresh).

        Raises:
            InvalidTokenException: Se o token for inválido.
            TokenExpiredException: Se o token estiver expirado.
            UnauthorizedException: Se o usuário não existir ou não estiver ativo.
        """
        logger.info("Tentativa de refresh token")

        try:
            # Decodificar e validar o token
            payload = JWTService.decode_token(refresh_token)

            # Verificar se é um refresh token
            if payload.get("type") != "refresh":
                logger.warning("Token não é do tipo refresh")
                raise InvalidTokenException()

            # Obter o subject (ID do usuário)
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token sem subject")
                raise InvalidTokenException()

            # Buscar usuário
            user = await self._repository.find_by_id(user_id)
            if not user:
                logger.warning(f"Usuário não encontrado: {user_id}")
                raise UnauthorizedException("Usuário não encontrado")

            # Verificar se a conta está ativa
            if user.status != StatusUsuario.ATIVO:
                logger.warning(f"Conta não ativa: {user.email} - {user.status}")
                raise UnauthorizedException("Esta conta não está ativa")

            logger.info(f"Refresh token bem-sucedido: {user.email}")

            # Gerar novo par de tokens
            tokens = JWTService.create_token_pair(str(user.id))

            return AuthResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type="bearer",
                expires_in=JWTService.get_expires_in(),
            )

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

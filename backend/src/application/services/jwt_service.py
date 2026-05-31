"""
Serviço de gerenciamento de tokens JWT.

Fornece funções para geração, validação e refresh de tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt

from src.shared.config import settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class JWTTokenPair:
    """Par de tokens JWT."""

    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token


class JWTService:
    """Serviço para operações com JWT."""

    @staticmethod
    def create_access_token(
        subject: str,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria um token de acesso.

        Args:
            subject: Identificador do usuário (geralmente o ID).
            extra_claims: Claims adicionais para incluir no token.

        Returns:
            Token JWT codificado.
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {
            "sub": subject,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "access",
        }

        if extra_claims:
            to_encode.update(extra_claims)

        encoded = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        logger.debug(f"Access token criado para subject: {subject}")
        return encoded

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """
        Cria um token de refresh.

        Args:
            subject: Identificador do usuário.

        Returns:
            Token JWT de refresh codificado.
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": subject,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "refresh",
        }

        encoded = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        logger.debug(f"Refresh token criado para subject: {subject}")
        return encoded

    @staticmethod
    def create_token_pair(subject: str) -> JWTTokenPair:
        """
        Cria um par de tokens (access + refresh).

        Args:
            subject: Identificador do usuário.

        Returns:
            Par de tokens.
        """
        access = JWTService.create_access_token(subject)
        refresh = JWTService.create_refresh_token(subject)
        return JWTTokenPair(access, refresh)

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodifica e valida um token JWT.

        Args:
            token: Token JWT.

        Returns:
            Payload do token decodificado.

        Raises:
            jwt.ExpiredSignatureError: Token expirado.
            jwt.InvalidTokenError: Token inválido.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            logger.debug("Token decodificado com sucesso")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {e}")
            raise

    @staticmethod
    def verify_token_type(token: str, expected_type: str) -> bool:
        """
        Verifica se o token é do tipo esperado.

        Args:
            token: Token JWT.
            expected_type: Tipo esperado ('access' ou 'refresh').

        Returns:
            True se o tipo está correto.
        """
        payload = JWTService.decode_token(token)
        return payload.get("type") == expected_type

    @staticmethod
    def get_subject(token: str) -> Optional[str]:
        """
        Extrai o subject (ID do usuário) do token.

        Args:
            token: Token JWT.

        Returns:
            Subject do token ou None.
        """
        try:
            payload = JWTService.decode_token(token)
            return payload.get("sub")
        except jwt.PyJWTError:
            return None

    @staticmethod
    def get_expires_in() -> int:
        """
        Retorna o tempo de expiração do access token em segundos.

        Returns:
            Tempo de expiração em segundos.
        """
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

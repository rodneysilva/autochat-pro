"""
Serviço de gerenciamento de senhas.

Fornece funções para hash e verificação de senhas usando bcrypt.
"""

from passlib.context import CryptContext

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

# Contexto de criptografia com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Serviço para operações com senhas."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera o hash de uma senha.

        Args:
            password: Senha em texto plano.

        Returns:
            Hash da senha.
        """
        hashed = pwd_context.hash(password)
        logger.debug("Senha hash gerada")
        return hashed

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha está correta.

        Args:
            plain_password: Senha em texto plano.
            hashed_password: Hash da senha armazenada.

        Returns:
            True se a senha estiver correta.
        """
        is_correct = pwd_context.verify(plain_password, hashed_password)
        if is_correct:
            logger.debug("Senha verificada com sucesso")
        else:
            logger.warning("Tentativa de senha incorreta")
        return is_correct

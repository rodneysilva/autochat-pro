"""
Serviço de gerenciamento de senhas.

Fornece funções para hash e verificação de senhas usando bcrypt.
"""

import bcrypt

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


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
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        logger.debug("Senha hash gerada")
        return hashed.decode('utf-8')

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
        is_correct = bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
        if is_correct:
            logger.debug("Senha verificada com sucesso")
        else:
            logger.warning("Tentativa de senha incorreta")
        return is_correct

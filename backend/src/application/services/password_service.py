"""
Serviço de hash e verificação de senhas usando Argon2.

Mais confiável que bcrypt para uso com uvicorn (sem bug de C extension).
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


class PasswordService:
    """
    Serviço para hash e verificação de senhas.
    Usa Argon2id — resistente a GPU/ASIC, sem problemas de C extension.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash Argon2 para a senha."""
        return _ph.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        try:
            _ph.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """Verifica se o hash precisa ser atualizado (parâmetros mudaram)."""
        return _ph.check_needs_rehash(hashed_password)

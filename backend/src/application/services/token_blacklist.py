"""
Serviço de blacklist de tokens usando Redis.

Permite invalidar tokens (logout real) e lockout de contas.
"""

import time
from typing import Optional

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

# Instância lazy de Redis
_redis = None


async def _get_redis():
    """Lazy load Redis client."""
    global _redis
    if _redis is None:
        try:
            import redis.asyncio as aioredis
            from src.shared.config import settings
            _redis = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        except Exception as e:
            logger.warning(f"Redis não disponível: {e}")
            return None
    return _redis


async def blacklist_token(token: str, ttl_seconds: int) -> bool:
    """
    Adiciona um token à blacklist com TTL.

    Args:
        token: Token JWT (jti ou hash do token).
        ttl_seconds: Tempo de vida da blacklist (deve ser o tempo restante do token).

    Returns:
        True se adicionado com sucesso.
    """
    redis = await _get_redis()
    if redis is None:
        return False

    try:
        # Usar hash do token como chave (tokens são longos)
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"
        await redis.setex(key, ttl_seconds, "1")
        logger.debug(f"Token adicionado à blacklist (TTL={ttl_seconds}s)")
        return True
    except Exception as e:
        logger.warning(f"Erro ao adicionar token à blacklist: {e}")
        return False


async def is_token_blacklisted(token: str) -> bool:
    """
    Verifica se um token está na blacklist.

    Args:
        token: Token JWT.

    Returns:
        True se o token está na blacklist.
    """
    redis = await _get_redis()
    if redis is None:
        return False

    try:
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"
        return await redis.exists(key) > 0
    except Exception as e:
        logger.warning(f"Erro ao verificar blacklist: {e}")
        return False


# ========================================
# Account Lockout
# ========================================

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutos


async def record_failed_login(email: str) -> int:
    """
    Registra uma tentativa de login falha. Retorna o total de tentativas.

    Args:
        email: Email do usuário.

    Returns:
        Número de tentativas falhas consecutivas.
    """
    redis = await _get_redis()
    if redis is None:
        return 0

    try:
        key = f"login_attempts:{email}"
        attempts = await redis.incr(key)
        if attempts == 1:
            await redis.expire(key, LOCKOUT_DURATION)
        return attempts
    except Exception as e:
        logger.warning(f"Erro ao registrar tentativa falha: {e}")
        return 0


async def get_login_attempts(email: str) -> int:
    """Retorna tentativas falhas restantes."""
    redis = await _get_redis()
    if redis is None:
        return 0
    try:
        key = f"login_attempts:{email}"
        val = await redis.get(key)
        return int(val) if val else 0
    except Exception:
        return 0


async def is_account_locked(email: str) -> tuple[bool, int]:
    """
    Verifica se conta está bloqueada por tentativas falhas.

    Returns:
        (is_locked, remaining_seconds)
    """
    redis = await _get_redis()
    if redis is None:
        return False, 0

    try:
        key = f"login_attempts:{email}"
        val = await redis.get(key)
        if not val or int(val) < MAX_LOGIN_ATTEMPTS:
            return False, 0
        ttl = await redis.ttl(key)
        return True, max(0, ttl)
    except Exception:
        return False, 0


async def reset_login_attempts(email: str) -> None:
    """Reseta contador de tentativas após login bem-sucedido."""
    redis = await _get_redis()
    if redis is None:
        return
    try:
        await redis.delete(f"login_attempts:{email}")
    except Exception as e:
        logger.warning(f"Erro ao resetar tentativas: {e}")

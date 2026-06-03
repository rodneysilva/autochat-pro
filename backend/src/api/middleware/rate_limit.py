"""
Middleware de rate limiting baseado em Redis.

Limita requisições por IP e/ou por usuário autenticado.
Utiliza as variáveis RATE_LIMIT_FREE/BASIC/PRO do config.
"""

import time
from functools import wraps
from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter usando Redis (sliding window)."""

    def __init__(self, redis_client=None):
        self._redis = redis_client

    async def _get_redis(self):
        """Lazy load Redis client."""
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                from src.shared.config import settings
                self._redis = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                )
            except Exception as e:
                logger.warning(f"Redis não disponível para rate limiting: {e}")
                return None
        return self._redis

    async def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60,
    ) -> tuple[bool, dict]:
        """
        Verifica se a key atingiu o limite.

        Returns:
            (is_limited, info_dict) — info_dict contém headers de rate limit
        """
        redis = await self._get_redis()
        if redis is None:
            return False, {"X-RateLimit-Limit": str(max_requests), "X-RateLimit-Remaining": str(max_requests)}

        now = time.time()
        window_key = f"rl:{key}"

        try:
            pipe = redis.pipeline()
            pipe.zremrangebyscore(window_key, 0, now - window_seconds)
            pipe.zadd(window_key, {str(now): now})
            pipe.zcard(window_key)
            pipe.expire(window_key, window_seconds + 1)
            results = await pipe.execute()

            current = results[2]
            remaining = max(0, max_requests - current)

            headers = {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(now + window_seconds)),
            }

            return current > max_requests, headers
        except Exception as e:
            logger.warning(f"Erro no rate limiting: {e}")
            return False, {}

    async def cleanup(self):
        """Fecha conexão Redis."""
        if self._redis:
            await self._redis.close()


# Instância global
rate_limiter = RateLimiter()


async def rate_limit_auth(request: Request, max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiting para endpoints de autenticação.

    Usa IP do cliente + endpoint como chave.
    Limpa padrão: 10 req/min por IP para login/register.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"auth:{client_ip}"

    is_limited, headers = await rate_limiter.is_rate_limited(key, max_requests, window_seconds)

    if is_limited:
        logger.warning(f"Rate limit atingido para IP: {client_ip}")
        return True, JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "erro": {
                    "codigo": "RATE_LIMIT_EXCEEDED",
                    "mensagem": "Muitas requisições. Tente novamente em instantes.",
                }
            },
            headers=headers,
        )

    return False, headers

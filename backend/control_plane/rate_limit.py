"""Control-plane rate limiting service."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from redis.asyncio import Redis
from structlog import get_logger

from config import get_settings
from .api_keys import APIKeyContext

logger = get_logger(__name__)


class RateLimitExceeded(Exception):
    """Raised when API key exceeds rate limit."""
    def __init__(self, limit: int, window: int) -> None:
        self.limit = limit
        self.window = window
        super().__init__(f"Rate limit exceeded: {limit} requests per {window} seconds")


class RateLimiter:
    """Redis-based rate limiting per API key."""
    
    def __init__(self, redis: Optional[Redis] = None) -> None:
        self._redis = redis
        self._settings = get_settings()
    
    async def _ensure_redis(self) -> Redis:
        """Lazy Redis connection."""
        if not self._redis:
            self._redis = Redis.from_url(self._settings.redis_url, decode_responses=True)
        return self._redis

    async def enforce(self, ctx: APIKeyContext) -> None:
        """Check and enforce rate limit for the given context."""
        if ctx.rate_limit_per_min <= 0:
            return  # No rate limiting
        
        redis = await self._ensure_redis()
        
        # 1. Burst Limit Check (20 requests/second)
        burst_limit = 20
        now = datetime.utcnow()
        burst_key = f"rate:burst:{ctx.api_key_id}:{now.strftime('%Y%m%d%H%M%S')}"
        
        burst_current = await redis.incr(burst_key)
        if burst_current == 1:
            await redis.expire(burst_key, 5)  # 5 seconds to ensure cleanup
            
        if burst_current > burst_limit:
            logger.warning(
                "Burst limit exceeded",
                api_key_id=ctx.api_key_id,
                current=burst_current,
                limit=burst_limit,
            )
            raise RateLimitExceeded(burst_limit, 1)
        
        # 2. Sustained Limit Check (per minute)
        # Key format: rate:{api_key_id}:{YYYYMMDDHHMM}
        window_key = f"rate:{ctx.api_key_id}:{now.strftime('%Y%m%d%H%M')}"
        
        # Increment counter
        try:
            current = await redis.incr(window_key)
            if current == 1:
                # Set expiry for the window
                await redis.expire(window_key, 120)  # 2 minutes to ensure cleanup
            
            if current > ctx.rate_limit_per_min:
                logger.warning(
                    "Rate limit exceeded",
                    api_key_id=ctx.api_key_id,
                    current=current,
                    limit=ctx.rate_limit_per_min,
                    window=window_key,
                )
                raise RateLimitExceeded(ctx.rate_limit_per_min, 60)
            
            logger.debug(
                "Rate limit check passed",
                api_key_id=ctx.api_key_id,
                current=current,
                limit=ctx.rate_limit_per_min,
            )
            
        except Exception as e:
            # If Redis fails, allow the request but log the error
            logger.error(
                "Rate limiter Redis error",
                api_key_id=ctx.api_key_id,
                error=str(e),
            )
            # Don't block requests if Redis is down

    async def get_current_usage(self, api_key_id: str) -> int:
        """Get current usage in the current minute window."""
        redis = await self._ensure_redis()
        now = datetime.utcnow()
        window_key = f"rate:{api_key_id}:{now.strftime('%Y%m%d%H%M')}"
        try:
            return int(await redis.get(window_key) or 0)
        except Exception:
            return 0

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()


rate_limiter = RateLimiter()
"""
Global rate limiter instance.
"""

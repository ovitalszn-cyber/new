"""Redis connection pool with reconnection logic for V6 system."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog
import redis.asyncio as redis

logger = structlog.get_logger()


class RedisConnectionPool:
    """Redis connection pool with automatic reconnection."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", max_connections: int = 20):
        """
        Initialize Redis connection pool.
        
        Args:
            redis_url: Redis connection URL
            max_connections: Maximum number of connections in pool
        """
        self.redis_url = redis_url
        self.max_connections = max_connections
        self._pool: Optional[redis.ConnectionPool] = None
        self._redis: Optional[redis.Redis] = None
        self._connected = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._last_ping: Optional[datetime] = None
    
    async def connect(self) -> bool:
        """Connect to Redis with connection pool."""
        try:
            # Create connection pool
            self._pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Create Redis client with pool
            self._redis = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._redis.ping()
            self._connected = True
            self._last_ping = datetime.now(timezone.utc)
            
            # Start health check task
            self._reconnect_task = asyncio.create_task(self._health_check_loop())
            
            logger.info("Connected to Redis with connection pool", 
                       url=self.redis_url, 
                       max_connections=self.max_connections)
            return True
            
        except Exception as exc:
            logger.error("Failed to connect to Redis", error=str(exc))
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis and cleanup."""
        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
        
        if self._redis:
            await self._redis.close()
        
        if self._pool:
            await self._pool.disconnect()
        
        self._connected = False
        logger.info("Disconnected from Redis connection pool")
    
    async def _health_check_loop(self) -> None:
        """Background health check and reconnection loop."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if self._connected and self._redis:
                    try:
                        await self._redis.ping()
                        self._last_ping = datetime.now(timezone.utc)
                    except Exception as exc:
                        logger.warning("Redis ping failed, attempting reconnection", error=str(exc))
                        await self._attempt_reconnection()
                else:
                    await self._attempt_reconnection()
                    
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Error in health check loop", error=str(exc))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _attempt_reconnection(self) -> None:
        """Attempt to reconnect to Redis."""
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                logger.info("Attempting Redis reconnection", attempt=attempt + 1, max_attempts=max_attempts)
                
                # Close existing connections
                if self._redis:
                    await self._redis.close()
                if self._pool:
                    await self._pool.disconnect()
                
                # Reconnect
                self._pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    max_connections=self.max_connections,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30
                )
                
                self._redis = redis.Redis(connection_pool=self._pool)
                await self._redis.ping()
                
                self._connected = True
                self._last_ping = datetime.now(timezone.utc)
                
                logger.info("Redis reconnection successful", attempt=attempt + 1)
                break
                
            except Exception as exc:
                logger.warning("Redis reconnection attempt failed", 
                             attempt=attempt + 1, 
                             error=str(exc))
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Redis reconnection failed after all attempts")
                    self._connected = False
    
    @property
    def redis(self) -> Optional[redis.Redis]:
        """Get Redis client."""
        return self._redis if self._connected else None
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get connection pool information."""
        if not self._connected or not self._redis:
            return {
                "connected": False,
                "error": "Not connected to Redis"
            }
        
        try:
            info = await self._redis.info()
            pool_info = self._pool.connection_pool_kwargs if self._pool else {}
            
            return {
                "connected": True,
                "url": self.redis_url,
                "max_connections": self.max_connections,
                "redis_version": info.get("redis_version"),
                "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                "connected_clients": info.get("connected_clients", 0),
                "last_ping": self._last_ping.isoformat() if self._last_ping else None,
                "pool_kwargs": pool_info
            }
        
        except Exception as exc:
            return {
                "connected": False,
                "error": str(exc)
            }


# Global connection pool
_redis_pool: Optional[RedisConnectionPool] = None


async def get_redis_pool() -> RedisConnectionPool:
    """Get global Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        from config import get_settings
        settings = get_settings()
        _redis_pool = RedisConnectionPool(
            redis_url=getattr(settings, 'redis_url', 'redis://localhost:6379'),
            max_connections=getattr(settings, 'redis_max_connections', 20)
        )
        if not await _redis_pool.connect():
            raise RuntimeError("Failed to connect to Redis")
    return _redis_pool


async def shutdown_redis_pool():
    """Shutdown Redis connection pool."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None

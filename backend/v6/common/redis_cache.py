"""Redis-based cache manager for V6 system."""

from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union

import structlog
import redis.asyncio as redis

from v6.common.redis_pool import get_redis_pool

logger = structlog.get_logger()


class RedisCacheManager:
    """Redis cache manager optimized for V6 performance."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", key_prefix: str = "v6"):
        """
        Initialize Redis cache manager.
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Key prefix for all cache entries
        """
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self._redis_pool = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Redis using connection pool."""
        try:
            self._redis_pool = await get_redis_pool()
            self._connected = self._redis_pool.is_connected
            logger.info("Connected to Redis via connection pool", url=self.redis_url)
            return self._connected
        except Exception as exc:
            logger.error("Failed to connect to Redis", error=str(exc))
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._connected = False
        logger.info("Disconnected from Redis cache manager")
    
    def _make_key(self, *parts: str) -> str:
        """Create a Redis key with prefix."""
        return f"{self.key_prefix}:" + ":".join(str(part) for part in parts)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._connected or not self._redis_pool:
            logger.warning("Redis not connected, cannot get key", key=key)
            return None
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return None
        
        try:
            data = await redis_client.get(key)
            if data is None:
                return None
            
            # Try to deserialize
            try:
                return pickle.loads(data)
            except (pickle.PickleError, TypeError):
                # Fallback to JSON
                try:
                    return json.loads(data.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return data.decode('utf-8')
        
        except Exception as exc:
            logger.error("Failed to get from Redis", key=key, error=str(exc))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        if not self._connected or not self._redis_pool:
            logger.warning("Redis not connected, cannot set key", key=key)
            return False
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return False
        
        try:
            # Serialize using pickle for complex objects
            if isinstance(value, (dict, list, tuple)) or hasattr(value, '__dict__'):
                data = pickle.dumps(value)
            else:
                data = str(value).encode('utf-8')
            
            if ttl:
                await redis_client.setex(key, ttl, data)
            else:
                await redis_client.set(key, data)
            
            return True
        
        except Exception as exc:
            logger.error("Failed to set in Redis", key=key, error=str(exc))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if not self._connected or not self._redis_pool:
            return False
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return False
        
        try:
            await redis_client.delete(key)
            return True
        except Exception as exc:
            logger.error("Failed to delete from Redis", key=key, error=str(exc))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._connected or not self._redis_pool:
            return False
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return False
        
        try:
            return bool(await redis_client.exists(key))
        except Exception as exc:
            logger.error("Failed to check key existence in Redis", key=key, error=str(exc))
            return False
    
    async def get_keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        if not self._connected or not self._redis_pool:
            return []
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return []
        
        try:
            keys = await redis_client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as exc:
            logger.error("Failed to get keys from Redis", pattern=pattern, error=str(exc))
            return []
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self._connected or not self._redis_pool:
            return 0
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return 0
        
        try:
            keys = await redis_client.keys(pattern)
            if keys:
                deleted = await redis_client.delete(*keys)
                logger.info("Cleared keys from Redis", pattern=pattern, deleted=deleted)
                return deleted
            return 0
        except Exception as exc:
            logger.error("Failed to clear pattern from Redis", pattern=pattern, error=str(exc))
            return 0
    
    # Optimized V6 cache methods
    
    async def store_event(self, canonical_event_id: str, event_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store event data using optimized V6 key structure."""
        event_key = self._make_key("event", canonical_event_id)
        return await self.set(event_key, event_data, ttl)
    
    async def get_event(self, canonical_event_id: str) -> Optional[Dict[str, Any]]:
        """Get event data using optimized V6 key structure."""
        event_key = self._make_key("event", canonical_event_id)
        return await self.get(event_key)
    
    async def store_sport_events(self, sport: str, event_ids: List[str], ttl: int = 3600) -> bool:
        """Store list of event IDs for a sport using optimized V6 key structure."""
        sport_key = self._make_key("sport", sport, "events")
        return await self.set(sport_key, event_ids, ttl)
    
    async def get_sport_events(self, sport: str) -> List[str]:
        """Get list of event IDs for a sport using optimized V6 key structure."""
        sport_key = self._make_key("sport", sport, "events")
        event_ids = await self.get(sport_key)
        return event_ids if isinstance(event_ids, list) else []
    
    async def store_lookup_key(self, sport: str, home_team: str, away_team: str, canonical_id: str, ttl: int = 3600) -> bool:
        """Store event lookup key using optimized V6 key structure."""
        # Normalize teams for lookup
        home_norm = home_team.lower().replace(" ", "_").replace("-", "_")
        away_norm = away_team.lower().replace(" ", "_").replace("-", "_")
        lookup_key = self._make_key("lookup", sport, home_norm, away_norm)
        return await self.set(lookup_key, canonical_id, ttl)
    
    async def get_lookup_key(self, sport: str, home_team: str, away_team: str) -> Optional[str]:
        """Get canonical event ID from lookup using optimized V6 key structure."""
        # Normalize teams for lookup
        home_norm = home_team.lower().replace(" ", "_").replace("-", "_")
        away_norm = away_team.lower().replace(" ", "_").replace("-", "_")
        lookup_key = self._make_key("lookup", sport, home_norm, away_norm)
        return await self.get(lookup_key)
    
    async def store_book_data(self, book_key: str, sport: str, data_type: str, data: Dict[str, Any], ttl: Optional[int] = 300) -> bool:
        """Store book-specific data with TTL."""
        book_key_redis = self._make_key("book", book_key, sport, data_type)
        return await self.set(book_key_redis, data, ttl)
    
    async def get_book_data(self, book_key: str, sport: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Get book-specific data."""
        book_key_redis = self._make_key("book", book_key, sport, data_type)
        return await self.get(book_key_redis)
    
    async def store_sport_snapshot(self, sport: str, snapshot: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store aggregated sport snapshot (odds/props) without TTL by default."""
        snapshot_key = self._make_key("sport", sport, "snapshot")
        return await self.set(snapshot_key, snapshot, ttl)

    async def get_sport_snapshot(self, sport: str) -> Optional[Dict[str, Any]]:
        """Retrieve aggregated sport snapshot."""
        snapshot_key = self._make_key("sport", sport, "snapshot")
        return await self.get(snapshot_key)

    async def store_feed_stage(
        self,
        sport: str,
        stage: str,
        payload: Dict[str, Any],
        ttl: Optional[int] = 60,
    ) -> bool:
        """Store intermediate feed payloads (raw, normalized, modeled, etc.)."""
        stage_key = self._make_key("sport", sport, "stage", stage)
        return await self.set(stage_key, payload, ttl)

    async def get_feed_stage(self, sport: str, stage: str) -> Optional[Dict[str, Any]]:
        """Fetch intermediate feed payloads."""
        stage_key = self._make_key("sport", sport, "stage", stage)
        return await self.get(stage_key)

    async def store_metrics(self, metrics: Dict[str, Any], ttl: int = 300) -> bool:
        """Store system metrics."""
        metrics_key = self._make_key("metrics", "system")
        return await self.set(metrics_key, metrics, ttl)
    
    async def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get system metrics."""
        metrics_key = self._make_key("metrics", "system")
        return await self.get(metrics_key)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health."""
        if not self._connected or not self._redis_pool:
            return {
                "connected": False,
                "error": "Not connected to Redis"
            }
        
        redis_client = self._redis_pool.redis
        if not redis_client:
            return {
                "connected": False,
                "error": "Redis client not available"
            }
        
        try:
            # Test ping
            start_time = datetime.now(timezone.utc)
            await redis_client.ping()
            ping_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Get info
            info = await redis_client.info()
            
            # Count keys
            key_count = len(await redis_client.keys(f"{self.key_prefix}:*"))
            
            return {
                "connected": True,
                "ping_time_seconds": ping_time,
                "redis_version": info.get("redis_version"),
                "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                "connected_clients": info.get("connected_clients", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "our_keys": key_count,
                "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)),
            }
        
        except Exception as exc:
            return {
                "connected": False,
                "error": str(exc)
            }
    
    async def set_hash(self, sport: str, hash_val: str, ttl: int = 86400) -> bool:
        """Store the current hash for a sport's data state."""
        hash_key = self._make_key("sport", sport, "hash")
        return await self.set(hash_key, hash_val, ttl)

    async def get_hash(self, sport: str) -> Optional[str]:
        """Get the last stored hash for a sport."""
        hash_key = self._make_key("sport", sport, "hash")
        val = await self.get(hash_key)
        return str(val) if val else None


# Global cache manager instance
_cache_manager: Optional[RedisCacheManager] = None


async def get_cache_manager() -> RedisCacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        from config import get_settings
        settings = get_settings()
        _cache_manager = RedisCacheManager(
            redis_url=getattr(settings, 'redis_url', 'redis://localhost:6379'),
            key_prefix="v6"
        )
        if not await _cache_manager.connect():
            raise RuntimeError("Failed to connect to Redis")
    return _cache_manager


async def shutdown_cache_manager():
    """Shutdown cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.disconnect()
        _cache_manager = None

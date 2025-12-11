"""Simple in-memory cache with TTL for V6 engines."""

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional


class CacheEntry:
    """Single cache entry with TTL."""
    
    def __init__(self, data: Any, ttl_seconds: int = 60):
        self.data = data
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.created_at > self.ttl_seconds
    
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds."""
        return time.time() - self.created_at


class SimpleCache:
    """Simple in-memory cache with automatic cleanup."""
    
    def __init__(self, default_ttl: int = 60, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        self._hits += 1
        return entry.data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        # Cleanup if cache is full
        if len(self._cache) >= self.max_size:
            self._cleanup_expired()
        
        # If still full, remove oldest entry
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
        
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        entries = []
        for key, entry in self._cache.items():
            entries.append({
                "key": key,
                "age_seconds": entry.age_seconds(),
                "ttl_seconds": entry.ttl_seconds,
                "expires_in": max(0, entry.ttl_seconds - entry.age_seconds()),
                "is_expired": entry.is_expired(),
            })
        
        return {
            "stats": self.get_stats(),
            "entries": sorted(entries, key=lambda x: x["age_seconds"]),
        }


# Global cache instances
_odds_cache = SimpleCache(default_ttl=30, max_size=500)  # Odds change frequently
_props_cache = SimpleCache(default_ttl=60, max_size=1000)  # Props change less frequently
_games_cache = SimpleCache(default_ttl=300, max_size=200)  # Games change rarely


def get_odds_cache() -> SimpleCache:
    """Get odds cache instance."""
    return _odds_cache


def get_props_cache() -> SimpleCache:
    """Get props cache instance."""
    return _props_cache


def get_games_cache() -> SimpleCache:
    """Get games cache instance."""
    return _games_cache


def cache_key(*parts: str) -> str:
    """Generate cache key from parts."""
    return ":".join(str(part) for part in parts)

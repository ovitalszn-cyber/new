"""Rate limiter for API calls to prevent overwhelming external services."""

from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}
        self._lock = asyncio.Lock()
    
    async def acquire(self, key: str = "default") -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            key: Identifier for the rate limit bucket
            
        Returns:
            True if request is allowed, False otherwise
        """
        async with self._lock:
            now = time.time()
            
            # Initialize bucket if doesn't exist
            if key not in self.requests:
                self.requests[key] = []
            
            # Remove old requests outside the time window
            cutoff = now - self.time_window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # Check if we can make a request
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            
            return False
    
    async def wait_if_needed(self, key: str = "default") -> None:
        """
        Wait until a request is allowed.
        
        Args:
            key: Identifier for the rate limit bucket
        """
        while not await self.acquire(key):
            # Calculate wait time until oldest request expires
            if key in self.requests[key] and self.requests[key]:
                oldest_request = min(self.requests[key])
                wait_time = self.time_window - (time.time() - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(min(wait_time, 1.0))  # Wait max 1 second
            else:
                await asyncio.sleep(0.1)  # Small delay
    
    def get_stats(self) -> Dict[str, int]:
        """Get current rate limit statistics."""
        stats = {}
        for key, requests in self.requests.items():
            now = time.time()
            cutoff = now - self.time_window
            recent_requests = len([r for r in requests if r > cutoff])
            stats[key] = recent_requests
        return stats


class RateLimitedSemaphore:
    """Combination of semaphore and rate limiter."""
    
    def __init__(self, max_concurrent: int, rate_limiter: RateLimiter):
        """
        Initialize rate limited semaphore.
        
        Args:
            max_concurrent: Maximum concurrent operations
            rate_limiter: Rate limiter instance
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = rate_limiter
    
    async def acquire(self, key: str = "default"):
        """Acquire both semaphore and rate limit."""
        await self.semaphore.acquire()
        await self.rate_limiter.wait_if_needed(key)
        return self
    
    async def __aenter__(self):
        return await self.acquire()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()


# Global rate limiters
# Lunosoft API: 10 requests per second per book
_lunosoft_limiter = RateLimiter(max_requests=10, time_window=1)
# Overall API: 100 requests per second
_global_limiter = RateLimiter(max_requests=100, time_window=1)


def get_lunosoft_limiter() -> RateLimiter:
    """Get Lunosoft-specific rate limiter."""
    return _lunosoft_limiter


def get_global_limiter() -> RateLimiter:
    """Get global rate limiter."""
    return _global_limiter

"""Metrics and monitoring for V6 engines."""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import structlog

logger = structlog.get_logger()


class MetricsCollector:
    """Collects and tracks performance metrics."""
    
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
        self.error_counts = defaultdict(int)
        self.book_stats = defaultdict(lambda: defaultdict(int))
        self.start_time = time.time()
    
    def increment(self, metric: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = self._make_key(metric, tags)
        self.counters[key] += value
    
    def timing(self, metric: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing metric."""
        key = self._make_key(metric, tags)
        self.timers[key].append(duration)
        
        # Keep only last 1000 measurements to prevent memory growth
        if len(self.timers[key]) > 1000:
            self.timers[key] = self.timers[key][-1000:]
    
    def gauge(self, metric: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        key = self._make_key(metric, tags)
        self.gauges[key] = value
    
    def error(self, error_type: str, book_key: Optional[str] = None) -> None:
        """Record an error."""
        self.error_counts[error_type] += 1
        if book_key:
            self.book_stats[book_key]['errors'] += 1
    
    def book_success(self, book_key: str, data_type: str) -> None:
        """Record successful data fetch from a book."""
        self.book_stats[book_key][f'{data_type}_success'] += 1
        self.book_stats[book_key]['total_success'] += 1
    
    def book_request(self, book_key: str, data_type: str) -> None:
        """Record a request to a book."""
        self.book_stats[book_key][f'{data_type}_requests'] += 1
        self.book_stats[book_key]['total_requests'] += 1
    
    def _make_key(self, metric: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a metric key with tags."""
        if not tags:
            return metric
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric}[{tag_str}]"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        uptime = time.time() - self.start_time
        
        # Calculate timer statistics
        timer_stats = {}
        for key, times in self.timers.items():
            if times:
                timer_stats[key] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "recent_avg": sum(times[-10:]) / min(len(times), 10),
                }
        
        # Calculate book success rates
        book_performance = {}
        for book_key, stats in self.book_stats.items():
            total_requests = stats.get('total_requests', 0)
            total_success = stats.get('total_success', 0)
            success_rate = total_success / total_requests if total_requests > 0 else 0
            
            book_performance[book_key] = {
                **stats,
                "success_rate": success_rate,
                "error_rate": stats.get('errors', 0) / total_requests if total_requests > 0 else 0,
            }
        
        return {
            "uptime_seconds": uptime,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timers": timer_stats,
            "errors": dict(self.error_counts),
            "book_performance": dict(book_performance),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.timers.clear()
        self.gauges.clear()
        self.error_counts.clear()
        self.book_stats.clear()
        self.start_time = time.time()


# Global metrics collector
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    return _metrics


class TimedOperation:
    """Context manager for timing operations."""
    
    def __init__(self, metric: str, tags: Optional[Dict[str, str]] = None):
        self.metric = metric
        self.tags = tags
        self.start_time = None
        self.metrics = get_metrics()
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics.timing(self.metric, duration, self.tags)
            
            if exc_type is not None:
                self.metrics.error(f"{self.metric}_error")
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics.timing(self.metric, duration, self.tags)
            
            if exc_type is not None:
                self.metrics.error(f"{self.metric}_error")


def timed(metric: str, tags: Optional[Dict[str, str]] = None):
    """Decorator for timing functions."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            async with TimedOperation(metric, tags):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with TimedOperation(metric, tags):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

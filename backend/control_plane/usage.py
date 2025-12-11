"""Control-plane usage tracking service."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Dict, Any, List

from structlog import get_logger

from db.auth_db import auth_db
from .api_keys import APIKeyContext

logger = get_logger(__name__)


class UsageTracker:
    """Logs API usage and maintains monthly aggregates."""
    
    def __init__(self) -> None:
        self._db = auth_db

    async def record_request(
        self,
        ctx: APIKeyContext,
        endpoint: str,
        method: str,
        status_code: int,
        credits_used: int = 1,
        latency_ms: int = None,
    ) -> None:
        """Record a single API request."""
        # Log to database (async wrapper)
        await asyncio.to_thread(
            self._db.log_usage,
            ctx.user_id,
            ctx.api_key_id,
            endpoint,
            method,
            status_code,
            credits_used,
            latency_ms,
        )
        
        # Update monthly aggregates
        await asyncio.to_thread(
            self._db.increment_monthly_usage,
            ctx.user_id,
            ctx.key_type,
            credits_used,
        )
        
        logger.debug(
            "Usage recorded",
            user_id=ctx.user_id,
            api_key_id=ctx.api_key_id,
            endpoint=endpoint,
            credits=credits_used,
        )

    async def get_monthly_usage(self, user_id: str, key_type: str) -> Dict[str, int]:
        """Get current month usage for a user."""
        return await asyncio.to_thread(self._db.get_monthly_usage, user_id, key_type)

    async def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage stats for a user."""
        test_usage = await self.get_monthly_usage(user_id, "test")
        live_usage = await self.get_monthly_usage(user_id, "live")
        
        return {
            "current_month": datetime.utcnow().strftime("%Y-%m"),
            "test": test_usage,
            "live": live_usage,
            "total": {
                "requests": test_usage["requests"] + live_usage["requests"],
                "credits": test_usage["credits"] + live_usage["credits"],
            }
        }

    async def get_usage_breakdown(
        self,
        user_id: str,
        start_time: datetime,
        *,
        endpoint_limit: int = 5,
        log_limit: int = 25,
        key_prefix_length: int = 8,
    ) -> Dict[str, Any]:
        """Get usage summary, endpoint breakdown, and recent logs since a timestamp."""
        summary = await asyncio.to_thread(
            self._db.get_usage_summary_since,
            user_id,
            start_time,
        )
        endpoints = await asyncio.to_thread(
            self._db.get_endpoint_usage_since,
            user_id,
            start_time,
            endpoint_limit,
        )
        logs = await asyncio.to_thread(
            self._db.get_usage_logs_since,
            user_id,
            start_time,
            log_limit,
        )
        return {
            "summary": summary,
            "endpoints": endpoints,
            "logs": [
                {
                    "id": row["id"],
                    "endpoint": row["endpoint"],
                    "method": row["method"],
                    "status_code": row["status_code"],
                    "credits_used": row["credits_used"],
                    "requested_at": row["requested_at"],
                    "key_id": row["api_key_id"],
                    "latency_ms": row["latency_ms"],
                    "key_preview": (row["key_prefix"] or "")[:key_prefix_length],
                }
                for row in logs
            ],
        }


usage_tracker = UsageTracker()
"""
Global usage tracker instance.
"""

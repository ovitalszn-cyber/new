"""Control-plane quota enforcement service."""

from __future__ import annotations

import asyncio
from typing import Dict, Any

from structlog import get_logger

from db.auth_db import auth_db
from .api_keys import APIKeyContext

logger = get_logger(__name__)


class QuotaExceeded(Exception):
    """Raised when user exceeds monthly quota."""
    def __init__(self, current: int, limit: int) -> None:
        self.current = current
        self.limit = limit
        super().__init__(f"Monthly quota exceeded: {current}/{limit} requests")


class QuotaEnforcer:
    """Enforces monthly quotas per user."""
    
    def __init__(self) -> None:
        self._db = auth_db

    async def check_quota(self, ctx: APIKeyContext) -> None:
        """Check if user has remaining quota for the month."""
        if ctx.monthly_quota <= 0:
            return  # No quota limit
        
        # Get current usage
        usage = await asyncio.to_thread(self._db.get_monthly_usage, ctx.user_id, ctx.key_type)
        current_requests = usage.get("requests", 0)
        
        if current_requests >= ctx.monthly_quota:
            logger.warning(
                "Monthly quota exceeded",
                user_id=ctx.user_id,
                current=current_requests,
                limit=ctx.monthly_quota,
                key_type=ctx.key_type,
            )
            raise QuotaExceeded(current_requests, ctx.monthly_quota)
        
        logger.debug(
            "Quota check passed",
            user_id=ctx.user_id,
            current=current_requests,
            limit=ctx.monthly_quota,
            remaining=ctx.monthly_quota - current_requests,
        )

    async def get_quota_status(self, user_id: str, key_type: str) -> Dict[str, Any]:
        """Get current quota status for a user."""
        # Get user's plan
        user = await asyncio.to_thread(self._db.get_user_by_id, user_id)
        if not user:
            return {"error": "User not found"}
        
        plan = await asyncio.to_thread(self._db.get_plan, user["plan"])
        if not plan:
            return {"error": "Plan not found"}
        
        # Get current usage
        usage = await asyncio.to_thread(self._db.get_monthly_usage, user_id, key_type)
        
        return {
            "plan": user["plan"],
            "key_type": key_type,
            "monthly_quota": plan["monthly_quota"],
            "current_usage": usage.get("requests", 0),
            "remaining": max(0, plan["monthly_quota"] - usage.get("requests", 0)),
            "usage_percentage": min(100, (usage.get("requests", 0) / plan["monthly_quota"]) * 100) if plan["monthly_quota"] > 0 else 0,
        }


quota_enforcer = QuotaEnforcer()
"""
Global quota enforcer instance.
"""

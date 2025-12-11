"""Control-plane API key service."""

from __future__ import annotations

import asyncio
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from structlog import get_logger

from db.auth_db import auth_db

logger = get_logger(__name__)


class APIKeyContext:
    """Resolved API key context attached to request.state by middleware."""
    
    def __init__(
        self,
        api_key_id: str,
        user_id: str,
        user_email: str,
        user_plan: str,
        key_type: str,
        monthly_quota: int,
        rate_limit_per_min: int,
    ) -> None:
        self.api_key_id = api_key_id
        self.user_id = user_id
        self.user_email = user_email
        self.user_plan = user_plan
        self.key_type = key_type
        self.monthly_quota = monthly_quota
        self.rate_limit_per_min = rate_limit_per_min


class APIKeyService:
    """API key validation and management."""
    
    def __init__(self) -> None:
        self._db = auth_db

    async def resolve_key(self, raw_key: str) -> Optional[APIKeyContext]:
        """Resolve API key from Authorization header value."""
        if not raw_key:
            return None
        
        # Remove "Bearer " prefix if present
        if raw_key.startswith("Bearer "):
            raw_key = raw_key[7:].strip()
        
        # Hash the key for lookup
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        logger.warning(f"Computing hash for {raw_key[:15]}...: {key_hash}")
        
        # Look up in database
        record = await asyncio.to_thread(self._db.get_api_key_record_by_hash, key_hash)
        if not record:
            logger.warning("API key not found", key_prefix=raw_key[:12])
            return None
        
        # Validate status
        if record.get("status") != "active":
            logger.warning("API key not active", key_prefix=raw_key[:12], status=record.get("status"))
            return None
        
        # Validate expiry
        if record.get("expires_at"):
            expires_at = datetime.fromisoformat(record["expires_at"])
            if datetime.utcnow() > expires_at:
                logger.warning("API key expired", key_prefix=raw_key[:12])
                return None
        
        # Update last used
        await asyncio.to_thread(self._db.update_last_used, record["id"])
        
        return APIKeyContext(
            api_key_id=record["id"],
            user_id=record["user_id"],
            user_email=record["user_email"],
            user_plan=record["user_plan"],
            key_type=record["key_type"],
            monthly_quota=record.get("monthly_quota", 1000),
            rate_limit_per_min=record.get("rate_limit_per_min", 5),
        )

    async def create_key(
        self,
        user_id: str,
        key_type: str = "live",
        name: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new API key."""
        return await asyncio.to_thread(
            self._db.create_api_key,
            user_id,
            key_type,
            name,
            expires_in_days,
        )

    async def list_keys(self) -> list[Dict[str, Any]]:
        """List all API keys with user info."""
        return await asyncio.to_thread(self._db.list_api_keys)

    async def get_key_by_id(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get API key by ID."""
        return await asyncio.to_thread(self._db.get_api_key_by_id, key_id)

    async def list_keys_for_user(self, user_id: str) -> list[Dict[str, Any]]:
        """List API keys scoped to a single user."""
        return await asyncio.to_thread(self._db.get_api_keys_for_user, user_id)

    async def deactivate_key(self, key_id: str) -> None:
        """Deactivate an API key."""
        await asyncio.to_thread(self._db.deactivate_key, key_id)

    async def delete_key(self, key_id: str) -> None:
        """Permanently delete an API key."""
        await asyncio.to_thread(self._db.delete_api_key, key_id)


api_key_service = APIKeyService()
"""
Global API key service instance used by middleware and endpoints.
"""

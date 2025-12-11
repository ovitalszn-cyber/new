"""Control-plane user service."""

from __future__ import annotations

import asyncio
from typing import Optional, Dict

from structlog import get_logger

from db.auth_db import auth_db

logger = get_logger(__name__)


class UserService:
    """High-level helpers around control-plane user records."""
    
    def __init__(self) -> None:
        self._db = auth_db
    
    async def create_user(
        self,
        email: str,
        password: str,
        plan: str = "free",
        *,
        google_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, str]:
        logger.info("Creating user", email=email, plan=plan)
        return await asyncio.to_thread(
            self._db.create_user,
            email,
            password,
            plan,
            "active",
            google_id,
            name,
        )
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, str]]:
        return await asyncio.to_thread(self._db.get_user_by_email, email)
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, str]]:
        return await asyncio.to_thread(self._db.get_user_by_google_id, google_id)
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, str]]:
        return await asyncio.to_thread(self._db.get_user_by_id, user_id)
    
    async def update_plan(self, user_id: str, plan: str) -> None:
        await asyncio.to_thread(self._db.update_user_plan, user_id, plan)
    
    async def update_profile(
        self,
        user_id: str,
        *,
        google_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        await asyncio.to_thread(self._db.update_user_profile, user_id, google_id, name)


user_service = UserService()

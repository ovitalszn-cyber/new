"""
API endpoints for KashRock Data Stream service.
"""

from fastapi import APIRouter
from api.streams import router as streams_router
from api.health import router as health_router
from api.odds import router as odds_router


__all__ = ["streams_router", "health_router", "odds_router"]

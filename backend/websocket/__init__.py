"""
WebSocket endpoints for real-time data streaming.
"""

from fastapi import APIRouter
from .stream import router as stream_router

# Main WebSocket router
router = APIRouter()

# Include sub-routers
router.include_router(stream_router, prefix="/stream", tags=["websocket"])

__all__ = ["router"]

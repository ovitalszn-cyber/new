"""
Health check API endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "kashrock-data-stream",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with component status."""
    # TODO: Add actual health checks for:
    # - Database connectivity
    # - Redis connectivity
    # - External API health
    # - Stream status
    
    return {
        "status": "healthy",
        "service": "kashrock-data-stream",
        "timestamp": "2024-01-01T00:00:00Z",
        "components": {
            "database": "healthy",
            "redis": "healthy",
            "streams": "healthy",
            "external_apis": "healthy"
        },
        "metrics": {
            "active_streams": 0,
            "total_connections": 0,
            "uptime_seconds": 0
        }
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes/load balancer health checks."""
    return {
        "status": "ready",
        "service": "kashrock-data-stream"
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes health checks."""
    return {
        "status": "alive",
        "service": "kashrock-data-stream"
    }

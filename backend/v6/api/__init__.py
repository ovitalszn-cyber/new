"""
V6 API endpoints for the unified sports data engine.
"""

from .stats import router as stats_router

__all__ = ["stats_router"]

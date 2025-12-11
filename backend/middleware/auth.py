"""FastAPI middleware for authentication, rate limiting, and usage tracking."""

from __future__ import annotations

from typing import Callable
import time
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from structlog import get_logger

from control_plane.api_keys import api_key_service, APIKeyContext
from auth import validate_api_key as legacy_validate_api_key, get_api_key_info
from control_plane.rate_limit import rate_limiter, RateLimitExceeded
from control_plane.quota import quota_enforcer, QuotaExceeded
from control_plane.usage import usage_tracker

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that handles API key validation, rate limiting, and usage logging."""
    
    # Paths that skip auth
    SKIP_PATHS = {
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/",
    }
    
    # Path prefixes that skip auth
    SKIP_PREFIXES = (
        "/v1/auth/",
        "/v1/dashboard/",
        "/v1/public/",  # Public endpoints (no auth required)
        "/v1/books",
        "/v6/admin/", # Handled by custom admin security
    )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Skip auth for certain path prefixes
        if any(request.url.path.startswith(prefix) for prefix in self.SKIP_PREFIXES):
            return await call_next(request)
        
        # Extract API key
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Missing API key. Use Authorization: Bearer <your-key>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Resolve API key
        ctx = await api_key_service.resolve_key(auth_header)
        if not ctx:
            # Fallback to legacy in-memory API key manager for backwards compatibility
            if legacy_validate_api_key(auth_header):
                legacy_info = get_api_key_info(auth_header)
                ctx = APIKeyContext(
                    api_key_id=getattr(legacy_info, "key", "legacy-key"),
                    user_id=getattr(legacy_info, "name", "legacy-user"),
                    user_email=f"{getattr(legacy_info, 'name', 'legacy')}@legacy.kashrock",
                    user_plan="legacy",
                    key_type="legacy",
                    monthly_quota=getattr(legacy_info, "rate_limit", 1000) * 60,
                    rate_limit_per_min=getattr(legacy_info, "rate_limit", 1000),
                )
                request.state.auth_context = ctx
                response = await call_next(request)
                response.headers["X-RateLimit-Limit"] = str(ctx.rate_limit_per_min)
                response.headers["X-Quota-Limit"] = str(ctx.monthly_quota)
                return response

            raise HTTPException(
                status_code=401,
                detail="Invalid or inactive API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Store context in request state for downstream use
        request.state.auth_context = ctx
        
        # Enforce rate limit
        try:
            await rate_limiter.enforce(ctx)
        except RateLimitExceeded as e:
            raise HTTPException(
                status_code=429,
                detail=str(e),
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(e.limit),
                    "X-RateLimit-Window": str(e.window),
                },
            )
        
        # Check monthly quota
        try:
            await quota_enforcer.check_quota(ctx)
        except QuotaExceeded as e:
            raise HTTPException(
                status_code=402,
                detail=str(e),
                headers={
                    "X-Quota-Limit": str(e.limit),
                    "X-Quota-Used": str(e.current),
                },
            )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Record usage (non-blocking)
        try:
            await usage_tracker.record_request(
                ctx,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                credits_used=self._calculate_credits(request),
                latency_ms=latency_ms,
            )
        except Exception as e:
            # Don't fail the request if usage tracking fails
            logger.error("Failed to record usage", error=str(e))
        
        # Add auth headers to response
        response.headers["X-RateLimit-Limit"] = str(ctx.rate_limit_per_min)
        response.headers["X-Quota-Limit"] = str(ctx.monthly_quota)
        
        return response
    
    def _calculate_credits(self, request: Request) -> int:
        """Calculate credits used based on endpoint complexity."""
        path = request.url.path
        
        # Simple credit system - can be expanded
        if path.startswith("/v5/match"):
            return 2  # Match endpoint is more expensive
        elif path.startswith("/v5/event/"):
            return 1
        elif path.startswith("/v4/"):
            return 1
        else:
            return 1  # Default


def get_auth_context(request: Request) -> APIKeyContext:
    """Helper to get auth context from request state."""
    if not hasattr(request.state, "auth_context"):
        raise HTTPException(
            status_code=401,
            detail="Authentication context not found",
        )
    return request.state.auth_context

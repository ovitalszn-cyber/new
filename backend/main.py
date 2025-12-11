"""
KashRock API - Main FastAPI application
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Literal
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
import os

# Load .env from parent directory (where the .env file is located)
env_path = Path.cwd().parent / ".env"
load_dotenv(env_path)



# FastAPI
from fastapi import FastAPI, HTTPException, Query, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, FileResponse
import structlog
from pydantic import BaseModel, EmailStr
from uuid import uuid4 as uuid4_fn
from math import exp
from jose import jwt, JWTError
import httpx

# V6 Hybrid Architecture
from v6.common.redis_pool import get_redis_pool, shutdown_redis_pool
from v6.common.redis_cache import get_cache_manager, shutdown_cache_manager
from v6.background_worker import start_background_worker, stop_background_worker
from v6.api.cached import router as v6_cached_router
from v6.api.stats import router as v6_stats_router
from v6.api.odds import router as v6_odds_router

# Async DB (SQLAlchemy)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import JSONB


# Import Lunosoft and EV sources
from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
from streamers.sharp_odds import SHARP_ODDS_STREAMERS
from streamers.ev_sources import EV_SOURCES, DEFAULT_EV_SOURCES
from api.odds import BOOK_MAP as API_BOOK_MAP

# Dynamic book mapping generation
async def get_lunosoft_books():
    """Fetch current Lunosoft books from their API."""
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.lunosoftware.com/sportsData/SportsDataService.svc/sportsbookIds",
                headers={
                    'accept': '*/*',
                    'user-agent': 'Live Scores & Odds/204 CFNetwork/3860.300.21 Darwin/25.2.0',
                    'priority': 'u=3',
                    'accept-language': 'en-US,en;q=0.9'
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert to our format
            books = {}
            for book in data:
                if isinstance(book, dict):
                    book_id = book.get('SportsbookID')
                    book_name = book.get('SportsbookName', '').replace(' ', '').lower()
                    if book_id and book_name:
                        books[book_name] = book_id
            
            return books
    except Exception as e:
        logger.warning(f"Failed to fetch Lunosoft books: {e}, using fallback")
        # Fallback to our existing Lunosoft books
        return {key: LUNOSOFT_BOOK_STREAMERS[key].BOOK_ID for key in LUNOSOFT_BOOK_STREAMERS.keys()}

async def get_walter_books():
    """Return Walter sportsbooks and supported sports."""
    return {
        'books': [
            'ballybet', 'betmgm', 'betparx', 'betr_us_dfs', 'betrivers', 
            'bovada', 'draftkings', 'espnbet', 'fanatics', 'fanduel', 
            'fliff', 'hardrockbet', 'pinnacle', 'prizepicks', 'sleeper', 
            'underdog', 'williamhill_us'
        ],
        'sports': ['americanfootball_nfl', 'basketball_nba']
    }

async def get_rotowire_books():
    """Return Rotowire sportsbooks and supported sports."""
    return {
        'books': [
            'betmgm-sb', 'betrivers-sb', 'draftkings-sb', 'fanduel-sb', 
            'pick6', 'prizepicks', 'sleeper', 'underdog'
        ],
        'sports': ['americanfootball_nfl', 'basketball_nba', 'icehockey_nhl', 'baseball_mlb', 'soccer']
    }

async def get_proply_books():
    """Return Proply sportsbooks and supported sports."""
    return {
        'books': [
            'ballybet', 'betmgm', 'betrivers', 'draftkings', 'espnbet', 
            'fanatics', 'fanduel', 'fliff', 'hardrockbet', 'novig', 
            'pick6', 'prizepicks', 'underdog', 'williamhill_us'
        ],
        'sports': ['americanfootball_nfl']
    }

async def get_sharp_books():
    """Return Sharp API sportsbooks and supported sports (104 books total)."""
    # Sharp supports 104 books: 8 US sportsbooks + 22 DFS + 74 global books
    return {
        'books': [
            # DFS/Fantasy (22)
            'prizepicks', 'sleeper', 'underdogsportsbook', 'draftkingspick6',
            'fliff', 'hotstreak', 'parlayplay', 'betr', 'betrpicks',
            'novig', 'sporttrade', 'kalshi', 'polymarket', 'ownersbox',
            'boomfantasy', 'dabblefantasy', 'thrillzz', 'rebet', 'rebetpropscity',
            'kutt', 'onyxodds', 'stakeus',
            # US Sportsbooks (8)
            'draftkings', 'fanduel', 'betmgm', 'betrivers', 'caesars',
            'fanatics', 'espnbet', 'circalv',
            # Global books (partial list - 74 total)
            'pinnacle', 'bet365', 'betfairexchange', 'betfairuk', 'bovada',
            'williamhill', 'unibet', 'betway', 'paddypoweruk', 'skybet uk',
            # ... and 64 more global books
        ],
        'sports': ['americanfootball_nfl', 'americanfootball_ncaaf', 'basketball_nba', 
                   'basketball_ncaab', 'icehockey_nhl', 'baseball_mlb']
    }

async def get_all_ev_books():
    """Return all EV source sportsbooks combined and all supported sports."""
    walter_data = await get_walter_books()
    rotowire_data = await get_rotowire_books()
    proply_data = await get_proply_books()
    sharp_data = await get_sharp_books()
    
    # Combine and deduplicate books
    all_books = list(set(
        walter_data['books'] + rotowire_data['books'] + 
        proply_data['books'] + sharp_data['books']
    ))
    
    # Combine and deduplicate sports
    all_sports = list(set(
        walter_data['sports'] + rotowire_data['sports'] + 
        proply_data['sports'] + sharp_data['sports']
    ))
    
    return {
        'books': sorted(all_books),
        'sports': sorted(all_sports)
    }

# EV source sport support mapping for filtering
EV_SOURCE_SPORTS_SUPPORT = {
    'walter': ['americanfootball_nfl', 'basketball_nba'],
    'rotowire': ['americanfootball_nfl', 'basketball_nba', 'icehockey_nhl', 'baseball_mlb', 'soccer'],
    'proply': ['americanfootball_nfl', 'basketball_nba'],
    'sharp_props': ['americanfootball_nfl', 'americanfootball_ncaaf', 'basketball_nba', 
              'basketball_ncaab', 'icehockey_nhl', 'baseball_mlb'],
}

def get_supported_ev_sources(sport: str) -> list:
    """Get list of EV sources that support the requested sport."""
    supported_sources = []
    for source, supported_sports in EV_SOURCE_SPORTS_SUPPORT.items():
        if sport in supported_sports:
            supported_sources.append(source)
    return supported_sources

# Import API routers (V6 only)
from v6.api.stats import router as v6_stats_router
from v6.api.unified import router as v6_unified_router
from v6.api.export import router as v6_export_router
from v6.api.esports import router as v6_esports_router

# Import config
from config import get_settings

# Control-plane services
from control_plane.users import user_service
from control_plane.api_keys import api_key_service

# Import auth
from auth import validate_api_key, get_api_key_info, api_key_manager
from control_plane.usage import usage_tracker
from db.auth_db import auth_db

# Initialize FastAPI app
app = FastAPI(
    title="KashRock API",
    description="The Generational Sport Bettting Data API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include V6 cached API router
app.include_router(v6_cached_router)

# CORS middleware (restrict origins when credentials are used)
dashboard_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dashboard_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auth middleware for usage tracking
from middleware.auth import AuthMiddleware
app.add_middleware(AuthMiddleware)

# Include V6 API routers only
app.include_router(v6_stats_router, prefix="/v6", tags=["v6-stats"])  # Unified stats engine
app.include_router(v6_odds_router, prefix="/v6", tags=["v6-odds"])    # Kashrock odds aggregation engine
app.include_router(v6_unified_router)  # Unified odds + props interface (already prefixed internally)
app.include_router(v6_export_router)   # Export engine (streaming CSV/JSON)
app.include_router(v6_esports_router, prefix="/v6")  # Esports match engine


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================
from db.auth_db import auth_db

# Simple admin security - Replace with your actual email
ADMIN_EMAILS = {"drax@example.com", "test@kashrock.com"} 

async def verify_admin(request: Request):
    # In production, this would verify the JWT token claims
    # For now/local, we'll check if the auth context has an admin email
    # OR if a special Admin-Secret header is present
    
    # 1. Check for Admin Secret Header (for scripts/curl)
    admin_secret = request.headers.get("X-Admin-Secret")
    if admin_secret == os.getenv("ADMIN_SECRET", "dev_admin_secret"):
        return True
        
    # 2. Check Auth Context (for Dashboard)
    # This requires AuthMiddleware to be active and user logged in
    # auth_ctx = getattr(request.state, "auth_context", None)
    # if auth_ctx and auth_ctx.user_email in ADMIN_EMAILS:
    #     return True
        
    raise HTTPException(status_code=403, detail="Admin access required")

@app.get("/v6/admin/usage/users", tags=["admin"])
async def get_admin_user_usage(
    limit: int = 50, 
    _ = Depends(verify_admin)
):
    """Get top users by usage (Admin only)."""
    return await asyncio.to_thread(auth_db.get_top_users_by_usage, limit)

@app.get("/v6/admin/usage/users/{user_id}/endpoints", tags=["admin"])
async def get_admin_user_endpoints(
    user_id: str,
    limit: int = 10,
    _ = Depends(verify_admin)
):
    """Get endpoint breakdown for a specific user (Admin only)."""
    return await asyncio.to_thread(auth_db.get_user_endpoint_stats, user_id, limit)



# ============================================================================
# STARTUP EVENTS
# ============================================================================

# V6 startup handled by startup_v6_hybrid_architecture below

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Unified book mapping for odds endpoints (standard books + Lunosoft + EV sources)
book_map = dict(API_BOOK_MAP)
for book_key, streamer_cls in LUNOSOFT_BOOK_STREAMERS.items():
    book_map.setdefault(book_key, streamer_cls)
for book_key, streamer_cls in SHARP_ODDS_STREAMERS.items():
    book_map.setdefault(book_key, streamer_cls)
for source in DEFAULT_EV_SOURCES:
    book_map.setdefault(source, EV_SOURCES[source])


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] | None = None) -> str:
    """Create a signed JWT access token for dashboard sessions."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return token

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    return app

# ============================================================================
# API ENDPOINTS
# ============================================================================

from pydantic import BaseModel
from typing import Dict, Any, Optional

class GoogleAuthRequest(BaseModel):
    """Payload carrying the Google ID token from the frontend."""

    id_token: str


class DashboardSession(BaseModel):
    user_id: str
    email: Optional[str] = None


class APIKeyResponse(BaseModel):
    id: str
    name: Optional[str] = None
    key_type: str
    key_prefix: str
    status: str
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None


class APIKeyCreateRequest(BaseModel):
    name: Optional[str] = None
    key_type: str = "live"
    expires_in_days: Optional[int] = None


class APIKeyCreateResponse(APIKeyResponse):
    plain_key: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/v1/auth/google")
async def google_auth(payload: GoogleAuthRequest) -> Dict[str, Any]:
    """Exchange a Google ID token for a KashRock dashboard access token.

    Flow:
    - Verify the Google ID token against the configured GOOGLE_CLIENT_ID
    - Upsert a user in the control-plane auth DB (users table)
    - Return a short-lived JWT access token scoped for the dashboard
    """

    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(
            status_code=500,
            detail="Google client ID is not configured on the server",
        )

    # Verify ID token against Google's tokeninfo endpoint
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": payload.id_token},
            )
        if resp.status_code != 200:
            logger.warning(
                "Google tokeninfo returned non-200",
                status=resp.status_code,
                body=resp.text[:200],
            )
            raise HTTPException(status_code=401, detail="Invalid Google ID token")

        idinfo = resp.json()
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to verify Google ID token via tokeninfo", error=str(exc))
        raise HTTPException(status_code=401, detail="Invalid Google ID token")

    # Basic validation: audience and issuer
    aud = idinfo.get("aud")
    if aud != settings.google_client_id:
        logger.warning("Google ID token audience mismatch", aud=aud)
        raise HTTPException(status_code=401, detail="Invalid Google ID token audience")

    issuer = idinfo.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        logger.warning("Google ID token issuer mismatch", iss=issuer)
        raise HTTPException(status_code=401, detail="Invalid Google ID token issuer")

    email = idinfo.get("email") or idinfo.get("email_verified") and idinfo.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google token missing email")
    google_user_id = idinfo.get("sub")

    full_name = (
        idinfo.get("name")
        or (
            f"{idinfo.get('given_name', '')} {idinfo.get('family_name', '')}".strip()
            if idinfo.get("given_name") or idinfo.get("family_name")
            else None
        )
    )

    # Look up or create the user in the control-plane auth DB
    user = None
    if google_user_id:
        user = await user_service.get_user_by_google_id(google_user_id)
    if not user:
        user = await user_service.get_user_by_email(email)
    if not user:
        # Create a new user with a random password (never used directly)
        random_password = uuid4_fn().hex
        user = await user_service.create_user(
            email=email,
            password=random_password,
            plan="free",
            google_id=google_user_id,
            name=full_name,
        )
    else:
        # Ensure Google profile metadata is captured
        await user_service.update_profile(
            user["id"],
            google_id=google_user_id if not user.get("google_id") else None,
            name=full_name if full_name and not user.get("name") else None,
        )

    user_id = user["id"]

    # Issue a short-lived dashboard access token
    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_id, "email": email, "scope": "dashboard"},
        expires_delta=access_token_expires,
    )

    user_payload = {
        "id": user_id,
        "email": email,
        "name": full_name,
        "plan": user.get("plan", "free"),
        "status": user.get("status", "active"),
        "created_at": user.get("created_at"),
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_payload,
    }

@app.post("/v1/auth/login")
async def password_login(payload: LoginRequest) -> Dict[str, Any]:
    """Email + password login for the dashboard."""
    email = payload.email.lower()
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    is_valid = await asyncio.to_thread(
        auth_db.verify_password,
        payload.password,
        user.get("password_hash", ""),
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=get_settings().access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["id"], "email": user.get("email"), "scope": "dashboard"},
        expires_delta=access_token_expires,
    )
    keys = await api_key_service.list_keys_for_user(user["id"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user.get("email"),
            "name": user.get("name"),
            "plan": user.get("plan"),
            "status": user.get("status"),
            "created_at": user.get("created_at"),
            "key_count": len(keys),
        },
    }


def _require_dashboard_session(authorization: str | None) -> DashboardSession:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing dashboard session token")
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:].strip()
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError as exc:
        logger.warning("Invalid dashboard token", error=str(exc))
        raise HTTPException(status_code=401, detail="Invalid session token")
    if payload.get("scope") != "dashboard":
        raise HTTPException(status_code=403, detail="Invalid token scope")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return DashboardSession(user_id=user_id, email=payload.get("email"))


def _serialize_api_key(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record["id"],
        "name": record.get("name"),
        "key_type": record.get("key_type", "live"),
        "key_prefix": record.get("key_prefix", "")[:16],
        "status": record.get("status", "unknown"),
        "created_at": record.get("created_at"),
        "last_used_at": record.get("last_used_at"),
    }


def _start_time_for_range(range_value: str) -> datetime:
    now = datetime.utcnow()
    if range_value == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if range_value == "30days":
        return now - timedelta(days=30)
    return now - timedelta(days=7)


@app.get("/v1/dashboard/me")
async def dashboard_me(authorization: str | None = Header(default=None, alias="Authorization")) -> Dict[str, Any]:
    session = _require_dashboard_session(authorization)
    user = await user_service.get_user_by_id(session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    keys = await api_key_service.list_keys_for_user(session.user_id)
    return {
        "id": user["id"],
        "email": user.get("email"),
        "name": user.get("name"),
        "plan": user.get("plan"),
        "status": user.get("status"),
        "created_at": user.get("created_at"),
        "key_count": len(keys),
    }


@app.get(
    "/v1/dashboard/api-keys",
    response_model=list[APIKeyResponse],
)
async def dashboard_list_api_keys(
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    session = _require_dashboard_session(authorization)
    records = await api_key_service.list_keys_for_user(session.user_id)
    return [_serialize_api_key(record) for record in records]


@app.post(
    "/v1/dashboard/api-keys",
    response_model=APIKeyCreateResponse,
)
async def dashboard_create_api_key(
    payload: APIKeyCreateRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    session = _require_dashboard_session(authorization)
    key = await api_key_service.create_key(
        user_id=session.user_id,
        key_type=payload.key_type,
        name=payload.name,
        expires_in_days=payload.expires_in_days,
    )
    record = await api_key_service.get_key_by_id(key["id"])
    if not record:
        raise HTTPException(status_code=500, detail="Failed to create API key")
    serialized = _serialize_api_key(record)
    serialized["plain_key"] = key["plain_key"]
    return serialized


@app.post("/v1/dashboard/api-keys/{key_id}/revoke")
async def dashboard_revoke_api_key(
    key_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> Dict[str, str]:
    session = _require_dashboard_session(authorization)
    record = await api_key_service.get_key_by_id(key_id)
    if not record or record.get("user_id") != session.user_id:
        raise HTTPException(status_code=404, detail="API key not found")
    await api_key_service.deactivate_key(key_id)
    return {"status": "revoked"}


@app.delete("/v1/dashboard/api-keys/{key_id}")
async def dashboard_delete_api_key(
    key_id: str,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> Dict[str, str]:
    session = _require_dashboard_session(authorization)
    record = await api_key_service.get_key_by_id(key_id)
    if not record or record.get("user_id") != session.user_id:
        raise HTTPException(status_code=404, detail="API key not found")
    await api_key_service.delete_key(key_id)
    return {"status": "deleted"}


@app.get("/v1/dashboard/usage")
async def dashboard_usage(
    range: Literal["today", "7days", "30days"] = Query("7days"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    session = _require_dashboard_session(authorization)
    user = await user_service.get_user_by_id(session.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = await asyncio.to_thread(auth_db.get_plan, user.get("plan"))
    if not plan:
        plan = {"monthly_quota": 0, "rate_limit_per_min": 0}

    start_time = _start_time_for_range(range)
    breakdown = await usage_tracker.get_usage_breakdown(
        session.user_id,
        start_time,
    )
    usage_stats = await usage_tracker.get_usage_stats(session.user_id)
    total_requests = breakdown["summary"]["total_requests"]
    successful_requests = breakdown["summary"]["successful_requests"]
    error_requests = total_requests - successful_requests
    error_rate = (error_requests / total_requests * 100) if total_requests else 0.0

    endpoint_usage = [
        {
            "endpoint": item["endpoint"],
            "count": item["count"],
            "percentage": round((item["count"] / total_requests) * 100, 2) if total_requests else 0.0,
        }
        for item in breakdown["endpoints"]
    ]

    monthly_quota = int(plan.get("monthly_quota") or 0)
    monthly_used = usage_stats["total"]["requests"]
    requests_remaining = max(monthly_quota - monthly_used, 0) if monthly_quota else 0
    daily_limit = monthly_quota // 30 if monthly_quota else plan.get("rate_limit_per_min", 0)

    recent_requests = [
        {
            "id": log["id"],
            "timestamp": log["requested_at"],
            "endpoint": log["endpoint"],
            "method": log.get("method") or "GET",
            "statusCode": log.get("status_code", 0),
            "latency": log.get("latency_ms"),
            "keyId": log.get("key_id"),
            "keyPreview": log.get("key_preview"),
            "creditsUsed": log.get("credits_used"),
        }
        for log in breakdown["logs"]
    ]

    return {
        "range": range,
        "metrics": {
            "totalRequests": total_requests,
            "successfulRequests": successful_requests,
            "errorRate": error_rate,
            "tier": user.get("plan", "unknown"),
            "requestsRemaining": requests_remaining,
            "dailyLimit": daily_limit,
            "monthlyQuota": monthly_quota,
        },
        "endpointUsage": endpoint_usage,
        "recentRequests": recent_requests,
    }


# ============================================================================
# PUBLIC API KEY GENERATION (NO AUTH REQUIRED)
# ============================================================================

class PublicKeyRequest(BaseModel):
    """Request to generate a public API key without authentication"""
    name: Optional[str] = "My API Key"
    email: Optional[str] = None

@app.post("/v1/public/generate-key")
async def public_generate_key(payload: PublicKeyRequest) -> Dict[str, Any]:
    """
    Generate an API key without requiring authentication.
    This creates an anonymous user and returns a live API key.
    """
    # Create an anonymous user
    anonymous_email = payload.email or f"anon_{uuid4_fn().hex[:12]}@kashrock.local"
    random_password = uuid4_fn().hex
    
    # Check if user already exists
    user = await user_service.get_user_by_email(anonymous_email)
    if not user:
        user = await user_service.create_user(
            email=anonymous_email,
            password=random_password,
            plan="free",
            name=payload.name or "Anonymous User"
        )
    
    # Generate API key
    key = await api_key_service.create_key(
        user_id=user["id"],
        key_type="live",
        name=payload.name or "My API Key",
        expires_in_days=None  # No expiration
    )
    
    return {
        "success": True,
        "api_key": key["plain_key"],
        "key_prefix": key["plain_key"][:16],
        "message": "API key generated successfully. Save this key - it won't be shown again!",
        "docs_url": "/docs"
    }

@app.get("/v1/books")
async def get_books() -> Dict[str, Any]:
    """
    Get the status of all sportsbooks available in V6.
    
    Returns all available sportsbooks and KashRock EV sources.
    """
    books = []
    
    # Add all available sportsbooks dynamically
    for book_key, streamer_class in LUNOSOFT_BOOK_STREAMERS.items():
        books.append({
            "name": book_key,
            "book_id": streamer_class.BOOK_ID,
            "book_name": streamer_class.BOOK_NAME,
            "status": "active",
            "sports": ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"],
            "type": "sportsbook",
            "source": "kashrock"
        })

    for book_key, streamer_class in SHARP_ODDS_STREAMERS.items():
        books.append({
            "name": book_key,
            "book_id": streamer_class.BOOK_ID,
            "book_name": streamer_class.BOOK_NAME,
            "status": "active",
            "sports": ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"],
            "type": "sportsbook",
            "source": "sharp"
        })
    
    walter_data = await get_walter_books()
    for book in walter_data['books']:
        books.append({
            "name": book,
            "status": "active",
            "sports": walter_data['sports'],
            "type": "sportsbook",
            "source": "kashrock"
        })
    
    rotowire_data = await get_rotowire_books()
    for book in rotowire_data['books']:
        books.append({
            "name": book,
            "status": "active",
            "sports": rotowire_data['sports'],
            "type": "sportsbook",
            "source": "kashrock"
        })
    
    proply_data = await get_proply_books()
    for book in proply_data['books']:
        books.append({
            "name": book,
            "status": "active",
            "sports": proply_data['sports'],
            "type": "sportsbook",
            "source": "kashrock"
        })
    
    # Add KashRock EV sources as metadata
    for source_key in DEFAULT_EV_SOURCES:
        books.append({
            "name": source_key,
            "status": "active",
            "sports": ["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"],
            "type": "ev_source",
            "source": "kashrock"
        })
    
    # Deduplicate books (some appear in multiple EV sources)
    unique_books = []
    seen_books = set()
    for book in books:
        book_key = (book["name"], book["source"])
        if book_key not in seen_books:
            seen_books.add(book_key)
            unique_books.append(book)
    
    return {
        "books": unique_books,
        "total_books": len(unique_books),
        "sportsbooks": len(LUNOSOFT_BOOK_STREAMERS),
        "ev_sources": len(DEFAULT_EV_SOURCES),
        "walter_books": len(walter_data['books']),
        "rotowire_books": len(rotowire_data['books']),
        "proply_books": len(proply_data['books']),
        "walter_sports": walter_data['sports'],
        "rotowire_sports": rotowire_data['sports'],
        "proply_sports": proply_data['sports'],
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/v1/odds/upcoming")
async def get_upcoming_odds(
    sport: str = Query(..., description="Sport to get odds for"),
    books: str = Query(..., description="Comma-separated list of books"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Get upcoming odds for a specific sport and books.
    """
    # Validate API key
    if not validate_api_key(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    # Parse books
    book_list = [book.strip() for book in books.split(",")]
    
    
    results = {}
    
    for book_name in book_list:
        try:
            if book_name not in book_map:
                results[book_name] = {
                    "status": "error",
                    "error": f"Unknown book: {book_name}",
                    "data": [],
                    "sport": sport,
                    "book": book_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
                continue
                
            streamer_class = book_map[book_name]
            
            # Dabble needs specific configuration
            if book_name == "dabble":
                config = {
                    "sport": sport,
                    "market_groups": [],  # Will auto-discover
                    "limit": 5000
                }
                streamer = streamer_class(f"dabble_{sport}", config)
            else:
                # Default config for other streamers
                config = {"sport": sport}
                streamer = streamer_class(f"{book_name}_{sport}", config)
            
            # Connect and fetch real data
            await streamer.connect()
            raw_data = await streamer.fetch_data()
            await streamer.disconnect()

            results[book_name] = {
                "status": "success",
                "data": raw_data,
                "sport": sport,
                "book": book_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            results[book_name] = {
                "status": "error",
                "error": str(e),
                "data": [],
                "sport": sport,
                "book": book_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return {
        "sport": sport,
        "books": book_list,
        "results": results,
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the API key generation page.
    """
    html_path = Path(__file__).parent / "public" / "generate-key.html"
    if html_path.exists():
        return FileResponse(html_path)
    else:
        return HTMLResponse("""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>KashRock API</h1>
                <p>Version 1.0.0</p>
                <p><a href="/docs">API Documentation</a></p>
                <p><a href="/v1/public/generate-key">Generate API Key (JSON)</a></p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# ----------------------------------------------------------------------------
# Backward-compatible aliases for old /v1 paths → call router handlers directly
# ----------------------------------------------------------------------------

# Legacy endpoints removed - use v4 API instead

# Admin endpoints for API key management
@app.get("/admin/keys")
async def list_api_keys(
    authorization: str | None = Header(default=None, alias="Authorization")
):
    """
    List all API keys (admin only).
    """
    # Check if this is an admin key
    key_info = get_api_key_info(authorization)
    if not key_info or key_info.name != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    keys = api_key_manager.list_keys()
    return {
        "keys": [
            {
                "name": key.name,
                "status": key.status.value,
                "created_at": key.created_at.isoformat(),
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "last_used": key.last_used.isoformat() if key.last_used else None,
                "usage_count": key.usage_count,
                "rate_limit": key.rate_limit,
                "notes": key.notes
            }
            for key in keys
        ]
    }

@app.post("/admin/keys/generate")
async def generate_api_key(
    name: str,
    rate_limit: int = 1000,
    expires_days: int = 30,
    authorization: str | None = Header(default=None, alias="Authorization")
):
    """
    Generate a new API key (admin only).
    """
    # Check if this is an admin key
    key_info = get_api_key_info(authorization)
    if not key_info or key_info.name != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    key = api_key_manager.generate_key(name, rate_limit, expires_days)
    
    return {
        "message": "API key generated successfully",
        "name": name,
        "key": key,
        "rate_limit": rate_limit,
        "expires_days": expires_days
    }

# Duplicate props and health endpoints have been removed from this file.
# Use the unified router endpoints under /api/v1 from src/api/odds.py

# ============================================================================
# V6 HYBRID ARCHITECTURE STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_v6_hybrid_architecture():
    """Initialize V6 hybrid architecture components."""
    print("[V6] Starting V6 hybrid architecture...")
    logger = structlog.get_logger()
    
    try:
        print("[V6] Initializing Redis connection pool...")
        logger.info("Starting V6 hybrid architecture...")
        
        # Initialize Redis connection pool
        redis_pool = await get_redis_pool()
        if not redis_pool.is_connected:
            print("[V6] Failed to connect to Redis pool")
            logger.error("Failed to connect to Redis pool")
            return
        
        print("[V6] Redis pool connected successfully")
        
        # Initialize cache manager
        print("[V6] Initializing cache manager...")
        cache_manager = await get_cache_manager()
        if not cache_manager._connected:
            print("[V6] Failed to initialize cache manager")
            logger.error("Failed to initialize cache manager")
            return
        
        print("[V6] Cache manager initialized successfully")
        
        # Initialize historical database for persistent storage
        from config import get_settings
        settings = get_settings()
        if settings.enable_historical_database:
            print("[V6] Initializing historical database...")
            from v6.historical.database import get_historical_db
            historical_db = await get_historical_db()
            if historical_db._connected:
                print("[V6] Historical database connected successfully")
                logger.info("Historical database initialized for persistent odds storage")
            else:
                print("[V6] Warning: Historical database connection failed - continuing without persistence")
                logger.warning("Historical database unavailable - data will only be cached in Redis")
        else:
            print("[V6] Historical database disabled - skipping initialization")
            logger.info("Historical database disabled - data will only be cached in Redis")
        
        # Start background worker with all lunosoft books
        print("[V6] Starting background worker...")
        from streamers.lunosoft_books import LUNOSOFT_BOOK_STREAMERS
        active_books = list(LUNOSOFT_BOOK_STREAMERS.keys())
        print(f"[V6] Found {len(active_books)} books to initialize")
        
        worker = await start_background_worker(
            cache_manager=cache_manager,
            active_books=active_books,
            poll_interval=15.0,
            sports=["americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl"]
        )
        
        if not worker._running:
            print("[V6] Failed to start V6 background worker")
            logger.error("Failed to start V6 background worker")
            return
        
        print("[V6] Background worker started successfully")
        
    except Exception as exc:
        logger.error("Failed to start V6 hybrid architecture", error=str(exc), exc_info=True)


@app.on_event("shutdown")
async def shutdown_v6_hybrid_architecture():
    """Shutdown V6 hybrid architecture components."""
    logger = structlog.get_logger()
    
    try:
        logger.info("Shutting down V6 hybrid architecture...")
        
        # Stop background worker
        await stop_background_worker()
        
        # Shutdown historical database
        from v6.historical.database import shutdown_historical_db
        await shutdown_historical_db()
        logger.info("Historical database shutdown complete")
        
        # Shutdown cache manager
        await shutdown_cache_manager()
        
        # Shutdown Redis pool
        await shutdown_redis_pool()
        
        logger.info("V6 hybrid architecture shutdown complete")
        
    except Exception as exc:
        logger.error("Error during V6 shutdown", error=str(exc), exc_info=True)

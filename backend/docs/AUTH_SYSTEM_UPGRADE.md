# KashRock API - Production Auth System Upgrade

## Current State Snapshot

### Strengths
- API key concept already in place (`kr_` keys)
- Admin endpoints to list/generate keys
- Redis is available for rate limiting / quota storage
- Structlog logging in project for observability

### Gaps
1. Keys live in memory/env only (lost on restart)
2. No persistent users or plans (no billing surface)
3. No per-request usage/rate enforcement (only stored metadata)
4. Keys stored as plain text (no hashing)
5. No test vs live separation
6. No monthly quota tracking
7. No key rotation/revocation capabilities beyond in-memory toggle

---

## Target Architecture

```
┌─────────────────────────────────────────┐
│            Control Plane                │
│  (auth.kashrock)                        │
│                                         │
│  • Users & authentication               │
│  • API key issuance & hashing           │
│  • Plan/quota definitions               │
│  • Usage + billing ledger               │
│  • Rate-limit counters                  │
└─────────────────────────────────────────┘
                 │ validates
                 ▼
┌─────────────────────────────────────────┐
│             Data Plane                  │
│  (api.kashrock)                         │
│                                         │
│  • Odds / props endpoints               │
│  • Background ingest workers            │
│  • Caches / canonicalization            │
└─────────────────────────────────────────┘
```

Keep auth separate so the data plane stays stateless and fast.

---

## Data Model (SQLite → PostgreSQL ready)

```sql
-- Users
CREATE TABLE users (
    id TEXT PRIMARY KEY,                -- uuid4
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'free',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plans
CREATE TABLE plans (
    id TEXT PRIMARY KEY,
    monthly_quota INTEGER NOT NULL,
    rate_limit_per_min INTEGER NOT NULL,
    price_monthly REAL NOT NULL,
    metadata JSON
);

INSERT INTO plans VALUES
    ('free',     1000,   10,   0.00,  '{"label":"Free"}'),
    ('starter', 10000,  100,  49.00, '{"label":"Starter"}'),
    ('pro',    100000,  500, 199.00, '{"label":"Pro"}');

-- API Keys
CREATE TABLE api_keys (
    id TEXT PRIMARY KEY,                 -- uuid4
    user_id TEXT NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,       -- SHA-256 hash
    key_prefix TEXT NOT NULL,            -- exposed first 8 chars (kr_live_...)
    key_type TEXT NOT NULL,              -- 'test' | 'live'
    status TEXT NOT NULL DEFAULT 'active',
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- Usage (immutable log)
CREATE TABLE usage_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    api_key_id TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    credits_used INTEGER NOT NULL DEFAULT 1,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
);
CREATE INDEX idx_usage_logs_user_time ON usage_logs(user_id, requested_at DESC);

-- Monthly aggregates for quick checks
CREATE TABLE monthly_usage (
    user_id TEXT NOT NULL,
    key_type TEXT NOT NULL,
    year_month TEXT NOT NULL,
    requests INTEGER NOT NULL DEFAULT 0,
    credits INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, key_type, year_month)
);
```

---

## Core Control Plane Services

### 1. User Service (`src/control_plane/users.py`)
- Create/activate/suspend users
- Hash passwords (use `bcrypt`)
- Assign plans

### 2. API Key Service (`src/control_plane/api_keys.py`)
- Generate keys (uuid4 → prefix):
  ```python
  raw_token = secrets.token_urlsafe(32)
  key = f"kr_{key_type}_{raw_token}"  # kr_live_xxx, kr_test_xxx
  key_hash = hashlib.sha256(key.encode()).hexdigest()
  ```
- Store only `key_hash`
- Return plain key once
- Rotate / revoke keys

### 3. Usage Service (`src/control_plane/usage.py`)
- `log_usage(user_id, api_key_id, endpoint, credits)`
- `increment_monthly(user_id, key_type, credits)` (Redis counter → nightly flush)

### 4. Rate Limiter (`src/control_plane/rate_limit.py`)
- Redis keys: `rl:{api_key_id}:{yyyyMMddHHmm}`
- Increment per request
- Compare to plan limit
- Return 429 if exceeded

---

## API Layer Integration

### Middleware Flow
1. Extract API key from `Authorization: Bearer <key>`
2. Hash and look up `api_keys.key_hash`
3. Join with `users` & `plans`
4. Check status/plan/limits (Redis)
5. Record usage
6. Pass request to endpoint

```python
# src/middleware/auth.py
async def auth_middleware(request: Request, call_next):
    key = extract_key(request.headers)
    api_key = await key_service.resolve_key(key)
    if not api_key:
        raise HTTPException(401, "Invalid API key")
    
    await rate_limiter.enforce(api_key)
    response = await call_next(request)
    await usage_logger.record(api_key, request, response.status_code)
    return response
```

### FastAPI Wiring
```python
app.middleware("http")(auth_middleware)
```

Skip middleware for `/health`, `/docs`, `/openapi.json`, `/admin/login`.

---

## Minimal Implementation Checklist (1 week)

- [ ] Create `data/auth.db` via Alembic migration
- [ ] `src/db/auth_db.py` with connection helpers
- [ ] `src/control_plane/users.py` (CRUD)
- [ ] `src/control_plane/api_keys.py` (generate/hash/lookup)
- [ ] `src/control_plane/usage.py` (Redis + SQLite)
- [ ] `src/control_plane/rate_limit.py` (Redis counters)
- [ ] `src/middleware/auth.py` (FastAPI middleware)
- [ ] Update `/admin/keys` endpoints to hit new control plane
- [ ] CLI scripts: `python manage_keys.py --create-user --generate-key`

---

## Operational Notes

- **Redis TTL**: set rate-limit keys to expire after 2 minutes
- **Quota Counter**: `quota:{user_id}:{YYYYMM}` → increment credits, flush nightly
- **Key Revocation**: mark `api_keys.status = 'revoked'` → middleware rejects instantly
- **Environment Separation**: maintain separate databases for staging vs prod
- **Monitoring**: expose `/metrics` gauge for requests per plan/user
- **Billing Hook**: export monthly usage → Stripe metered billing
- **Rotation**: allow multiple active keys per user to avoid downtime

---

## Next Steps

1. Implement schema & services above (start with SQLite → migrate to Postgres later)
2. Refactor FastAPI auth to route through control-plane helpers
3. Add admin UI/CLI to manage users, keys, and plans
4. Instrument usage dashboards & alerts

This gives KashRock the same control-plane discipline real API platforms rely on, without blocking shipping odds features.

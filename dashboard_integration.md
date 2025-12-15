# KashRock Dashboard Integration Guide

This document describes how to integrate the KashRock frontend dashboard (www.kashrock.com) with the backend API (api.kashrock.com).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                            │
│                   www.kashrock.com                              │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ Google      │    │ Dashboard   │    │ API Key     │        │
│  │ Sign-In     │───▶│ UI          │───▶│ Management  │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                  │                  │                │
│         ▼                  ▼                  ▼                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Supabase Auth (JWT)                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Authorization: Bearer <supabase_jwt>
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Railway)                            │
│                   api.kashrock.com                              │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ JWT         │    │ /v1/dev/*   │    │ /v6/*       │        │
│  │ Verification│───▶│ Dashboard   │    │ Data APIs   │        │
│  └─────────────┘    │ Endpoints   │    └─────────────┘        │
│                     └─────────────┘           │                │
│                            │                  │                │
│                            ▼                  ▼                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              SQLite / Supabase Postgres                 │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Environment Variables

### Backend (Railway)

Add these to your Railway environment:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase-dashboard

# API Key Hashing (optional pepper for extra security)
API_KEY_HASH_SECRET=your-random-pepper-string

# CORS (automatically configured, but can override)
CORS_ORIGINS=https://www.kashrock.com,https://kashrock.com,http://localhost:3000
```

### Frontend (Vercel)

Add these to your Vercel environment:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Backend API
NEXT_PUBLIC_API_BASE_URL=https://api.kashrock.com
```

## API Endpoints

### Developer Dashboard Endpoints (`/v1/dev/*`)

All endpoints require Supabase JWT authentication:
```
Authorization: Bearer <supabase_access_token>
```

#### Create API Key
```bash
POST /v1/dev/api-keys
Content-Type: application/json
Authorization: Bearer <supabase_jwt>

{
  "name": "My Production Key"  // optional
}

# Response (200 OK)
{
  "id": "uuid",
  "name": "My Production Key",
  "api_key": "kr_live_abc123...",  // ONLY shown once!
  "key_prefix": "kr_live_abc1",
  "tier": "tester_free",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### List API Keys
```bash
GET /v1/dev/api-keys
Authorization: Bearer <supabase_jwt>

# Response (200 OK)
{
  "keys": [
    {
      "id": "uuid",
      "name": "My Production Key",
      "key_prefix": "kr_live_abc1",
      "status": "active",
      "tier": "tester_free",
      "created_at": "2025-01-01T00:00:00Z",
      "last_used_at": "2025-01-02T12:00:00Z"
    }
  ]
}
```

#### Revoke API Key
```bash
POST /v1/dev/api-keys/{key_id}/revoke
Authorization: Bearer <supabase_jwt>

# Response (200 OK)
{
  "id": "uuid",
  "status": "revoked",
  "message": "API key has been revoked and will no longer work"
}
```

#### Get Usage Summary
```bash
GET /v1/dev/usage/summary?range=7d
Authorization: Bearer <supabase_jwt>

# Response (200 OK)
{
  "total_requests": 1234,
  "error_count": 12,
  "error_rate": 0.97,
  "top_endpoints": [
    {"endpoint": "/v6/odds", "count": 500},
    {"endpoint": "/v6/props/basketball_nba", "count": 300}
  ],
  "requests_per_day": [
    {"date": "2025-01-01", "requests": 100},
    {"date": "2025-01-02", "requests": 150}
  ],
  "range": "7d"
}
```

#### Get Profile
```bash
GET /v1/dev/profile
Authorization: Bearer <supabase_jwt>

# Response (200 OK)
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://...",
  "tier": "tester_free",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### Health Check (no auth required)
```bash
GET /v1/dev/health

# Response (200 OK)
{
  "status": "healthy",
  "service": "kashrock-dev-api",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Frontend Integration

### 1. Supabase Auth Setup

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

### 2. Google Sign-In

```typescript
// Sign in with Google
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: `${window.location.origin}/auth/callback`
  }
})
```

### 3. API Client

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.kashrock.com'

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session?.access_token) {
    throw new Error('Not authenticated')
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'API request failed')
  }
  
  return response.json()
}

// Usage
const keys = await apiClient<ListKeysResponse>('/v1/dev/api-keys')
const newKey = await apiClient<CreateKeyResponse>('/v1/dev/api-keys', {
  method: 'POST',
  body: JSON.stringify({ name: 'My Key' })
})
```

## Testing with cURL

### 1. Get Supabase JWT (from browser dev tools)

After signing in on the frontend, get the access token from:
- Browser DevTools → Application → Local Storage → `sb-<project>-auth-token`
- Or from `supabase.auth.getSession()` in console

### 2. Test Endpoints

```bash
# Set your token
export SUPABASE_JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Health check (no auth)
curl https://api.kashrock.com/v1/dev/health

# Create API key
curl -X POST https://api.kashrock.com/v1/dev/api-keys \
  -H "Authorization: Bearer $SUPABASE_JWT" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key"}'

# List keys
curl https://api.kashrock.com/v1/dev/api-keys \
  -H "Authorization: Bearer $SUPABASE_JWT"

# Get usage
curl "https://api.kashrock.com/v1/dev/usage/summary?range=7d" \
  -H "Authorization: Bearer $SUPABASE_JWT"

# Revoke key
curl -X POST https://api.kashrock.com/v1/dev/api-keys/{key_id}/revoke \
  -H "Authorization: Bearer $SUPABASE_JWT"
```

### 3. Test API Key Usage

```bash
# Use the generated API key to call data endpoints
export API_KEY="kr_live_abc123..."

curl "https://api.kashrock.com/v6/odds?sport=basketball_nba" \
  -H "x-api-key: $API_KEY"
```

## Acceptance Tests

1. ✅ Sign in on Vercel with Google → user row exists in database
2. ✅ Create key from dashboard → key stored hashed; plaintext shown once
3. ✅ Call a real endpoint with x-api-key → returns data and logs usage
4. ✅ Dashboard usage endpoint shows increasing counts after calls
5. ✅ Revoke key → subsequent API calls fail with 401
6. ✅ CORS preflight works from Vercel origin

## Security Notes

- API keys are stored as SHA256 hashes (never plaintext)
- Plaintext key is shown only once at creation
- Keys can be revoked but not recovered
- Rate limiting: 5 keys per user maximum
- Supabase JWT verification uses the project's JWT secret
- CORS is configured to only allow specific origins

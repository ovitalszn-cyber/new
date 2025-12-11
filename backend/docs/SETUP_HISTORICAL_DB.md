# Historical Database Setup Guide

## Quick Start

The `/v6/stats` endpoint is working and showing cache statistics. To enable **persistent historical odds storage**, follow these steps:

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE kashrock_stream;
CREATE USER kashrock WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE kashrock_stream TO kashrock;

# Exit
\q
```

### 3. Configure Environment

Create or update `.env` file:

```bash
# Redis (already configured)
REDIS_URL=redis://localhost:6379/0

# PostgreSQL for historical data
DATABASE_URL=postgresql+asyncpg://kashrock:your_secure_password@localhost/kashrock_stream
```

### 4. Restart Server

```bash
# The server will automatically:
# 1. Connect to PostgreSQL
# 2. Create historical_odds and historical_player_props tables
# 3. Start persisting all odds data

# Restart your server
# Tables will be created automatically on first startup
```

### 5. Verify It's Working

Check server logs for:
```
[V6] Initializing historical database...
[V6] Historical database connected successfully
```

Check PostgreSQL:
```bash
psql kashrock_stream -c "SELECT COUNT(*) FROM historical_odds;"
psql kashrock_stream -c "SELECT COUNT(*) FROM historical_player_props;"
```

## Optional: TimescaleDB for Better Performance

For large-scale historical data, install TimescaleDB extension:

```bash
# macOS
brew install timescaledb

# Ubuntu
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update
sudo apt-get install timescaledb-postgresql-15

# Enable extension
psql kashrock_stream -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

# Convert to hypertables
psql kashrock_stream -c "SELECT create_hypertable('historical_odds', 'captured_at', if_not_exists => TRUE);"
psql kashrock_stream -c "SELECT create_hypertable('historical_player_props', 'captured_at', if_not_exists => TRUE);"
```

## What Happens Now

### Without PostgreSQL (Current State)
- ✅ `/v6/stats` endpoint works (shows cache stats)
- ✅ `/v6/player_props` endpoint works (real-time data from Redis)
- ✅ `/v6/spreads` endpoint works (real-time data from Redis)
- ⚠️ Data is **only in Redis** (cleared every 30-60 seconds)
- ❌ No historical data persistence

### With PostgreSQL (After Setup)
- ✅ All endpoints continue working
- ✅ **Every odds snapshot saved to PostgreSQL**
- ✅ **Historical data never cleared**
- ✅ Can query line movements, historical props, etc.
- ✅ Build ML models on historical data

## Current Stats Endpoint

The `/v6/stats` endpoint shows:

```json
{
    "metrics": {
        "last_update": "2025-12-06T18:31:08.066225+00:00",
        "events_processed": 12,
        "sport": "icehockey_nhl",
        "active_books": 38
    },
    "events_by_sport": {
        "americanfootball_nfl": 270,
        "basketball_nba": 96,
        "baseball_mlb": 0,
        "icehockey_nhl": 12
    },
    "total_events": 378,
    "timestamp": "2025-12-06T18:33:03.492518+00:00"
}
```

This shows **real-time cache statistics**. Once PostgreSQL is set up, this same data will also be persisted historically.

## Testing Historical Data

After running for a few hours with PostgreSQL configured:

```sql
-- See how many odds snapshots you've collected
SELECT 
    sport,
    COUNT(*) as snapshot_count,
    COUNT(DISTINCT event_id) as unique_events,
    MIN(captured_at) as first_capture,
    MAX(captured_at) as last_capture
FROM historical_odds
GROUP BY sport;

-- See player props history
SELECT 
    sport,
    COUNT(*) as prop_count,
    COUNT(DISTINCT player_name) as unique_players,
    COUNT(DISTINCT stat_type) as stat_types
FROM historical_player_props
GROUP BY sport;

-- Line movement example
SELECT 
    captured_at,
    book_name,
    market_data->>'value' as line,
    market_data->>'over_odds' as odds
FROM historical_odds
WHERE event_id LIKE '%_nfl_%'
    AND market_type = 'spread'
ORDER BY captured_at DESC
LIMIT 50;
```

## Architecture Summary

```
Background Worker (polls every 30s)
    ↓
    ├─→ Redis Cache (ephemeral, TTL 1 hour)
    │   └─→ API Endpoints (/v6/stats, /v6/player_props, etc.)
    │
    └─→ PostgreSQL (persistent, never cleared)
        └─→ Historical Analysis, ML Training, Line Movement Tracking
```

## Troubleshooting

**Database connection fails:**
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Check logs for connection errors

**Tables not created:**
- Tables are created automatically on first startup
- Check server logs for errors
- Manually create if needed (see `v6/historical/database.py`)

**No data in historical tables:**
- Verify `DATABASE_URL` is set correctly
- Check server logs for "Stored event in historical database"
- Ensure PostgreSQL is running and accessible

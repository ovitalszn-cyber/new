# Dual Database Architecture for KashRock V6

## Overview

KashRock V6 now uses **two separate storage systems** to handle different data persistence needs:

### 1. **Redis Cache** (Ephemeral, Real-Time)
- **Purpose**: Fast, real-time odds delivery to API clients
- **Behavior**: Data gets cleared and refreshed every 30-60 seconds
- **TTL**: 1 hour (3600 seconds)
- **Location**: `redis://localhost:6379/0`
- **Use Case**: Serving live odds via `/v6/player_props`, `/v6/spreads`, etc.

### 2. **PostgreSQL/TimescaleDB** (Persistent, Historical)
- **Purpose**: Long-term storage for historical odds analysis
- **Behavior**: Append-only, never cleared
- **Location**: Configured via `DATABASE_URL` in `.env`
- **Use Case**: Building historical odds database, analytics, ML training data

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  V6 Background Worker                        │
│                                                              │
│  1. Fetch odds from Lunosoft (38 books)                    │
│  2. Fetch player props from Lunosoft                        │
│  3. Fetch EV data from Walter & Action Network             │
│  4. Normalize and merge data                                │
│                                                              │
│  5. DUAL STORAGE:                                           │
│     ┌──────────────────┐      ┌──────────────────┐        │
│     │  Redis Cache     │      │  PostgreSQL DB   │        │
│     │  (Ephemeral)     │      │  (Persistent)    │        │
│     │                  │      │                  │        │
│     │  • Live odds     │      │  • Historical    │        │
│     │  • TTL: 1 hour   │      │  • Append-only   │        │
│     │  • Cleared       │      │  • Never cleared │        │
│     │    regularly     │      │  • Timestamped   │        │
│     └──────────────────┘      └──────────────────┘        │
│            │                           │                    │
└────────────┼───────────────────────────┼────────────────────┘
             │                           │
             ▼                           ▼
      ┌─────────────┐           ┌──────────────┐
      │  API Clients│           │  Analytics   │
      │  (Live Data)│           │  (Historical)│
      └─────────────┘           └──────────────┘
```

## Database Schema

### Historical Odds Table
```sql
CREATE TABLE historical_odds (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sport VARCHAR(100) NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    commence_time TIMESTAMPTZ,
    book_name VARCHAR(100) NOT NULL,
    book_id INTEGER,
    market_type VARCHAR(50) NOT NULL,  -- 'spread', 'total', 'moneyline'
    market_data JSONB NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'kashrock'
);
```

### Historical Player Props Table
```sql
CREATE TABLE historical_player_props (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sport VARCHAR(100) NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    game_id INTEGER,
    player_name VARCHAR(255) NOT NULL,
    player_team VARCHAR(100),
    stat_type VARCHAR(100) NOT NULL,  -- 'Passing Yards', 'Rushing TD', etc.
    stat_value DECIMAL(10, 2),
    direction VARCHAR(20),  -- 'over', 'under'
    odds INTEGER,
    book_name VARCHAR(100) NOT NULL,
    book_id INTEGER,
    sportsbook_id INTEGER,
    prop_data JSONB NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'kashrock'
);
```

## Key Benefits

### ✅ **Separation of Concerns**
- Redis: Optimized for speed, low latency API responses
- PostgreSQL: Optimized for complex queries, historical analysis

### ✅ **No Data Loss**
- Clearing Redis cache no longer loses historical data
- Every odds snapshot is permanently stored in PostgreSQL

### ✅ **Historical Analysis**
- Query odds movements over time
- Build ML models on historical data
- Track book accuracy and line movements

### ✅ **Scalability**
- Redis can be cleared/refreshed without affecting historical data
- PostgreSQL can use TimescaleDB for efficient time-series queries

## Configuration

### Environment Variables
```bash
# Redis (ephemeral cache)
REDIS_URL=redis://localhost:6379/0

# PostgreSQL (persistent historical data)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/kashrock_stream
```

### Optional: TimescaleDB Enhancement
For better time-series performance, convert tables to hypertables:

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert to hypertables
SELECT create_hypertable('historical_odds', 'captured_at', if_not_exists => TRUE);
SELECT create_hypertable('historical_player_props', 'captured_at', if_not_exists => TRUE);
```

## Usage Examples

### Query Historical Odds Movement
```sql
-- Get DraftKings spread movement for a specific game
SELECT 
    captured_at,
    market_data->>'value' as spread_value,
    market_data->>'over_odds' as home_odds,
    market_data->>'under_odds' as away_odds
FROM historical_odds
WHERE 
    book_name = 'draftkings'
    AND event_id = 'americanfootball_nfl_det_gb_2025-11-27'
    AND market_type = 'spread'
ORDER BY captured_at DESC
LIMIT 100;
```

### Query Player Prop History
```sql
-- Get Jared Goff passing yards prop history across all books
SELECT 
    captured_at,
    book_name,
    stat_value,
    direction,
    odds
FROM historical_player_props
WHERE 
    player_name = 'Jared Goff'
    AND stat_type = 'Passing Yards'
    AND captured_at > NOW() - INTERVAL '7 days'
ORDER BY captured_at DESC, book_name;
```

### Analyze Line Movement
```sql
-- Find games with significant line movement
SELECT 
    event_id,
    home_team,
    away_team,
    book_name,
    MIN(CAST(market_data->>'value' AS DECIMAL)) as opening_line,
    MAX(CAST(market_data->>'value' AS DECIMAL)) as closing_line,
    MAX(CAST(market_data->>'value' AS DECIMAL)) - 
        MIN(CAST(market_data->>'value' AS DECIMAL)) as line_movement
FROM historical_odds
WHERE 
    market_type = 'spread'
    AND captured_at > NOW() - INTERVAL '1 day'
GROUP BY event_id, home_team, away_team, book_name
HAVING ABS(MAX(CAST(market_data->>'value' AS DECIMAL)) - 
           MIN(CAST(market_data->>'value' AS DECIMAL))) > 2.0
ORDER BY line_movement DESC;
```

## Implementation Status

✅ **Completed:**
- Historical database module (`v6/historical/database.py`)
- Dual storage in background worker
- PostgreSQL schema with indexes
- Automatic persistence alongside Redis caching

🔄 **Next Steps:**
1. Set up PostgreSQL database
2. Configure `DATABASE_URL` in `.env`
3. Optional: Install TimescaleDB for better performance
4. Build analytics endpoints to query historical data

## Performance Considerations

- **Redis**: ~1ms latency for API responses
- **PostgreSQL**: Bulk inserts every 30 seconds (non-blocking)
- **Storage**: ~1KB per odds snapshot, ~500 bytes per player prop
- **Estimated Growth**: ~50GB/year for 38 books × 4 sports × continuous polling

## Monitoring

The background worker logs both storage operations:
```
[INFO] Successfully stored event in Redis
[DEBUG] Stored event in historical database
```

Monitor PostgreSQL table sizes:
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'historical_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

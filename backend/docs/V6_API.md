# KashRock V6 API Reference

This document describes all V6 API endpoints implemented under `v6/` and how they are mounted in `main.py`. It is intended as an engineering-facing reference.

> **Base URL:** `http://<host>:<port>`

## Router Mounting

Routers are wired in `main.py` as follows:

- `v6.api.cached.router` → `app.include_router(v6_cached_router)` → **base path `/v6`**
- `v6.api.stats.router` → `app.include_router(v6_stats_router, prefix="/v6")`
- `v6.api.odds.router` → `app.include_router(v6_odds_router, prefix="/v6")`
- `v6.api.unified.router` → `app.include_router(v6_unified_router)` (router has internal prefix `/v6`)
- `v6.api.export.router` → `app.include_router(v6_export_router)` (router has internal prefix `/v6`)
- `v6.api.production.router` exists but is **not mounted** in `main.py` as of this doc.

**Auth patterns:**

- Many cached endpoints in `v6.api.cached` require a KashRock API key via `Authorization: Bearer <api_key>` and call `auth.validate_api_key`.
- `v6.api.production` uses FastAPI `HTTPBearer`; currently any non-empty token is accepted (placeholder for real auth).

---

## 1. V6 Cached API (`v6.api.cached`, prefix `/v6`)

Redis-backed, background-worker-populated endpoints.

### 1.1 Root

**GET `/v6/`**

- **Auth:** None.
- **Description:** Returns metadata about the V6 cached "News Agency" architecture: version, components, primary endpoints, monitoring endpoints, benefits.

### 1.2 Event Discovery & Retrieval

**GET `/v6/event/{canonical_event_id}`**

- **Auth:** API key.
- **Path params:**
  - `canonical_event_id` – KashRock canonical event identifier.
- **Query params:**
  - `include` (str, default `"props,books"`) – comma-separated: `props`, `books`, `ev_slips`.
  - `normalize` (bool, default `true`) – if true, returns AI-friendly normalized data structure.
- **Behavior:**
  - Looks up event in Redis by canonical event id.
  - If `normalize=true`, runs `_normalize_for_ai` to output markets (`h2h`, `spreads`, `totals`, `team_totals`, `player_props`) and a summary block.

**GET `/v6/match`**

- **Auth:** API key.
- **Query params:**
  - `sport` (required) – e.g. `basketball_nba`.
  - `home_team` (optional).
  - `away_team` (optional).
  - `markets` (str, default `"h2h,spreads,totals"`).
- **Behavior:**
  - If `home_team` and `away_team` are supplied, resolves canonical event via `cache_manager.get_lookup_key` and returns a single event (optionally filtered markets).
  - If teams are omitted, returns all cached events for the sport (up to a high cap), including markets, books, props, provenance.

### 1.3 Market-Level Cache Views

**GET `/v6/spreads`**

- **Auth:** API key.
- **Query params:**
  - `sport` (required) – sport key.
  - `home_team` (optional).
  - `away_team` (optional).
- **Behavior:**
  - Extracts point-spread markets from cached events (via `odds_by_book` and/or `books[*].markets/odds`).
  - With teams → one game; without → all games for sport.
- **Response shape:**
  - `{ sport, games: [ { match: {home_team, away_team, sport, commence_time}, spreads: [...] } ], total_games }`.

**GET `/v6/player_props`**

- **Auth:** API key.
- **Query params:**
  - `sport` (required).
  - `home_team` (optional).
  - `away_team` (optional).
- **Behavior:**
  - Extracts **player props only** from each event (prefers `books[book].props`, falls back to `props_by_book` or flat `props`).
  - Filters out traditional team markets (`market_type` in `spread|total|moneyline`) and props where `player_name` looks like a matchup (`"A vs B"`, `"A @ B"`).
  - Ensures `stat_value` is populated from `value` when missing.
- **Response:**
  - `{ sport, games: [ { match: {...}, player_props: [...] } ], count, generated_at }`.

**GET `/v6/game_bundle`**

- **Auth:** API key.
- **Query params:**
  - `sport` (required).
  - `home_team` (required).
  - `away_team` (required).
  - `books` (required) – comma-separated; normalized to canonical sportsbook keys.
- **Behavior:**
  - Resolves canonical event.
  - Builds two sections:
    - `markets`: core markets (moneyline, spreads, totals) per team.
    - `player_props`: player props grouped by team, then player.
  - Computes coverage stats:
    - `requested_books`, `books_with_data`.
  - If requested books yield no data, falls back to all books present on event.

### 1.4 EV-Focused Cache Reads

**GET `/v6/ev-props`**

- **Auth:** API key.
- **Query params:**
  - `sport` (required).
- **Behavior:**
  - Iterates cached events for sport; extracts EV-enhanced props from `props_by_book`.
  - Flattens into a list, then groups by `(player_name, stat_type)`.
  - Each group has `books` entries containing EV metrics (`ev_edge_value`, `walter_probability`, `no_vig_odds`, `no_vig_probability`).
  - Sorted by best EV edge.
- **Response:**
  - `{ sport, ev_props: [...], total_props, generated_at }`.

**GET `/v6/ev`**

- **Auth:** API key.
- **Query params:**
  - `sport` (required) – must be in EV source support map.
  - `books` (optional) – normalized with `EV_BOOK_ALIASES`.
  - `raw` (bool, default `false`) – if true, emit raw processed EV source props.
- **Behavior:**
  - Filters `DEFAULT_EV_SOURCES` by `EV_SOURCE_SPORTS_SUPPORT` for the given sport.
  - For each source: `create_ev_streamer → connect → fetch_data(sport) → process_data()`; collects `player_props`.
  - Optionally filters by requested books.
  - Returns unified EV payload combining props and derived bets.
- **Response shape:**
  - `{ sport, ev_props: [...], total_props, ev_sources: [...], sportsbooks: [...], generated_at }` (exact structure depends on streamer logic).

### 1.5 Cache Health & Admin

**GET `/v6/health/cache`**

- **Auth:** API key.
- **Behavior:**
  - `cache_manager.health_check()` for Redis.
  - `get_background_worker().get_worker_status()` if present.
- **Response:**
  - `{ cache: {...}, worker: { running, active_books, sports, poll_interval, ... }, timestamp }`.

**GET `/v6/stats`** (cache statistics)

- **Auth:** API key.
- **Behavior:**
  - Calls `cache_manager.get_metrics()`.
  - For main sports (`americanfootball_nfl`, `basketball_nba`, `baseball_mlb`, `icehockey_nhl`), counts cached events via `get_sport_events`.
- **Response:**
  - `{ metrics, events_by_sport, total_events, timestamp }`.

**POST `/v6/admin/cache/clear`**

- **Auth:** API key.
- **Query params:**
  - `pattern` (optional) – pattern for keys to clear; if omitted, uses `"v6:*"`.
- **Behavior:**
  - Uses `cache_manager.clear_pattern` to delete matching keys.
- **Response:**
  - `{ message, deleted_keys, timestamp }`.

---

## 2. V6 Unified Odds/Props API (`v6.api.unified`, prefix `/v6`)

Combines `OddsEngine` and Redis-based props into a unified interface.

### 2.1 Health & Book Discovery

**GET `/v6/health`**

- **Auth:** None.
- **Behavior:**
  - `odds_engine.health_check()`.
  - `cache_manager.health_check()` for props cache.
- **Response:**
  - `{ status: "healthy"|"degraded", odds_engine: {...}, props_cache: {...}, timestamp }`.

**GET `/v6/books`**

- **Auth:** None.
- **Behavior:**
  - `odds_engine.get_available_books()`.
  - Scans Redis keys for props books per main sport.
- **Response:**
  - `{ odds_books, props_books, props_books_by_sport, total_odds_books, total_props_books, timestamp }`.

### 2.2 Odds

**GET `/v6/odds/{book_key}`**

- **Auth:** None.
- **Path params:** `book_key`.
- **Query params:** `sport` (optional).
- **Behavior:** calls `OddsEngine.get_odds_by_book(book_key, sport)`.
- **Errors:** HTTP 404 if result contains `{"error": ...}`.

**GET `/v6/odds`**

- **Auth:** None.
- **Query params:** `sport` (optional).
- **Behavior:** `OddsEngine.get_all_odds(sport)`.

### 2.3 Props (Redis Cached)

**GET `/v6/props/{book_key}`**

- **Auth:** None.
- **Path params:** `book_key`.
- **Query params:** `sport` (optional; defaults to `basketball_nba` inside helper).
- **Behavior:** retrieves cached props envelope for that book+sport via `get_book_data`.

**GET `/v6/props`**

- **Auth:** None.
- **Query params:**
  - `sport` (optional; default `basketball_nba`).
  - `books` (optional) – comma-separated; if omitted, uses discovered books from cache for that sport.
- **Behavior:**
  - Fetches payloads for requested books, computes `total_props`, and returns summary.

### 2.4 Main Sports Snapshot

**GET `/v6/main-sports`**

- **Auth:** None.
- **Query params:**
  - `books` (optional) – target books to focus on; if omitted, uses available books.
  - `include_odds` (bool, default `true`).
  - `include_props` (bool, default `true`).
- **Behavior:**
  - For each sport in `MAIN_SPORTS`:
    - Optionally attaches `odds` from `OddsEngine.get_main_sports_odds`.
    - Optionally attaches props by scanning cache and aggregating per book.

### 2.5 Player & Stat Filters

**GET `/v6/player/{player_name}`**

- **Auth:** None.
- **Path params:** `player_name`.
- **Query params:**
  - `sport` (optional; default `basketball_nba`).
  - `books` (optional).
- **Behavior:**
  - Fetches cached props for books, filters props whose `player_name` (case-insensitive) matches.
- **Response:**
  - `{ player, sport, books: {book_key: { player_props, total_props, fetched_at }}, total_props, requested_books, missing_books, fetched_at }`.

**GET `/v6/stat/{stat_type}`**

- **Auth:** None.
- **Path params:** `stat_type` (e.g., `points`, `rebounds`).
- **Query params:**
  - `sport` (optional; default `basketball_nba`).
  - `books` (optional).
- **Behavior:**
  - Similar to `/player/{player_name}`, but filters by `stat_type_name` or `market_type` in props.

---

## 3. V6 Stats API (`v6.api.stats`, mounted at `/v6`)

These endpoints expose games, teams, players, box scores, and historical stats.

### 3.1 Games & Schedule

**GET `/v6/games`**

- Query: `sport` (default `nfl`), `league` (default `nfl`), `event_ids` (comma-separated optional), `betmode` (bool, default `true`).

**GET `/v6/games/today`**

- Query: `sport` (default `nfl`).

**GET `/v6/games/live`**

- Query: `sport` (default `nfl`).

**GET `/v6/games/{game_id}`**

- Path: `game_id`.
- Query: `sport` (default `nfl`).

**GET `/v6/schedule`**

- Query: `sport` (default `nfl`), `utc_offset` (seconds, default `-18000`).

All of the above return `GameResponse` lists or `ScheduleResponse` as defined in `stats.py`.

### 3.2 Teams & Standings

**GET `/v6/teams`**

- Query: `sport` (default `nfl`), `league` (default `nfl`).

**GET `/v6/teams/{team_id}`**

- Path: `team_id`.
- Query: `sport` (default `nfl`).

**GET `/v6/standings`**

- Query: `sport` (default `nfl`), `league` (default `nfl`).

### 3.3 Players & Rosters

**GET `/v6/players`**

- Query: `team_id` (required), `sideload_team` (bool, default `true`).

**GET `/v6/roster`**

- Alias for `/v6/players` (same params).

**GET `/v6/players/{player_id}`**

- Path: `player_id`.
- Query: `team_id` (optional).

### 3.4 Box Scores

**GET `/v6/boxscore/{game_id}`**

- Path: `game_id`.
- Query: `sport` (default `nfl`).
- Returns normalized boxscore payload including `game_id`, `sport`, and normalized box score under `box_score`.

### 3.5 Comprehensive Stats & Metadata

**GET `/v6/stats`**

- Team-level player stats.
- Query: `team_id` (required), `sport` (required), `start_date`, `end_date`, `categories`, `position`, `min_games`.

**GET `/v6/stats/{player_id}`**

- Player-level stats.
- Path: `player_id`.
- Query: `team_id` (optional), `sport` (required), `categories` (optional).

**GET `/v6/stats/categories`**

- Returns doc-like metadata about stat categories and supported sports.

**GET `/v6/stats/compare`**

- Query: `player_ids` (comma-separated), `sport`, `categories` (optional).
- Returns side-by-side comparison of player statistics.

### 3.6 Stats Engine Health & Status

**GET `/v6/health`** (stats engine)

- Lightweight engine health check.

**GET `/v6/status`**

- Returns stats engine status summary including supported features and covered sports.

### 3.7 ESPN Historical Data

All paths are prefixed by `/v6`.

**GET `/v6/history/{sport}/{date}`** (Historical games list)

- Path: `sport`, `date` (`YYYY-MM-DD`).
- Returns `HistoricalGameList` with ESPN-derived summaries for the date.

**GET `/v6/history/{event_id}`** (Historical game summary)

- Path: `event_id` (ESPN event id).
- Query: `sport` (default `basketball_nba`).
- Returns `HistoricalGameSummary`.

**GET `/v6/history/{sport}/search`**

- Path: `sport`.
- Query: `team` (optional), `start_date` (optional, `YYYY-MM-DD`), `end_date` (optional), `limit` (default `50`).
- Returns search results and metadata for ESPN historical games.

---

## 4. V6 Odds API (`v6.api.odds`, mounted at `/v6`)

Odds-focused endpoints wrapping Lunosoft and internal aggregation.

### 4.1 Live Odds

**GET `/v6/odds/live`**

- Query: `sport` (default `basketball_nba`).
- Returns `List[LiveOddsResponse]` for in-progress games (live state, scores, live moneyline/spread/total).

**GET `/v6/odds/live/{sport}`**

- Path: `sport`.
- Query: `limit` (default `200`).
- Uses `StatsEngine.get_today_games` + per-game odds aggregation.

### 4.2 Unified Game Odds

**GET `/v6/odds/{game_id}`**

- Path: `game_id`.
- Query: `sport` (default `nfl`).
- Returns list of `UnifiedOddsResponse` entries for the given game.

### 4.3 Historical Odds (Unified Format)

**GET `/v6/odds/history/{sport}/{date}`**

- Path: `sport`, `date` (`YYYY-MM-DD`).
- Query: `sportsbook_ids` (optional, comma-separated ints).
- Returns unified odds entries for all games on that date.

**GET `/v6/odds/history/{game_id}`**

- Path: `game_id`.
- Query: `sport` (default `nfl`), `hours_back` (default `24`).
- Currently simulated timeline of `OddsHistoryResponse` snapshots for dev/backtest purposes.

### 4.4 Odds Export

**GET `/v6/odds/export/{sport}`**

- Path: `sport`.
- Query: `date_from` (datetime), `date_to` (datetime), `format` (`json|csv`).
- Returns metadata about a hypothetical export task (stub implementation).

---

## 5. V6 Export API (`v6.api.export`, prefix `/v6`)

**GET `/v6/export`**

- Streaming export of odds, props, stats, and historical datasets.
- Query params:
  - `format` – `"json"` (NDJSON) or `"csv"`.
  - `datasets` – optional comma-separated list from:
    - `live_odds`, `live_props`, `game_stats`,
    - `historical_odds`, `historical_props`, `historical_games`,
    - `historical_team_stats`, `historical_team_stat_leaders`,
    - `historical_players`, `historical_player_boxscores`.
  - `scope` – `"all" | "live" | "historical"`.
  - Filters: `sport`, `books`, `book_name`, `date_from`, `date_to`, `team_id`, `player_id`, `game_id`, `limit`.
- **Response:**
  - `StreamingResponse` with `application/x-ndjson` or `text/csv`, plus `Content-Disposition` filename.

---

## 6. V6 Production API (`v6.api.production`, prefix `/v6/prod`, NOT mounted by default)

This router is defined but not currently attached in `main.py`. Paths below assume it is mounted.

### 6.1 Health & Monitoring

**GET `/v6/prod/health`**

- **Auth:** Bearer (production placeholder).
- Detailed health across optimized engines, caches, and metrics.

**GET `/v6/prod/monitoring/metrics`**

- **Auth:** Bearer.
- Query: `hours_back` (1–24).
- Returns realtime summary from metrics + historical metrics from persistence.

**GET `/v6/prod/monitoring/caches`**

- **Auth:** Bearer.
- Returns cache info for odds + props caches.

**GET `/v6/prod/monitoring/circuit-breakers`**

- **Auth:** Bearer.
- Returns per-book circuit breaker state and counts problematic books.

### 6.2 Admin & Historical Persistence

**POST `/v6/prod/admin/caches/clear`**

- **Auth:** Bearer.
- Query: `cache_type` (`odds|props|all`).
- Clears in-process caches and increments a `cache_cleared` metric.

**POST `/v6/prod/admin/circuit-breakers/reset`**

- **Auth:** Bearer.
- Query: `book_key` (optional).
- Resets circuit breakers for a specific book or all books.

**GET `/v6/prod/history/odds/{book_key}`**

- **Auth:** Bearer.
- Path: `book_key`.
- Query: `sport`, `hours_back` (1–168).
- Returns odds snapshots over time from persistence.

**GET `/v6/prod/history/props/{book_key}/{player_id}`**

- **Auth:** Bearer.
- Path: `book_key`, `player_id`.
- Query: `hours_back`.
- Returns historical props records for a given player/book.

**POST `/v6/prod/admin/persistence/cleanup`**

- **Auth:** Bearer.
- Query: `days_to_keep` (7–90).
- Triggers asynchronous cleanup of old historical data.

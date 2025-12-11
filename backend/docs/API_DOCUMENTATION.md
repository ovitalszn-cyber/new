# Kashrock V6 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All requests require an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

Test API Key: `kr_test_key`

---

## 📊 Stats API - Real Game Data

### Get NFL Games
```bash
GET /v6/games?sport=nfl&limit=10
```

**Response:** List of NFL games with full team details, scores, and metadata

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/games?sport=nfl&limit=5"
```

### Supported Sports
- `nfl` - NFL Football
- `nba` - NBA Basketball  
- `mlb` - MLB Baseball
- `nhl` - NHL Hockey

---

## 🎯 Live Odds & Player Props

### Discover Live Events
```bash
GET /v6/match?sport=americanfootball_nfl&limit=5
```

**Response:** Live events with player props from multiple sportsbooks

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/match?sport=americanfootball_nfl&limit=3"
```

### Get Specific Event
```bash
GET /v6/event/{canonical_event_id}
```

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/event/evt_6305523b1822e954"
```

**Response includes:**
- Home/Away teams
- All available sportsbooks
- Player props (Passing Yards, TDs, Rushing, Receiving, etc.)
- Odds from 30+ books (Pinnacle, DraftKings, FanDuel, BetMGM, etc.)

---

## 🎮 Esports API

### Get Esports Matches
```bash
GET /v6/esports/matches?discipline={lol|cs2|dota2|val}&limit=10
```

**Query Parameters:**
- `discipline` - Filter by esport (lol, cs2, dota2, val)
- `start_date` - Filter by start date (YYYY-MM-DD)
- `end_date` - Filter by end date (YYYY-MM-DD)
- `limit` - Max results (default: 50)

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/esports/matches?discipline=lol&limit=5"
```

### Get Specific Match
```bash
GET /v6/esports/matches/{match_id}
```

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/esports/matches/105117"
```

---

## 📈 Historical Odds (Database Backed)

### Get Odds History for Game
```bash
GET /v6/odds/history/{game_id}?sport={sport}&hours_back=24
```

**Query Parameters:**
- `sport` - Sport type (nfl, nba, mlb, nhl)
- `hours_back` - Hours of history (1-168, default: 24)

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/odds/history/137554?sport=nfl&hours_back=48"
```

**Response:** Time-series odds snapshots with movement indicators

---

## 📥 Data Export

### Export Historical Data
```bash
GET /v6/export?format={json|csv}&datasets={dataset_list}&sport={sport}
```

**Supported Datasets:**
- `live_odds` - Current odds
- `live_props` - Current player props
- `historical_odds` - Historical odds snapshots
- `historical_props` - Historical prop snapshots
- `game_stats` - Game statistics
- `historical_player_boxscores` - Player box scores

**Query Parameters:**
- `format` - Export format (json or csv)
- `datasets` - Comma-separated list of datasets
- `sport` - Filter by sport
- `date_from` - Start date (ISO8601)
- `date_to` - End date (ISO8601)
- `limit` - Row limit (default: 5000)

**Example:**
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/export?format=json&datasets=live_props&sport=americanfootball_nfl&limit=100" \
  > props_export.jsonl
```

### Legacy Export Endpoint (Redirects)
```bash
GET /v6/odds/export/{sport}?date_from={date}&date_to={date}
```

Automatically redirects to the streaming export service.

---

## 🔍 Quick Test Suite

### 1. Verify API is Running
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/games?sport=nfl&limit=1"
```

### 2. Check Live Player Props
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/match?sport=americanfootball_nfl&limit=1"
```

### 3. Test Esports Data
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/esports/matches?discipline=lol&limit=3"
```

### 4. Verify Historical Odds
```bash
curl -H "Authorization: Bearer kr_test_key" \
  "http://localhost:8000/v6/odds/history/137554?sport=nfl"
```

---

## 📋 Response Formats

### Game Response
```json
{
  "id": 137553,
  "sport": "nfl",
  "league": "nfl",
  "scheduled_at": "2025-08-08T00:00:00Z",
  "status": "final",
  "home_team": {
    "medium_name": "DET Lions",
    "abbreviation": "DET",
    "id": 9
  },
  "away_team": {
    "medium_name": "LA Chargers",
    "abbreviation": "LAC",
    "id": 8
  },
  "score": {...},
  "venue": "Canton, OH"
}
```

### Player Prop Response
```json
{
  "player_name": "Baker Mayfield",
  "stat_type_name": "Passing Yards",
  "line": 217.5,
  "direction": "over",
  "odds": -115,
  "sportsbook_name": "Pinnacle",
  "home_team": "TB",
  "away_team": "ATL",
  "game_start": "12/12/2025 01:15"
}
```

### Esports Match Response
```json
{
  "id": 380165,
  "match_id": 105117,
  "sport": "lol",
  "discipline": "lol",
  "start_date": "2025-12-21T15:00:00.000+00:00",
  "status": "upcoming",
  "bo_type": 3,
  "tournament_id": 5042,
  "tier": "c"
}
```

---

## ⚡ Performance Notes

- **Stats API**: < 100ms response time
- **Live Props**: Cached, refreshed every 30 seconds
- **Historical Queries**: Indexed for fast lookups
- **Export**: Streaming responses for large datasets

---

## 🚀 Next Steps

1. **Test with real game IDs** from `/v6/games`
2. **Explore live props** via `/v6/match`
3. **Query historical data** as it accumulates
4. **Export datasets** for analysis

For issues or questions, check the logs or contact support.

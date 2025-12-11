# v5 Consumer Feedback Analysis

## The Problem We're Solving (From Customer Feedback)

**Customer wants:**
```
Match X
1x2 {
  bet365: 2, marathonbet: 2.4
  marathonbet: 4, bet365: 3.8
  X: ...
}
```

**Translation:** Market-first structure where:
- You query by teams directly ("Lakers vs Warriors")
- Get ALL bookies' odds for each outcome in one response
- Format: `outcome: {book1: odds1, book2: odds2, ...}`

**Key quote:** *"When I look for an event I want to get for example all bookies odds for a particular result, or the event"*

## Critical Issues Found

### ❌ Issue 1: Wrong Response Structure

**Current (Book-first):**
```json
{
  "books": {
    "draftkings": {
      "markets": {
        "h2h": {
          "runners": [{"id": "Lakers", "odds": 2.10}]
        }
      }
    },
    "betmgm": {
      "markets": {
        "h2h": {
          "runners": [{"id": "Lakers", "odds": 2.05}]
        }
      }
    }
  }
}
```

**What they want (Market-first, Outcome-centric):**
```json
{
  "markets": {
    "h2h": {
      "Los Angeles Lakers": {
        "draftkings": 2.10,
        "betmgm": 2.05,
        "caesars": 2.02
      },
      "Golden State Warriors": {
        "draftkings": 1.85,
        "betmgm": 1.90,
        "caesars": 1.88
      }
    },
    "spreads": {
      "Los Angeles Lakers -3.5": {
        "draftkings": 1.91,
        "betmgm": 1.89
      }
    }
  }
}
```

**Problem:** Current structure requires consumers to iterate through books, then markets, then find outcomes. They want to see ALL books for an outcome in one place.

### ❌ Issue 2: Two-Step Process (Friction)

**Current flow:**
1. Call `/v5/events?sport=basketball_nba&home_team=Lakers&away_team=Warriors`
2. Get `canonical_event_id`
3. Call `/v5/event/{canonical_event_id}`

**What they want:**
1. Call `/v5/match?home_team=Lakers&away_team=Warriors&sport=basketball_nba`
2. Done.

**Problem:** Extra step creates friction. They want to query by teams directly.

### ❌ Issue 3: Missing Direct Team Query

**Current:** Must discover events first, then use canonical_event_id

**What they want:** Direct query by teams:
```
GET /v5/match?home_team=Los Angeles Lakers&away_team=Golden State Warriors&sport=basketball_nba
```

### ❌ Issue 4: Response Doesn't Match Their Format

They showed this exact format:
```
1x2 {
  bet365: 2, marathonbet: 2.4
  marathonbet: 4, bet365: 3.8
  X: ...
}
```

This is: **Market → Outcome → {book: odds}**

We're returning: **Books → Markets → Outcomes**

## Required Fixes

### ✅ Fix 1: Add Direct Match Endpoint

```python
@router.get("/match")
async def get_match_unified(
    sport: str = Query(..., description="Sport key"),
    home_team: str = Query(..., description="Home team name"),
    away_team: str = Query(..., description="Away team name"),
    markets: str = Query("h2h,spreads,totals,player_props", description="Markets to include"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    Get unified odds for a match by team names.
    Returns market-first structure with all books per outcome.
    """
```

### ✅ Fix 2: Restructure Response to Market-First

**New structure:**
```json
{
  "match": {
    "home_team": "Los Angeles Lakers",
    "away_team": "Golden State Warriors",
    "sport": "basketball_nba",
    "commence_time": "2025-01-15T20:00:00Z"
  },
  "markets": {
    "h2h": {
      "Los Angeles Lakers": {
        "draftkings": 2.10,
        "betmgm": 2.05,
        "caesars": 2.02
      },
      "Golden State Warriors": {
        "draftkings": 1.85,
        "betmgm": 1.90,
        "caesars": 1.88
      }
    },
    "spreads": {
      "Los Angeles Lakers -3.5": {
        "draftkings": 1.91,
        "betmgm": 1.89
      },
      "Golden State Warriors +3.5": {
        "draftkings": 1.91,
        "betmgm": 1.89
      }
    },
    "player_props": {
      "LeBron James Over 25.5 Points": {
        "prizepicks": 1.91,
        "underdog": 1.88,
        "dabble": 1.93
      }
    }
  },
  "provenance": {
    "sources": ["draftkings", "betmgm", "caesars", "prizepicks", "underdog", "dabble"],
    "source_count": 6
  }
}
```

### ✅ Fix 3: Update Merge Service

The merge service needs to output market-first format:
- Group by market
- For each market, group by outcome
- For each outcome, show all books with their odds

### ✅ Fix 4: Keep Canonical ID Endpoint (For Caching/Advanced Use)

Keep `/v5/event/{canonical_event_id}` for:
- Cached lookups
- Advanced users who want canonical IDs
- But make `/v5/match` the primary endpoint

## Implementation Priority

1. **HIGH:** Add `/v5/match` endpoint with direct team query
2. **HIGH:** Restructure response to market-first format
3. **MEDIUM:** Update merge service to output new format
4. **LOW:** Keep canonical ID endpoint for advanced use

## Example Usage (After Fixes)

```bash
# What they want - ONE CALL
curl "https://api.com/v5/match?sport=basketball_nba&home_team=Los%20Angeles%20Lakers&away_team=Golden%20State%20Warriors" \
  -H "Authorization: Bearer KEY"

# Response shows ALL books for each outcome
{
  "markets": {
    "h2h": {
      "Los Angeles Lakers": {
        "draftkings": 2.10,
        "betmgm": 2.05,
        "caesars": 2.02
      }
    }
  }
}
```

This is exactly what they're asking for - **one call, all books, market-first structure**.


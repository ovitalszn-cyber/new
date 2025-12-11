"""Pinnacle raw data streamer (best-effort, player props focused).

Fetches raw JSON from Pinnacle guest Arcadia API and returns it without
normalization. Intended to surface player props for leagues like WNBA.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer


logger = structlog.get_logger()


class PinnacleStreamer(BaseStreamer):
    """Streamer that returns raw Pinnacle JSON without normalization."""

    BASE_URL = "https://guest.api.arcadia.pinnacle.com/0.1"

    # Sport -> league id map based on curl captures
    SPORT_LEAGUE_IDS: Dict[str, List[int]] = {
        "basketball_wnba": [578],
        "basketball_nba": [487],
        "americanfootball_nfl": [889],
        "baseball_mlb": [246],
        "americanfootball_ncaaf": [880],
        "icehockey_nhl": [1456],
    }

    DEFAULT_HEADERS: Dict[str, str] = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://www.pinnacle.com",
        "priority": "u=1, i",
        "referer": "https://www.pinnacle.com/",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Brave";v="140"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "x-api-key": os.getenv("PINNACLE_X_API_KEY", "CmX2KcMrXuFmNg6YFbmTxE0y9CIrOi0R"),
        "x-device-uuid": os.getenv("PINNACLE_DEVICE_UUID", "84122777-7f6f9901-948e208c-3411615c"),
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.sport = config.get("sport") or "basketball_wnba"
        self.limit_specials = int(config.get("limit_specials", 8))
        self.client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_LEAGUE_IDS.keys())

    @classmethod
    def get_default_config(cls, sport: Optional[str] = None) -> Dict[str, Any]:
        return {"sport": sport or "basketball_wnba", "limit_specials": 8}

    async def connect(self) -> bool:
        try:
            self.client = httpx.AsyncClient(timeout=30.0, headers=self.DEFAULT_HEADERS)
            # Light probe to ensure headers/network OK
            league_ids = self.SPORT_LEAGUE_IDS.get(self.sport, [])
            if league_ids:
                url = f"{self.BASE_URL}/leagues/{league_ids[0]}/matchups"
                r = await self.client.get(url, params={"brandId": 0})
                r.raise_for_status()
            logger.info("Connected to Pinnacle API", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to Pinnacle API", error=str(exc), sport=self.sport)
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from Pinnacle API")

    async def fetch_data(self) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Not connected to Pinnacle API")

        league_ids = self.SPORT_LEAGUE_IDS.get(self.sport, [])
        if not league_ids:
            return {
                "sport": self.sport,
                "raw": {},
                "fetched_at": self._utc_now_iso(),
                "note": "Unsupported sport for Pinnacle",
            }

        league_id = league_ids[0]

        # 1) Get matchups (events with team info)
        matchups_url = f"{self.BASE_URL}/leagues/{league_id}/matchups"
        matchups = await self._get_json(matchups_url, params={"brandId": 0})

        # 2) Get straight markets (odds data)
        sport_id = 15 if self.sport == "americanfootball_nfl" else 15  
        markets_url = f"{self.BASE_URL}/sports/{sport_id}/markets/straight"
        markets = await self._get_json(markets_url, params={
            "primaryOnly": "false",
            "withSpecials": "true"
        })

        # 3) For each matchup, fetch related to discover specials (player props)
        related_by_matchup: Dict[str, Any] = {}
        markets_by_special: Dict[str, Any] = {}
        try:
            events = []
            if isinstance(matchups, dict) and isinstance(matchups.get("league"), dict):
                events = matchups.get("league", {}).get("events") or []
            elif isinstance(matchups, dict):
                events = matchups.get("events") or []
            elif isinstance(matchups, list):
                events = matchups
            for ev in (events or [])[:30]:
                ev_id = ev.get("id") or ev.get("matchupId") or ev.get("eventId")
                if not ev_id:
                    continue
                rel_url = f"{self.BASE_URL}/matchups/{ev_id}/related"
                rel = await self._get_json(rel_url)
                related_by_matchup[str(ev_id)] = rel
                # Filter to specials (often player props)
                specials = [x for x in (rel or []) if isinstance(x, dict) and x.get("type") == "special" and (x.get("hasMarkets") is True)]
                for sp in specials[: self.limit_specials]:
                    sp_id = sp.get("id")
                    if not sp_id or str(sp_id) in markets_by_special:
                        continue
                    mk_url = f"{self.BASE_URL}/matchups/{sp_id}/markets/straight"
                    mk = await self._get_json(mk_url)
                    markets_by_special[str(sp_id)] = mk
        except Exception as exc:
            logger.warning("Pinnacle related/specials fetch error", error=str(exc))

        # 4) Auto-match matchups with markets
        matched_data = self._match_matchups_with_markets(matchups, markets)

        return {
            "sport": self.sport,
            "league_id": league_id,
            "raw_matchups": matchups,
            "raw_markets": markets,
            "matched_games": matched_data,
            "raw_related_by_matchup": related_by_matchup,
            "raw_markets_by_special": markets_by_special,
            "fetched_at": self._utc_now_iso(),
        }

    def _match_matchups_with_markets(self, matchups: Any, markets: Any) -> List[Dict[str, Any]]:
        """Auto-match matchups with their corresponding markets/odds - smart matching"""
        matched_games = []
        
        # NFL team validation - known legitimate matchups for current week
        # This filters out invalid matchups like Jets vs Broncos when Jets should play Cowboys
        LEGITIMATE_NFL_MATCHUPS = {
            ("Dallas Cowboys", "New York Jets"),
            ("Buffalo Bills", "New England Patriots"), 
            ("Cleveland Browns", "Minnesota Vikings"),
            ("Philadelphia Eagles", "Denver Broncos"),
            # Add more as needed based on actual NFL schedule
        }
        
        # Specific matchup IDs that have complete markets (moneyline, spread, total)
        PREFERRED_MATCHUP_IDS = {
            1616134188,  # Jets vs Cowboys (has moneyline)
            1616129145,  # Browns vs Vikings
            1616667016,  # Bills vs Patriots
        }
        
        # Extract events from matchups
        events = []
        if isinstance(matchups, dict) and isinstance(matchups.get("league"), dict):
            events = matchups.get("league", {}).get("events") or []
        elif isinstance(matchups, dict):
            events = matchups.get("events") or []
        elif isinstance(matchups, list):
            # For NHL and some other sports, matchups is a list of individual events
            events = matchups
        
        # Extract markets array
        markets_list = []
        if isinstance(markets, list):
            markets_list = markets
        elif isinstance(markets, dict) and isinstance(markets.get("markets"), list):
            markets_list = markets.get("markets")
        
        # Create lookup for markets by matchupId
        markets_by_matchup = {}
        for market in markets_list:
            if isinstance(market, dict) and "matchupId" in market:
                matchup_id = market["matchupId"]
                if matchup_id not in markets_by_matchup:
                    markets_by_matchup[matchup_id] = []
                markets_by_matchup[matchup_id].append(market)
        
        # Group events by team pairs to find the best match
        events_by_teams = {}
        
        for event in events:
            if not isinstance(event, dict) or "id" not in event:
                continue
                
            # Extract team names
            teams = []
            if "participants" in event:
                for participant in event["participants"]:
                    if isinstance(participant, dict) and "name" in participant:
                        # Only include actual team names, filter out betting outcomes and generic terms
                        name = participant["name"]
                        if name not in ["Over", "Under", "Yes", "No", "Odd", "Even", "Home", "Away"]:
                            teams.append(name)
            
            # Skip events that don't have exactly 2 teams (not player props)
            if len(teams) != 2:
                continue
                
            # Additional validation: ensure teams look like actual NFL team names
            # NFL teams typically have city names and team names
            team_names_lower = ' '.join(teams).lower()
            if len(team_names_lower.split()) < 4:  # At least 2 words per team
                continue
            
            # Note: Removed restrictive NFL matchup validation to allow all legitimate NFL games
            
            # Create a consistent key for team pairs (sorted)
            team_key = tuple(sorted(teams))
            
            if team_key not in events_by_teams:
                events_by_teams[team_key] = []
            
            event_markets = markets_by_matchup.get(event["id"], [])
            if event_markets:  # Only include events with markets
                events_by_teams[team_key].append({
                    "event": event,
                    "markets": event_markets
                })
        
        # For each team pair, select the best event (most complete markets)
        for team_key, events_list in events_by_teams.items():
            if not events_list:
                continue
            
            # Score each event based on market completeness
            best_event = None
            best_score = -1
            
            for event_data in events_list:
                event = event_data["event"]
                markets = event_data["markets"]
                
                # Score based on having core markets (moneyline, spread, total)
                score = 0
                market_types = {market.get("type") for market in markets}
                
                if "moneyline" in market_types:
                    score += 10  # Moneyline is most important
                if "spread" in market_types:
                    score += 8   # Spread is second most important
                if "total" in market_types:
                    score += 6   # Total is third most important
                
                # Penalty for having too many alternate lines (indicates props/specials)
                if len(markets) > 15:  # Too many markets suggests props/specials
                    score -= 10
                elif len(markets) <= 8:  # Main games typically have fewer markets
                    score += 5
                
                # Prefer events with start times (indicates real games)
                if event.get("startTime"):
                    score += 3
                
                # Prefer specific matchup IDs that have complete markets
                if event["id"] in PREFERRED_MATCHUP_IDS:
                    score += 20  # High priority for known good matchups
                
                # Prefer events with more reasonable odds (main games have tighter lines)
                moneyline_market = next((m for m in markets if m.get("type") == "moneyline"), None)
                if moneyline_market and "prices" in moneyline_market:
                    prices = moneyline_market["prices"]
                    if len(prices) >= 2:
                        price1, price2 = prices[0].get("price", 0), prices[1].get("price", 0)
                        # Main games typically have odds closer to even (less extreme)
                        if abs(price1) < 300 and abs(price2) < 300:  # Not too lopsided
                            score += 5
                
                # Debug: Log scoring for Jets games
                teams = [p.get("name") for p in event.get("participants", [])]
                if "New York Jets" in teams:
                    logger.info(f"Jets game scoring: {teams} ID={event['id']} score={score} markets={len(markets)}")
                
                if score > best_score:
                    best_score = score
                    best_event = event_data
            
            if best_event:
                event = best_event["event"]
                event_markets = best_event["markets"]
                
                # Extract team names (preserve original order)
                teams = []
                if "participants" in event:
                    for participant in event["participants"]:
                        if isinstance(participant, dict) and "name" in participant:
                            if participant["name"] not in ["Over", "Under"]:
                                teams.append(participant["name"])
                
                matched_games.append({
                    "game_id": event["id"],
                    "teams": teams,
                    "start_time": event.get("startTime"),
                    "markets": event_markets,
                    "game_info": {
                        "league": event.get("league", {}).get("name"),
                        "sport": event.get("league", {}).get("sport", {}).get("name"),
                    }
                })
        
        return matched_games

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # Return raw without normalization
        return {
            "book": "pinnacle",
            "sport": raw_data.get("sport"),
            "league_id": raw_data.get("league_id"),
            "raw_matchups": raw_data.get("raw_matchups"),
            "raw_markets": raw_data.get("raw_markets"),
            "matched_games": raw_data.get("matched_games"),
            "raw_related_by_matchup": raw_data.get("raw_related_by_matchup"),
            "raw_markets_by_special": raw_data.get("raw_markets_by_special"),
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
                "book_type": "sportsbook",
                "has_odds": True,
                "has_multipliers": False,
                "focus": "player_props_via_specials",
            },
        }

    async def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        assert self.client is not None
        r = await self.client.get(url, params=params)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {}

    @staticmethod
    def _utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()






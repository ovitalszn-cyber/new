"""Sharp Odds Streamer - Fetches main markets (Moneyline, Spread, Total) from Sharp API."""
from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Type

import httpx
import structlog

from streamers.base import BaseStreamer
from v6.common.market_normalizer import normalize_market_key

logger = structlog.get_logger()

# --- Book Configuration (All Available Main Market Books) ---
SHARP_KEY_PREFIX = "sharp_"

# (BookID, Key, Name) - derived from sharp_books_v2.json data for isFantasy=False
_SHARP_BOOK_DATA = [
    (7, "draftkings", "DraftKings"), (24, "betmgm", "BetMGM"), (14, "betrivers", "BetRivers"), 
    (39, "circalv", "Circa LV"), (19, "caesars", "Caesars"), (8, "fanduel", "FanDuel"), 
    (40, "fanatics", "Fanatics"), (37, "espnbet", "ESPN Bet"), (25, "unibet", "Unibet"), 
    (10009, "paddypoweruk", "Paddy Power UK"), (10160, "betmgmuk", "BetMGM UK"), (10070, "windcreek", "Wind Creek"), 
    (12, "betparx", "BetParx"), (10026, "primesports", "Prime Sports"), (10150, "mybookie", "MyBookie"), 
    (10200, "propsbuilder", "Props Builder"), (10114, "proline", "Proline"), (10090, "tonybet", "TonyBet"), 
    (10106, "tabtouch", "TABtouch"), (10027, "ladbrokesau", "Ladbrokes AU"), (10037, "bookmaker", "BookMaker"), 
    (10015, "tabau", "Tab AU"), (10081, "rizk", "Rizk"), (10019, "betonline", "BetOnline"), 
    (10023, "888sport", "888 Sport"), (2, "pinny", "Pinny"), (10008, "northstarbetsontario", "NorthStar Bets Ontario"), 
    (10083, "twinspires", "TwinSpires"), (10120, "coolbet", "Coolbet"), (10088, "neds", "Neds"), 
    (10110, "unibetau", "Unibet AU"), (10100, "topsportau", "TopSport AU"), (10104, "williamhill", "William Hill"), 
    (10111, "dabbleau", "Dabble AU"), (10113, "crabsports", "Crab Sports"), (10124, "sxbet", "SX Bet"), 
    (10126, "ibet", "iBet"), (10128, "betopenly", "BetOpenly"), (10127, "betvictor", "BetVictor"), 
    (10024, "betfairuk", "Betfair UK"), (10021, "bovada", "Bovada"), (50, "bet365", "Bet365"), 
    (10071, "leovegas", "LeoVegas"), (10016, "thescorebet", "TheScore Bet"), (10073, "bet105", "bet105"), 
    (10025, "sportsinteractionontario", "Sports Interaction Ontario"), (10076, "betano", "Betano"), 
    (10101, "powerplay", "PowerPlay"), (10082, "fourwinds", "Four Winds"), (10087, "miseojeu", "Mise-o-jeu"), 
    (10123, "betsson", "Betsson"), (10092, "playalberta", "Play Alberta"), (10072, "partypoker", "partypoker"), 
    (10094, "goldennugget", "Golden Nugget"), (10060, "resortsworldbet", "Resorts World Bet"), 
    (10061, "borgata", "Borgata"), (10062, "action247", "Action 247"), (10031, "desertdiamondsports", "Desert Diamond Sports"), 
    (10074, "bet99", "BET99"), (49, "betway", "Betway"), (10103, "firekeepers", "FireKeepers"), 
    (10089, "stnsports", "STN Sports"), (10093, "playeagle", "Play Eagle"), (10020, "bodog", "Bodog"), 
    (10165, "betfairexchange", "Betfair Exchange"), (38, "superbook", "SuperBook"), (10013, "skybetuk", "Sky Bet UK"), 
    (1, "pinnacle", "Pinnacle"), (10011, "prophetx", "ProphetX"), (10107, "circasports", "Circa Sports"), 
    (10022, "ballybet", "Bally Bet"), (10018, "unibetuk", "Unibet UK"), (10064, "betcris", "BetCris"), 
    (9, "sugarhouse", "SugarHouse"), (10080, "sportzino", "Sportzino"), (10077, "betjack", "betJACK"), 
    (10125, "sportsbet", "Sportsbet"), (10003, "casumoontario", "Casumo Ontario"), (10028, "betfreduk", "Betfred UK"), 
    (10007, "ladbrokesuk", "Ladbrokes UK"), (10006, "hardrockbet", "Hard Rock Bet"), (10001, "betsafeontario", "Betsafe Ontario")
]

ALL_SHARP_BOOK_IDS = [b[0] for b in _SHARP_BOOK_DATA]


class SharpOddsClient:
    """Shared client for Sharp Odds API to avoid duplicate requests."""

    BASE_URL = "https://graph.sharp.app/operations/v2/markets/ByMarketGroup"
    API_HASH = "a945f208"

    SPORT_MAP = {
        "basketball_nba": "nba",
        "americanfootball_nfl": "nfl",
        "baseball_mlb": "mlb",
        "icehockey_nhl": "nhl",
        "americanfootball_ncaaf": "ncaaf",
        "basketball_ncaab": "ncaab",
        "soccer_epl": "epl",
        # Add more mappings as needed
    }

    def __init__(self) -> None:
        self.session: Optional[httpx.AsyncClient] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
        self._inflight_requests: Dict[str, asyncio.Task] = {}

    async def get_session(self) -> httpx.AsyncClient:
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(
                headers={
                    "user-agent": "SharpApp/2406 CFNetwork/3860.300.21 Darwin/25.2.0",
                    "accept": "application/json",
                },
                timeout=httpx.Timeout(20.0), # Increased timeout for large payload
            )
        return self.session

    async def close(self) -> None:
        if self.session:
            await self.session.aclose()
            self.session = None

    async def fetch_markets(self, sport: str, group: str) -> Dict[str, Any]:
        """Fetch markets for a sport/group combination for ALL configured books."""
        sharp_league = self.SPORT_MAP.get(sport)
        if not sharp_league:
            return {}

        cache_key = f"{sport}:{group}"
        
        async with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached:
                age = (datetime.now() - cached["timestamp"]).total_seconds()
                if age < 30:
                    return cached["data"]

        if cache_key in self._inflight_requests:
            return await self._inflight_requests[cache_key]

        task = asyncio.create_task(self._do_fetch(sport, sharp_league, group))
        self._inflight_requests[cache_key] = task
        try:
            return await task
        finally:
            self._inflight_requests.pop(cache_key, None)

    async def _do_fetch(self, sport: str, league: str, group: str) -> Dict[str, Any]:
        session = await self.get_session()
        
        # Always fetch ALL book IDs to efficient cache sharing
        ids_str = ",".join(str(bid) for bid in ALL_SHARP_BOOK_IDS)
        
        params = {
            "wg_api_hash": self.API_HASH,
            "league": league,
            "group": group,
            "sportsbookIds": ids_str
        }

        try:
            resp = await session.get(self.BASE_URL, params=params)
            if resp.status_code == 200:
                data = resp.json()
                async with self._cache_lock:
                    self._cache[f"{sport}:{group}"] = {
                        "data": data,
                        "timestamp": datetime.now()
                    }
                return data
            elif resp.status_code == 404:
                # Expected for some combinations
                return {}
            else:
                logger.warning("Sharp Odds API error", status=resp.status_code, sport=sport, group=group)
                return {}
        except Exception as e:
            logger.error("Sharp Odds API exception", error=str(e), sport=sport)
            return {}
            
    async def fetch_all_main_markets(self, sport: str) -> Dict[str, Any]:
        """Fetch moneyline, spread, and totals concurrently and merge relational data."""
        groups = ["moneyline", "spread", "total"]
        
        tasks = [self.fetch_markets(sport, g) for g in groups]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined = {
            "markets": [],
            "events": {},
            "teams": {}
        }
        
        for res in results:
            if isinstance(res, dict) and "data" in res:
                data = res["data"]
                combined["markets"].extend(data.get("markets", []))
                for evt in data.get("events", []):
                    combined["events"][evt.get("eventId")] = evt
                for tm in data.get("teams", []): # Just in case
                    pass 
                
        return combined


# Shared singleton instance
_SHARP_CLIENT = SharpOddsClient()


class _SharpBookOddsStreamer(BaseStreamer):
    """Base streamer for a specific Sharp book."""

    BOOK_ID: int = -1
    BOOK_KEY: str = ""
    BOOK_NAME: str = ""

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.client = _SHARP_CLIENT

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        pass

    async def fetch_data(self, sport: Optional[str] = None) -> Dict[str, Any]:
        if not sport:
            sport = "americanfootball_nfl"

        data_package = await self.client.fetch_all_main_markets(sport)
        
        return {
            "data_package": data_package,
            "sport": sport,
            "book_id": self.BOOK_ID
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Sharp markets to V6 normalized format."""
        data_package = raw_data.get("data_package", {})
        markets = data_package.get("markets", [])
        events_map = data_package.get("events", {})
        
        sport = raw_data.get("sport", "")
        target_book_id = self.BOOK_ID
        
        games_map: Dict[str, Dict[str, Any]] = {}
        
        for m in markets:
            if m.get("sportsbookId") != target_book_id:
                continue
                
            event_id = m.get("eventId")
            if not event_id:
                continue
            
            event_obj = events_map.get(event_id)
            if not event_obj:
                continue
                
            if event_id not in games_map:
                game_info = self._extract_game_info(event_obj)
                games_map[event_id] = {
                    **game_info,
                    "normalized_markets": [],
                    "canonical_markets": []
                }
                
            # Normalize Market
            raw_type = m.get("marketType", "")
            period, base_type = self._parse_market_type(raw_type)
            canonical_key = normalize_market_key(base_type, "")
            
            game_obj = games_map[event_id]
            if "temp_markets" not in game_obj:
                game_obj["temp_markets"] = {} 
            
            mk_key = (period, canonical_key)
            if mk_key not in game_obj["temp_markets"]:
                game_obj["temp_markets"][mk_key] = {
                    "market_key": canonical_key,
                    "period": period,
                    "sportsbook_id": target_book_id
                }
            
            entry = game_obj["temp_markets"][mk_key]
            
            # Fill prices
            price = m.get("price")
            line = m.get("line")
            outcome_type = m.get("outcomeType", "").lower()
            
            if canonical_key == "h2h":
                if "home" in outcome_type:
                    entry["home_price"] = price
                elif "away" in outcome_type:
                    entry["away_price"] = price
            elif canonical_key == "spreads":
                if "home" in outcome_type:
                    entry["home_spread"] = line
                    entry["home_price"] = price
                elif "away" in outcome_type:
                    entry["away_spread"] = line
                    entry["away_price"] = price
            elif canonical_key == "totals":
                entry["total"] = line
                if "over" in outcome_type:
                    entry["over_price"] = price
                elif "under" in outcome_type:
                    entry["under_price"] = price
        
        final_games = []
        for gid, game in games_map.items():
            temp = game.pop("temp_markets", {})
            norm_markets = list(temp.values())
            canon_keys = list(set(m["market_key"] for m in norm_markets))
            game["normalized_markets"] = norm_markets
            game["canonical_markets"] = canon_keys
            final_games.append(game)
            
        return {
            "player_props": [],
            "games": final_games,
            "book": {
                "id": self.BOOK_ID,
                "key": self.BOOK_KEY,
                "name": self.BOOK_NAME,
            },
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_game_info(self, event: Dict[str, Any]) -> Dict[str, Any]:
        teams = event.get("teams", [])
        home_team = {}
        away_team = {}
        home_id = event.get("homeTeamId")
        away_id = event.get("awayTeamId")
        
        for t in teams:
            tid = t.get("teamId")
            if tid == home_id:
                home_team = t
            elif tid == away_id:
                away_team = t
                
        return {
            "game_id": event.get("eventId"),
            "start_time": event.get("gameDate"),
            "home_team": home_team.get("key"),  
            "away_team": away_team.get("key"),
            "home_team_full": home_team.get("fullName"),
            "away_team_full": away_team.get("fullName"),
        }

    def _parse_market_type(self, raw: str) -> Tuple[str, str]:
        raw_lower = raw.lower()
        period = "game"
        clean_name = raw
        
        if "1st half" in raw_lower:
            period = "1h"
            clean_name = re.sub(r"1st half", "", raw, flags=re.IGNORECASE)
        elif "2nd half" in raw_lower:
            period = "2h"
            clean_name = re.sub(r"2nd half", "", raw, flags=re.IGNORECASE)
        elif "1st quarter" in raw_lower:
            period = "1q"
            clean_name = re.sub(r"1st quarter", "", raw, flags=re.IGNORECASE)
        elif "2nd quarter" in raw_lower:
            period = "2q"
            clean_name = re.sub(r"2nd quarter", "", raw, flags=re.IGNORECASE)
        elif "3rd quarter" in raw_lower:
            period = "3q"
            clean_name = re.sub(r"3rd quarter", "", raw, flags=re.IGNORECASE)
        elif "4th quarter" in raw_lower:
            period = "4q"
            clean_name = re.sub(r"4th quarter", "", raw, flags=re.IGNORECASE)
            
        clean_name = clean_name.strip()
        cn_lower = clean_name.lower()
        if "point spread" in cn_lower:
            return period, "spread"
        if "total points" in cn_lower:
            return period, "total"
        if "moneyline" in cn_lower:
            return period, "moneyline"
            
        return period, clean_name

    def get_supported_sports(self) -> List[str]:
        return list(SharpOddsClient.SPORT_MAP.keys())

    def get_sport_name(self, sport: str) -> str:
        return SharpOddsClient.SPORT_MAP.get(sport, sport)

    async def health_check(self) -> bool:
        return True


# --- Dynamic Class Generation ---
SHARP_ODDS_STREAMERS: Dict[str, Type[_SharpBookOddsStreamer]] = {}

for book_id, key, name in _SHARP_BOOK_DATA:
    full_key = f"{SHARP_KEY_PREFIX}{key}"
    class_name = f"Sharp{name.replace(' ', '')}Streamer"
    
    streamer_cls = type(
        class_name,
        (_SharpBookOddsStreamer,),
        {
            "BOOK_ID": book_id,
            "BOOK_KEY": full_key,
            "BOOK_NAME": name,
            "__module__": __name__,
        },
    )
    SHARP_ODDS_STREAMERS[full_key] = streamer_cls
    globals()[class_name] = streamer_cls

__all__ = ["SHARP_ODDS_STREAMERS"] + [cls.__name__ for cls in SHARP_ODDS_STREAMERS.values()]

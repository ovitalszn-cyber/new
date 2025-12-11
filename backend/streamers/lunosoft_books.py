"""Per-book streamers backed by the Lunosoft Live Odds service."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type

from streamers.base import BaseStreamer
from streamers.lunosoft import LunosoftClient


class _LunosoftBookStreamer(BaseStreamer):
    """Base class for per-book Lunosoft connectors."""

    BOOK_ID: int = -1
    BOOK_KEY: str = ""
    BOOK_NAME: str = ""

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self._client = LunosoftClient(config)

    async def connect(self) -> bool:
        return await self._client.connect()

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def fetch_data(self, sport: Optional[str] = None) -> Dict[str, Any]:
        return await self._client.fetch_book_props(self.BOOK_ID, sport)

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        player_props: List[Dict[str, Any]] = []

        if not raw_data:
            return {
                "player_props": player_props,
                "book": {
                    "id": self.BOOK_ID,
                    "key": self.BOOK_KEY,
                    "name": self.BOOK_NAME,
                },
                "processed_at": datetime.utcnow().isoformat(),
            }

        for sport_section in raw_data.get("sports", []):
            props = sport_section.get("props", [])
            for prop in props:
                enriched = dict(prop)
                enriched["source"] = self.BOOK_KEY
                enriched["book_id"] = self.BOOK_ID
                enriched["book_name"] = self.BOOK_NAME
                player_props.append(enriched)

        return {
            "player_props": player_props,
            "sports": raw_data.get("processed_sports", []),
            "requested_sport": raw_data.get("requested_sport"),
            "book": {
                "id": self.BOOK_ID,
                "key": self.BOOK_KEY,
                "name": self.BOOK_NAME,
            },
            "processed_at": datetime.utcnow().isoformat(),
        }

    def get_supported_sports(self) -> List[str]:
        return self._client.get_supported_sports()

    def get_sport_name(self, sport: str) -> str:
        return self._client.get_sport_name(sport)

    async def health_check(self) -> bool:
        try:
            payload = await self._client.fetch_book_props(self.BOOK_ID, "americanfootball_nfl")
            props = payload.get("sports", [{}])[0].get("props", []) if payload.get("sports") else []
            return len(props) > 0
        except Exception:
            return False


def _sanitize_class_name(book_name: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", book_name).title().replace(" ", "")
    if not cleaned:
        cleaned = "Book"
    if cleaned[0].isdigit():
        cleaned = f"Book{cleaned}"
    return f"{cleaned}PropsStreamer"


def _sanitize_key(book_name: str) -> str:
    key = re.sub(r"[^0-9A-Za-z]+", "_", book_name).lower().strip("_")
    if not key:
        key = "book"
    return key


# Source: lunosoft curls provided by user
_LUNOSOFT_BOOK_DATA: Tuple[Tuple[int, str, str], ...] = (
    (1, "pinnacle", "Pinnacle"),
    (2, "bodog", "Bodog"),
    (3, "betcris", "BetCRIS"),
    (5, "bookmaker", "BookMaker"),
    (7, "bovada", "Bovada"),
    (13, "williamhill", "William Hill"),
    (17, "bwin", "bwin"),
    (20, "sportsbet", "Sportsbet"),
    (28, "caesars", "Caesars"),
    (37, "betfair", "BetFair"),
    (83, "draftkings", "DraftKings"),
    (85, "betrivers", "BetRivers"),
    (86, "pointsbet", "PointsBet"),
    (87, "betmgm", "BetMGM"),
    (88, "unibet", "Unibet"),
    (89, "fanduel", "FanDuel"),
    (90, "1xbet", "1xBet"),
    (91, "888sport", "888sport"),
    (93, "ballybet", "Bally Bet"),
    (94, "hardrock", "Hard Rock"),
    (95, "circasports", "Circa Sports"),
    (97, "sporttrade", "Sporttrade"),
    (98, "bet99", "BET99"),
    (101, "betano", "Betano"),
    (106, "betopenly", "BetOpenly"),
    (107, "betparx", "betPARX"),
    (109, "betr", "Betr"),
    (110, "betsafe", "Betsafe"),
    (113, "borgata", "Borgata"),
    (118, "espnbet", "ESPN BET"),
    (119, "fanatics", "Fanatics"),
    (122, "ladbrokes", "Ladbrokes"),
    (125, "partypoker", "partypoker"),
    (130, "prophetx", "Prophet X"),
    (135, "sugarhouse", "SugarHouse"),
    (139, "thescore", "theScore"),
    (141, "twinspires", "TwinSpires"),
    (147, "novig", "Novig"),
)

LUNOSOFT_BOOK_STREAMERS: Dict[str, Type[_LunosoftBookStreamer]] = {}

for book_id, key, name in _LUNOSOFT_BOOK_DATA:
    book_key = key or _sanitize_key(name)
    class_name = _sanitize_class_name(name)
    streamer_cls = type(
        class_name,
        (_LunosoftBookStreamer,),
        {
            "BOOK_ID": book_id,
            "BOOK_KEY": book_key,
            "BOOK_NAME": name,
            "__module__": __name__,
        },
    )
    LUNOSOFT_BOOK_STREAMERS[book_key] = streamer_cls
    globals()[class_name] = streamer_cls

__all__ = [
    "_LunosoftBookStreamer",
    "LUNOSOFT_BOOK_STREAMERS",
] + [cls.__name__ for cls in LUNOSOFT_BOOK_STREAMERS.values()]

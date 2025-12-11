"""ProphetX data streamer that returns raw API payloads."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import structlog

from .base import BaseStreamer

logger = structlog.get_logger()


class ProphetXStreamer(BaseStreamer):
    """Streamer for ProphetX sportsbook data returning raw JSON."""

    BASE_URL = "https://cash.api.prophetx.co/trade/public/api"

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Origin": "https://app.prophetx.co",
        "Referer": "https://app.prophetx.co/",
    }

    SPORT_TOURNAMENT_IDS: Dict[str, List[int]] = {
        "baseball_mlb": [109],
        "football_nfl": [31],
        "football_ncaaf": [27653],
        "basketball_wnba": [1600000176],
    }

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)

        self.sport = config.get("sport", "football_nfl")
        self.event_limit = int(config.get("event_limit", 250))
        self.include_future_days = int(config.get("future_days", 7))
        self.params_override: Dict[str, Any] = config.get("event_params", {})
        self.market_delay = float(config.get("market_delay", 0.1))

        self.client: Optional[httpx.AsyncClient] = None

        self.tournament_ids = self.SPORT_TOURNAMENT_IDS.get(self.sport, [])
        if not self.tournament_ids:
            raise ValueError(f"Unsupported sport for ProphetX streamer: {self.sport}")

        logger.info(
            "Initialized ProphetX streamer",
            sport=self.sport,
            tournament_ids=self.tournament_ids,
            event_limit=self.event_limit,
        )

    async def connect(self) -> bool:
        """Create an HTTP client and validate connectivity."""
        headers = {**self.DEFAULT_HEADERS}

        self.client = httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True)

        test_tournament = self.tournament_ids[0]
        try:
            params = self._build_event_params()
            response = await self.client.get(
                f"{self.BASE_URL}/v1/tournaments/{test_tournament}/events",
                params=params,
            )
            response.raise_for_status()
            response.json()
            logger.info("Connected to ProphetX API", sport=self.sport)
            return True
        except Exception as exc:
            logger.error("Failed to connect to ProphetX API", sport=self.sport, error=str(exc))
            if self.client:
                await self.client.aclose()
            self.client = None
            return False

    async def disconnect(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from ProphetX API")
            self.client = None

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch raw events and markets for the configured sport."""
        if not self.client:
            raise RuntimeError("ProphetX client is not connected")

        events_by_tournament: Dict[str, Dict[str, Any]] = {}
        markets_by_event: Dict[str, Dict[str, Any]] = {}

        params = self._build_event_params()

        for tournament_id in self.tournament_ids:
            try:
                events_response = await self._get_events(tournament_id, params)
                events_by_tournament[str(tournament_id)] = {
                    "request": {"params": params},
                    "response": events_response,
                }

                events = events_response.get("data", []) if isinstance(events_response, dict) else []
                event_count = 0

                for event in events:
                    event_id = str(event.get("id")) if isinstance(event, dict) else None
                    if not event_id:
                        continue

                    if event_count >= self.event_limit:
                        break

                    try:
                        markets_response = await self._get_markets(event_id)
                        markets_by_event[event_id] = {
                            "response": markets_response,
                            "event": event,
                        }
                    except Exception as market_exc:
                        logger.warning(
                            "Error fetching ProphetX markets",
                            sport=self.sport,
                            event_id=event_id,
                            error=str(market_exc),
                        )
                        continue

                    event_count += 1
                    await asyncio.sleep(self.market_delay)

            except Exception as exc:
                logger.error(
                    "Error fetching ProphetX events",
                    sport=self.sport,
                    tournament_id=tournament_id,
                    error=str(exc),
                )
                continue

        return {
            "sport": self.sport,
            "tournament_ids": self.tournament_ids,
            "events": events_by_tournament,
            "markets": markets_by_event,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return raw ProphetX payload and a compact view with odds from selections."""
        events = raw_data.get("events", {})
        markets = raw_data.get("markets", {})

        total_events = sum(
            len(info.get("response", {}).get("data", []))
            for info in events.values()
            if isinstance(info, dict)
        )
        total_markets = sum(
            len(resp.get("response", {}).get("data", {}).get("markets", []))
            for resp in markets.values()
            if isinstance(resp, dict)
        )

        # Build a compact, terminal-friendly view that extracts odds from selections
        compact_events: List[Dict[str, Any]] = []
        for _, bundle in markets.items():
            if not isinstance(bundle, dict):
                continue
            event_obj = bundle.get("event") or {}
            event_name = event_obj.get("name") or event_obj.get("description") or "Unknown Event"
            resp = (bundle.get("response") or {}).get("data") or {}
            mlist = resp.get("markets") or []

            std_markets: List[Dict[str, Any]] = []
            for m in mlist:
                try:
                    mtype = m.get("type") or m.get("name") or "market"
                    selections = m.get("selections")
                    if not selections or not isinstance(selections, list) or len(selections) == 0:
                        continue
                    outcomes: List[Dict[str, Any]] = []
                    # Selections is usually a list of sides (e.g., [homePrices[], awayPrices[]])
                    for side in selections[:2]:
                        if isinstance(side, list) and len(side) > 0 and isinstance(side[0], dict):
                            top = side[0]
                            outcomes.append({
                                "name": top.get("abbreviatedName") or top.get("displayName") or top.get("name") or "",
                                "price": top.get("odds"),
                                "line": top.get("line"),
                            })
                    if outcomes:
                        std_markets.append({"type": mtype, "outcomes": outcomes})
                except Exception:
                    continue

            if std_markets:
                compact_events.append({"event": event_name, "markets": std_markets})

        return {
            "book": "prophetx",
            "sport": raw_data.get("sport"),
            "tournament_ids": raw_data.get("tournament_ids"),
            "raw_events": events,
            "raw_markets": markets,
            "compact": compact_events,
            "fetched_at": raw_data.get("fetched_at"),
            "metadata": {
                "total_events": total_events,
                "total_markets": total_markets,
                "has_odds": True,
                "has_multipliers": False,
                "market_types": ["moneyline", "spread", "total", "player_props", "game_props"],
                "book_type": "sportsbook",
            },
        }

    async def _get_events(self, tournament_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        assert self.client is not None
        response = await self.client.get(
            f"{self.BASE_URL}/v1/tournaments/{tournament_id}/events",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    async def _get_markets(self, event_id: str) -> Dict[str, Any]:
        assert self.client is not None
        response = await self.client.get(f"{self.BASE_URL}/v2/events/{event_id}/markets")
        response.raise_for_status()
        return response.json()

    def _build_event_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "limit": str(self.event_limit),
            "t": str(int(datetime.utcnow().timestamp())),
        }

        try:
            params["from"] = datetime.utcnow().strftime("%Y-%m-%d")
            params["to"] = (datetime.utcnow() + timedelta(days=self.include_future_days)).strftime("%Y-%m-%d")
        except Exception:
            pass

        params.update(self.params_override)
        return params

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        return list(cls.SPORT_TOURNAMENT_IDS.keys())

    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        if sport not in cls.SPORT_TOURNAMENT_IDS:
            raise ValueError(f"Unsupported ProphetX sport: {sport}")
        return {
            "sport": sport,
            "event_limit": 250,
            "future_days": 7,
            "market_delay": 0.1,
        }

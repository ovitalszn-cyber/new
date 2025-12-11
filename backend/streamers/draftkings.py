"""DraftKings streamer that fetches live data from DraftKings Sportsbook API."""

import asyncio
import httpx
import structlog
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .base import BaseStreamer

logger = structlog.get_logger(__name__)


class DraftKingsStreamer(BaseStreamer):
    """Streamer that fetches live data from DraftKings Sportsbook API."""

    # Sport mapping to DraftKings sport keys
    SPORT_CONFIG = {
        # Academy Awards
        "academy_awards": {"sport_key": "207365", "name": "Academy Awards"},
        
        # Aussie Rules
        "aussie_rules": {"sport_key": "79494", "name": "AFL"},
        
        # Baseball
        "baseball_mlb": {"sport_key": "84240", "name": "MLB"},
        
        # Basketball
        "basketball_wnba": {"sport_key": "94682", "name": "WNBA"},
        "basketball_nba_preseason": {"sport_key": "79507", "name": "NBA Preseason"},
        "basketball_nba": {"sport_key": "42648", "name": "NBA"},
        "basketball_ncaab": {"sport_key": "92483", "name": "College Basketball (M)"},
        "basketball_wncaab": {"sport_key": "36647", "name": "College Basketball (W)"},
        
        # Boxing
        "boxing": {"sport_key": "72061", "name": "Boxing"},
        
        # Cricket
        "cricket": {"sport_key": "89725", "name": "Test Matches"},
        
        # Darts
        "darts": {"sport_key": "204787", "name": "Modus Super Series"},
        
        # E-Sports
        "esports_lol": {"sport_key": "72976", "name": "League of Legends World Championship"},
        
        # Football
        "americanfootball_nfl": {"sport_key": "88808", "name": "NFL"},
        "americanfootball_ncaaf": {"sport_key": "87637", "name": "College Football"},
        
        # Golf
        "golf": {"sport_key": "82839", "name": "Sanderson Farms"},
        "golf_masters": {"sport_key": "92694", "name": "The Masters"},
        "golf_ryder_cup": {"sport_key": "16936", "name": "Ryder Cup"},
        
        # Hockey
        "icehockey_nhl": {"sport_key": "42133", "name": "NHL"},
        "icehockey_ncaa": {"sport_key": "84813", "name": "College Hockey"},
        "icehockey_finnish": {"sport_key": "40480", "name": "Finnish - SM Liiga"},
        "icehockey_swedish": {"sport_key": "38522", "name": "Sweden - SHL"},
        
        # Jai Alai
        "jai_alai": {"sport_key": "210578", "name": "World Jai Alai League"},
        
        # Lacrosse
        "lacrosse": {"sport_key": "207131", "name": "National Lacrosse League"},
        
        # MMA
        "mma": {"sport_key": "9034", "name": "UFC"},
        
        # Motorsports
        "motorsports_f1": {"sport_key": "212334", "name": "Formula 1"},
        "motorsports_nascar": {"sport_key": "87556", "name": "NASCAR Cup Races"},
        "motorsports_nhra": {"sport_key": "199216", "name": "NHRA Drag Racing"},
        
        # Soccer
        "soccer_mls": {"sport_key": "89345", "name": "MLS"},
        "soccer_mexico": {"sport_key": "44525", "name": "Mexico - Liga MX"},
        "soccer_argentina": {"sport_key": "59107", "name": "Argentina - Liga Profesional"},
        "soccer_nwsl": {"sport_key": "37539", "name": "NWSL"},
        "soccer_bundesliga": {"sport_key": "40481", "name": "Germany - Bundesliga"},
        
        # Table Tennis
        "table_tennis": {"sport_key": "208037", "name": "TT Elite Series"},
        
        # Tennis
        "tennis_atp": {"sport_key": "78722", "name": "ATP - Shanghai"},
        "tennis_atp_doubles": {"sport_key": "78733", "name": "ATP Doubles - Shanghai"},
        
        # Winter Olympics
        "winter_olympics": {"sport_key": "207445", "name": "Medal Market Specials"},
    }

    # Default headers for DraftKings API
    DEFAULT_HEADERS = {
        "content-type": "application/json",
        "x-client-name": "sbios",
        "accept": "application/json",
        "x-dk-device-appname": "sbios",
        "x-client-version": "5.29.4",
        "x-client-template-id": "b6f414b8-c1ca-4040-ab9d-0492a805d532__client_sbandroid_5.26_sbios_5.26",
        "x-dk-device-idfa": "00000000-0000-0000-0000-000000000000",
        "priority": "u=3",
        "x-dk-device-idfv": "E08EFBD4-5C73-4308-A47F-52195822E184",
        "accept-language": "en-US,en;q=0.9",
        "x-dk-device-version": "5.29.4",
        "x-dk-device-isadtrackingenabled": "false",
        "user-agent": "sbios/5.29.4 (iOS; iPhone13,4; iOS26.0.0)",
        "cookie": "bm_sv=6591D62A6510B69C8D6751469A5D3F07~YAAQZavWF6Wk4JeZAQAAOIAXth1CAgEepZ0bmE/QHZNI575IKqijGMg9w8DDKtTTqXn67Tkn/E+HgCVHVEQueEoH5OMEcIfiBydLpP35mfNCzC1wdXMc/3wT/sYcEITSyXRNt88A0JxqVO0Pj0/ecHqDudkaPJWVPdnb//SPjMbiFMeNekz/vFhPQTGfxjsXdWHUxT+s8kYrrrDBVGAt90TyQRa62NsYqFP/wO/lIXJOfLpD4YdVjyUY8gOmRf4NH7TBmp4=~1; STE=\"2025-10-05T21:06:54.3492184Z\"; ak_bmsc=B5793E25283AE09F1984D31FB117EA2D~000000000000000000000000000000~YAAQZavWFxl54JeZAQAAkX0Wth3PvyvtCTXWZdnC0UMggGWCHMo+QExSCRHEIKV1vRjXrs0vFetYjcPafh22WYy7fu7LtO/XwHwePDXw2JieKyjoJtPQ40oW/fZyQBaWlgU0bU+L0W8xJZBbfM1XDU9pvlqE1UrKOf6D4bl41rZB0L7AebAsg3EybpTNmKRDohnjTLom8PzwZtohSxn6cg0SzFJlzNRW9taHEksxI4JuGRX8iV5hnGLz5Ycz13G764vU7c+D7VIZhalda30wdCJ7c2TsosyTzyDDQzj5QAymykW3DHhb8f116mzYWVP/EN2hc4aiY+LUtfE1qTZsYcRLY4Xirlzbh0VLaiu3QrfBtv4HjBrLFlfmK/avrJCVBaZgJRGJpdOIswxcR/JzW6zSRbnAL1wNxA3IMO9/7mNmrV9mZv3WV0nxOfL2rRLlzK0/IO7B7hg=; _abck=BB2348FA26AF00C89537180F4F73116D~-1~YAAQZKvWF1C0VJaZAQAAY3gWtg5fKKcDk7hT2jB6FLNmmgGXNLycdWMkb7Q76qVWbeHnq18kmnZgaeCQrdUnSUezCNKbo+OiM5IMgT2wDTothNd29hBh6ZPDofBzYwflzVXdqffVcWyubQLdW+jQCyk7Y+WzRGjFCSgfCiafAwLaVlmL7W5U5IqJIycMv8fXMa0tD6qwRN5NJd5vhVxAD7m/qpFa4Wya6Xb/Xk3Yid5688kxi6smUyPf/yoE4ckhJyrtsneGW7X5GZpM+U//fc72nviPE0qOWfNvc6a4P8MpMo1+SmLgltWN/oBeNUtSJsV/9M7XI0H4NoWjzCug2QQIgUHhUF7xoM7a9/YyREuRlj0ta9I7NzJtM6s4u2orG4AItd4TbjemH5Fnm9sKzAqJxKxPWY7wntedCjD0/Eoa88FG4Di5B4h5kQrioUTCIL1ExjSpthFZyvfTlY3K2WmcINCoYv0sp7sl179AxUBzdMFy0JaY94Cbnza1ztmWH3vnxfyampWXDGxB2deHYvr50b7sWaUWDyhQG/fentfS8LnyVuHyjL02QPFymZfmeV+HxaQ0aCGCAT8GFoBqOptfoO9HLS00UjQn6e3R3/IMDkeUwgUxtEx4F+m/PTyAUBLAr1rokec=~-1~-1~-1~-1~-1; bm_sz=760AB56564251BAE76882A324C808FD3~YAAQZKvWF1K0VJaZAQAAY3gWth2WVmG1ZVA6r+y8GeF7owleiC2oygdvtyC8EATqsle4abExYkUPYd3k3KQiq59UPnMqLY2nBr8HNAguMBOiHUpQa9Ydhh/aa967vayAGzYgTVpjOEBPiCYRMfHl/hXaflnv3GV8OuPHb8OGWyvpYk6yd8wCRy0kwVELMKZfWHbl/Enctu7/+kvDLIzX6bDeNrVkHq17AWUC7KtWkl96Jt6lW+EuIVmBCWXJjS1kNUcwRiEAxgVULIYQDypBanxDhVAnQnyjSNwEOX3GTJM5+jHXZ2JWlWeA1e1oOgNwK5EiCwk5TVrSvqxWcKZUrPwEZNemMUECZ6iTLvfdRl7VVqcjGAagbePJL7pf+owybLFiLRr+HQCvKIShDIw9UtZT~3356726~3749169; STH=cc279b31900c4d5703456006f146057c461953b6fac4afb90012beb3899e2c45; STIDN=eyJDIjoxMjIzNTQ4NTIzLCJTIjoxMTgzMDAzNzE2MzgsIlNTIjoxMjI0MjM5MjExMjYsIlYiOjcxNDMwNjc4NDI2LCJMIjoxLCJFIjoiMjAyNS0xMC0wNVQyMTowNTo0OS4zNjMyNDU2WiIsIlNFIjoiVVMtREsiLCJVQSI6Im9McVNscFB1UncyQUZDOVRVREdERGk1MzF3SExUUUhXQjdNRllhRkNLL289IiwiREsiOiJhY2NlZmUzZS0zOGQ0LTRiNjYtYWYwYy04YTNiMGQ1N2U2M2IiLCJESSI6IjY1OGUxMDhiLWQ1NzMtNDAzZC05MTllLTkzMWUxYWM4ZDJmYiIsIkREIjo4NDk0NDY2NDM5N30=; _csrf=f0525620-1619-4ec2-a6e6-59d1300e8dff; hgg=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWQiOiI3MTQzMDY3ODQyNiIsImRraC0xMjYiOiI4MzNUZF9ZSiIsImRrZS0xMjYiOiIwIiwiZGtlLTIwNCI6IjcxMCIsImRrZS0yODgiOiIxMTI4IiwiZGtlLTMxOCI6IjEyNjAiLCJka2UtMzQ1IjoiMTM1MyIsImRrZS0zNDYiOiIxMzU2IiwiZGtlLTQyOSI6IjE3MDUiLCJka2UtNzAwIjoiMjk5MiIsImRrZS03MzkiOiIzMTQwIiwiZGtlLTc1NyI6IjMyMTIiLCJka2UtODA2IjoiMzQyNSIsImRrZS04MDciOiIzNDM3IiwiZGtlLTgyNCI6IjM1MTEiLCJka2UtODI1IjoiMzUxNCIsImRrZS04MzYiOiIzNTcwIiwiZGtoLTg5NSI6IjhlU3ZaRG8wIiwiZGtlLTg5NSI6IjAiLCJka2UtOTAzIjoiMzg0OCIsImRrZS05MTciOiIzOTEzIiwiZGtlLTk0NyI6IjQwNDIiLCJka2UtOTc2IjoiNDE3MSIsImRraC0xNjQxIjoiUjBrX2xta0ciLCJka2UtMTY0MSI6IjAiLCJka2UtMTY1MyI6IjcxMzEiLCJka2UtMTY4NiI6IjcyNzEiLCJka2UtMTY4OSI6IjcyODciLCJka2UtMTc1NCI6Ijc2MDUiLCJka2UtMTc2MCI6Ijc2NDkiLCJka2UtMTc3NCI6Ijc3MDkiLCJka2UtMTc5NCI6Ijc4MDEiLCJka2gtMTgwNSI6Ik9Ha2Jsa0h4IiwiZGtlLTE4MDUiOiIwIiwiZGtlLTE4MjgiOiI3OTU2IiwiZGtlLTE4NjEiOiI4MTU3IiwiZGtlLTE4NjgiOiI4MTg4IiwiZGtlLTE4OTgiOiI4MzEzIiwiZGtoLTE5NTIiOiJhVWdlRFhiUSIsImRrZS0xOTUyIjoiMCIsImRrZS0yMDk3IjoiOTIwNSIsImRrZS0yMTAwIjoiOTIyMyIsImRrZS0yMTM1IjoiOTM5MyIsImRraC0yMTUwIjoiTmtiYVNGOGYiLCJka2UtMjE1MCI6IjAiLCJka2UtMjE5NSI6Ijk2NjUiLCJka2UtMjIyNCI6Ijk3ODMiLCJka2UtMjIyNiI6Ijk3OTAiLCJka2UtMjIzNyI6Ijk4MzQiLCJka2UtMjIzOCI6Ijk4MzciLCJka2UtMjI0MCI6Ijk4NTciLCJka2UtMjI0NiI6Ijk4ODciLCJka2UtMjMyNCI6IjEwMzI0IiwiZGtlLTIzMjgiOiIxMDMzOCIsImRrZS0yMzMzIjoiMTAzNzEiLCJka2UtMjMzOSI6IjEwMzk2IiwiZGtlLTIzNDIiOiIxMDQxMSIsImRka2UtMjM1MiI6IjEwNDgzIiwiZGtlLTIzNTkiOiIxMDUxOCIsImRka2UtMjM2NSI6IjEwNTQ1IiwiZGtlLTIzNjYiOiIxMDU0OSIsImRka2UtMjM4OCI6IjEwNjUxIiwiZGtlLTI0MDMiOiIxMDc2MiIsImRka2UtMjQxOCI6IjEwODUzIiwiZGtlLTI0MjAiOiIxMDg2MiIsImRka2UtMjQyMSI6IjEwODY1IiwiZGtlLTI0MjMiOiIxMDg3MSIsImRka2UtMjQyNyI6IjEwODk2IiwiZGtlLTI0MjkiOiIxMDkwMyIsImRka2UtMjQzMSI6IjEwOTA4IiwiZGtlLTI0MzQiOiIxMDkxOSIsImRka2UtMjQzNSI6IjEwOTIyIiwiZGtlLTI0MzYiOiIxMDkzMiIsImRka2gtMjQzNyI6IkNSMk03TkdvIiwiZGtlLTI0MzciOiIwIiwiZGtlLTI0NDAiOiIxMDk1MCIsImRka2gtMjQ0NyI6IjlfRXRGRlFUIiwiZGtlLTI0NDciOiIwIiwiZGtlLTI0NTEiOiIxMDk5MiIsImRka2UtMjQ1OCI6IjExMDE5IiwiZGtlLTI0NTkiOiIxMTAyMyIsImRka2UtMjQ2MCI6IjExMDI1IiwiZGtlLTI0NjEiOiIxMTAyOCIsImRka2UtMjQ2NiI6IjExMDM0IiwiZGtlLTI0NjkiOiIxMTA0MCIsImRka2UtMjQ3NSI6IjExMDYxIiwiZGtoLTI0NzYiOiJfU201QUYyUyIsImRka2UtMjQ3NiI6IjAiLCJka2UtMjQ3NyI6IjExMDcxIiwiZGtlLTI0NzgiOiIxMTA3NSIsImRka2UtMjQ4NiI6IjExMTEwIiwiZGtlLTI0OTEiOiIxMTEyNiIsImRka2gtMjQ5MiI6IlNXOEJGajY2IiwiZGtlLTI0OTIiOiIwIiwiZGtoLTI0OTMiOiJVOVFYRHA2USIsImRka2UtMjQ5MyI6IjAiLCJka2gtMjQ5NCI6IjRXSS1lZ0t6IiwiZGtlLTI0OTQiOiIwIiwibmJmIjoxNzU5Njk2NTQ5LCJleHAiOjE3NTk2OTY4NDksImlhdCI6MTc1OTY5NjU0OSwiaXNzIjoiZGsifQ.2FU-AHcAUA9h5upHWfbWZMxsCOa4Y_XeCMOoNLT6Os4; Native=appId=sbios&osType=ios&osv=26.0&appVersion=5.29.4&make=Apple&model=iPhone13_4&adId=00000000-0000-0000-0000-000000000000&DI=&DK=&appName=SB&appname=SB&dId=E08EFBD4-5C73-4308-A47F-52195822E184&language=en; ab.storage.sessionId.9d77303b-c984-428b-9d54-2c42d6280e3a=%7B%22g%22%3A%22cce3e6e7-ac17-d9e2-789f-ed86dd4dece3%22%2C%22e%22%3A1754796967750%2C%22c%22%3A1754795167751%2C%22l%22%3A1754795167751%7D; ab.storage.deviceId.9d77303b-c984-428b-9d54-2c42d6280e3a=%7B%22g%22%3A%227feadf02-c39e-6a6a-c284-849f7f76a58a%22%2C%22c%22%3A1751839330108%2C%22l%22%3A1751839330108%7D"
    }

    BASE_URL = "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets"

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """Connect to DraftKings API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to DraftKings API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to DraftKings API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from DraftKings API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from DraftKings API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from DraftKings API for a specific sport."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to DraftKings API")
            return None

        # Use sport from config if not provided
        if sport is None:
            sport = self.config.get("sport", "basketball_nba")

        sport_config = self.SPORT_CONFIG.get(sport)
        if not sport_config:
            logger.warning(f"Unsupported sport: {sport}")
            return None

        try:
            # Use the sport_key as league_id, but use 4511 as subcategory_id for NBA
            league_id = sport_config['sport_key']
            subcategory_id = "4511"  # NBA subcategory ID from working curl
            
            params = {
                "appname": "sbios",
                "version": "5.29.4",
                "eventsQuery": f"$filter=leagueId eq '{league_id}' AND clientMetadata/Subcategories/any(s: s/Id eq '{subcategory_id}')",
                "marketsQuery": f"$filter=clientMetadata/subCategoryId eq '{subcategory_id}' AND tags/all(t: t ne 'SportcastBetBuilder')",
                "include": "Events",
                "format": "json"
            }

            logger.info(f"Fetching DraftKings data for sport: {sport} ({sport_config['sport_key']})")
            
            response = await self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched DraftKings data for {sport}")
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching DraftKings data for {sport}: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error fetching DraftKings data for {sport}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching DraftKings data for {sport}: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw DraftKings data into standardized format."""
        try:
            if not raw_data:
                logger.warning("No data found in DraftKings response")
                return {"markets": [], "events": [], "total_markets": 0, "total_events": 0, "processed_at": datetime.now(timezone.utc).isoformat()}
            
            # DraftKings API returns data directly with keys like 'events', 'markets', etc.
            markets_data = raw_data.get("markets", [])
            events_data = raw_data.get("events", [])
            
            processed_data = {
                "markets": markets_data,
                "events": events_data,
                "total_markets": len(markets_data),
                "total_events": len(events_data),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed DraftKings data: {len(markets_data)} markets, {len(events_data)} events")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process DraftKings data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        return list(self.SPORT_CONFIG.keys())

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_config = self.SPORT_CONFIG.get(sport)
        return sport_config["name"] if sport_config else sport

    async def health_check(self) -> bool:
        """Check if DraftKings API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with NBA data
            data = await self.fetch_data("basketball_nba")
            return data is not None and "data" in data

        except Exception as e:
            logger.error(f"DraftKings health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"DraftKingsStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()

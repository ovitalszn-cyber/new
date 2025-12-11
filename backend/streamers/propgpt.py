"""PropGPT streamer that fetches AI-analyzed top bet recommendations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class PropGPTStreamer(BaseStreamer):
    """Streamer that fetches AI-analyzed top bets from PropGPT."""

    BASE_URL = "https://us-central1-bestbet-d4d6b.cloudfunctions.net/homepage_endpoint"
    
    DEFAULT_HEADERS = {
        "accept": "*/*",
        "user-agent": "PropGPT/218 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3, i",
        "accept-language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """Connect to PropGPT API."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            self.is_connected = True
            logger.info("Connected to PropGPT API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PropGPT API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from PropGPT API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from PropGPT API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from PropGPT API."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to PropGPT API")
            return None

        try:
            logger.info(f"Fetching PropGPT top bets")
            
            response = await self.session.get(self.BASE_URL)
            response.raise_for_status()
            
            data = response.json()
            
            # Add metadata
            data["fetched_at"] = datetime.now(timezone.utc).isoformat()
            
            top_bets_count = len(data.get("top_bets", []))
            logger.info(f"Fetched PropGPT data: {top_bets_count} top bets")
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching PropGPT data: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error fetching PropGPT data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching PropGPT data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw PropGPT data into standardized format."""
        try:
            if not raw_data:
                return {"error": "No data found in PropGPT response"}
            
            top_bets = raw_data.get("top_bets", [])
            
            # Process bets into player_props format
            player_props = []
            for bet in top_bets:
                if not isinstance(bet, dict):
                    continue
                
                analysis = bet.get("analysis", {})
                input_data = analysis.get("input", {})
                
                # Extract player info - player_id is a long number, we'll use it as-is
                player_id = input_data.get("player_id")
                if not player_id:
                    continue
                
                # Get stat type and line
                stat_type = input_data.get("stat", "")
                line = input_data.get("line")
                direction = analysis.get("over_under", "")
                
                # Get team and opponent
                team = input_data.get("team_code", "")
                opponent = input_data.get("opponent_abv", "")
                
                # Get AI analysis
                grade = analysis.get("grade")  # 0-100 score
                insights = analysis.get("insights", [])
                short_answer = analysis.get("short_answer", "")
                long_answer = analysis.get("long_answer", "")
                injury = analysis.get("injury")
                league = analysis.get("league", "")
                
                player_props.append({
                    "bet_id": bet.get("id"),
                    "player_id": str(player_id),
                    "player_name": None,  # PropGPT doesn't provide player name directly
                    "team": team,
                    "opponent": opponent,
                    "stat_type": stat_type,
                    "line": line,
                    "direction": direction,
                    "odds": None,  # PropGPT doesn't provide odds
                    "book": "propgpt",
                    "league": league,
                    # AI Analysis
                    "grade": grade,  # 0-100 confidence score
                    "insights": insights,  # List of AI insights
                    "short_answer": short_answer,
                    "long_answer": long_answer,
                    "injury": injury,
                    "insights_count": len(insights),
                })
            
            processed_data = {
                "player_props": player_props,
                "total_bets": len(player_props),
                "game_tags": raw_data.get("game_tags", {}),
                "fetched_at": raw_data.get("fetched_at"),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed PropGPT data: {len(player_props)} AI-analyzed bets")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process PropGPT data: {e}")
            return {"error": str(e)}

    def get_supported_sports(self) -> List[str]:
        """Get list of supported sports."""
        # PropGPT returns whatever sports it has analyzed
        return ["basketball_nba", "americanfootball_nfl", "baseball_mlb", "icehockey_nhl"]

    def get_sport_name(self, sport: str) -> str:
        """Get display name for a sport."""
        sport_map = {
            "basketball_nba": "NBA",
            "americanfootball_nfl": "NFL",
            "baseball_mlb": "MLB",
            "icehockey_nhl": "NHL",
        }
        return sport_map.get(sport, sport)

    async def health_check(self) -> bool:
        """Check if PropGPT API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test fetch
            data = await self.fetch_data()
            return data is not None and len(data.get("top_bets", [])) > 0

        except Exception as e:
            logger.error(f"PropGPT health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"PropGPTStreamer(name={self.name}, connected={self.is_connected})"

    def __repr__(self) -> str:
        return self.__str__()

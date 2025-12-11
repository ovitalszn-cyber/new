"""Action Network streamer that collects EV projections and player props."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

from streamers.base import BaseStreamer
from v6.clients.actionnetwork import ActionNetworkClient

logger = structlog.get_logger()


class ActionNetworkStreamer(BaseStreamer):
    """Streamer that fetches EV projections from Action Network API."""

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self._client = ActionNetworkClient()
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Check if the streamer is connected."""
        return self._is_connected

    async def connect(self) -> bool:
        """Connect to Action Network API."""
        try:
            # Action Network doesn't require authentication setup
            self._is_connected = True
            logger.info("Action Network streamer connected")
            return True
        except Exception as e:
            self._is_connected = False
            logger.error("Failed to connect Action Network streamer", error=str(e))
            return False

    async def disconnect(self) -> None:
        """Disconnect from Action Network API."""
        try:
            await self._client.close()
            self._is_connected = False
            logger.info("Action Network streamer disconnected")
        except Exception as e:
            logger.error("Failed to disconnect Action Network streamer", error=str(e))

    async def fetch_data(self, sport: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch EV data from Action Network.
        
        Args:
            sport: Sport to fetch (nfl, nba, mlb, nhl)
        
        Returns:
            Dictionary with player props and game projections
        """
        try:
            if not sport:
                sport = "nfl"  # Default to NFL
            
            # Map sport names to Action Network format
            sport_mapping = {
                "americanfootball_nfl": "nfl",
                "basketball_nba": "nba", 
                "baseball_mlb": "mlb",
                "icehockey_nhl": "nhl"
            }
            
            an_sport = sport_mapping.get(sport, sport)
            
            # Fetch EV data from Action Network
            ev_data = await self._client.get_ev_data(sport=an_sport)
            
            return {
                "sport": sport,
                "player_props": ev_data.get("player_props", []),
                "game_projections": ev_data.get("game_projections", []),
                "requested_sport": sport,
                "processed_sports": [sport],
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "actionnetwork"
            }
            
        except Exception as e:
            logger.error(
                "Failed to fetch Action Network data",
                sport=sport,
                error=str(e)
            )
            return {
                "sport": sport,
                "player_props": [],
                "game_projections": [],
                "requested_sport": sport,
                "processed_sports": [],
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "actionnetwork",
                "error": str(e)
            }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw Action Network data for EV calculations.
        
        Args:
            raw_data: Raw data from Action Network API
        
        Returns:
            Processed data ready for EV calculations
        """
        # Debug: Log the actual raw_data type and content
        print(f"DEBUG: ActionNetworkStreamer.process_data() raw_data type: {type(raw_data)}")
        # print(f"DEBUG: ActionNetworkStreamer.process_data() raw_data: {str(raw_data)[:200]}...")  # Commented out - may cause error
        
        try:
            print(f"DEBUG: Starting process_data with raw_data type: {type(raw_data)}")
            print(f"DEBUG: raw_data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'NOT A DICT'}")
            
            # Action Network data is already normalized by the client
            # Just ensure it's in the expected format for EV pipeline
            player_props = raw_data.get("player_props", [])
            game_projections = raw_data.get("game_projections", [])
            
            print(f"DEBUG: player_props type: {type(player_props)}, length: {len(player_props)}")
            print(f"DEBUG: game_projections type: {type(game_projections)}, length: {len(game_projections)}")
            
            # Add EV calculation metadata
            processed_props = []
            for i, prop in enumerate(player_props):
                try:
                    # Debug: Check each prop type
                    if i < 3:  # Only log first 3 props to avoid spam
                        print(f"DEBUG: Prop {i} type: {type(prop)}")
                    
                    # Skip if prop is not a dictionary (prevents string mapping error)
                    if not isinstance(prop, dict):
                        print(f"DEBUG: Skipping non-dict prop {i}: {type(prop)}")
                        continue
                    
                    processed_prop = {
                        **prop,
                        "ev_source": "actionnetwork",
                        "ev_timestamp": datetime.utcnow().isoformat(),
                        "ev_processed": True
                    }
                    processed_props.append(processed_prop)
                except Exception as e:
                    print(f"DEBUG: Error processing prop {i}: {e}, prop type: {type(prop)}, prop: {str(prop)[:100]}")
                    continue  # Skip problematic props instead of raising
            
            processed_projections = []
            for i, proj in enumerate(game_projections):
                try:
                    # Debug: Check each projection type
                    if i < 3:  # Only log first 3 projections to avoid spam
                        print(f"DEBUG: Projection {i} type: {type(proj)}")
                    
                    # Skip if projection is not a dictionary (prevents string mapping error)
                    if not isinstance(proj, dict):
                        print(f"DEBUG: Skipping non-dict projection {i}: {type(proj)}")
                        continue
                    
                    processed_projection = {
                        **proj,
                        "ev_source": "actionnetwork", 
                        "ev_timestamp": datetime.utcnow().isoformat(),
                        "ev_processed": True
                    }
                    processed_projections.append(processed_projection)
                except Exception as e:
                    print(f"DEBUG: Error processing projection {i}: {e}, proj type: {type(proj)}, proj: {str(proj)[:100]}")
                    continue  # Skip problematic projections instead of raising
            
            logger.info(
                "Processed Action Network data for EV",
                player_props=len(processed_props),
                game_projections=len(processed_projections)
            )
            
            return {
                **raw_data,
                "player_props": processed_props,
                "game_projections": processed_projections,
                "processed": True
            }
            
        except Exception as e:
            logger.error(
                "Failed to process Action Network data",
                error=str(e)
            )
            return raw_data

    def get_supported_sports(self) -> List[str]:
        """Get list of sports supported by Action Network."""
        return [
            "americanfootball_nfl",
            "basketball_nba", 
            "baseball_mlb",
            "icehockey_nhl"
        ]


# Register the streamer
def create_streamer(name: str, config: Dict[str, Any]) -> ActionNetworkStreamer:
    """Create an Action Network streamer instance."""
    return ActionNetworkStreamer(name, config)


# Streamer configuration
STREAMER_CONFIG = {
    "name": "actionnetwork",
    "display_name": "Action Network",
    "description": "EV projections and player props from Action Network API",
    "supports_ev": True,
    "supports_odds": True,
    "supports_projections": True,
    "rate_limit": 0.2,  # 200ms between requests
    "timeout": 30.0
}

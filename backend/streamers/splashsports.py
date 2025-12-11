"""
SplashSports data streamer for KashRock Data Stream service.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class SplashSportsStreamer(BaseStreamer):
    """Streamer for SplashSports player props data."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # SplashSports configuration
        self.sport = config.get("sport", "football_nfl")
        self.prop_types = config.get("prop_types", ["points", "passing_touchdowns", "passing_yards"])
        self.limit = config.get("limit", 1000)
        
        # API configuration
        self.base_url = "https://api.splashsports.com/props-service/api/props"
        self.client: Optional[httpx.AsyncClient] = None
        
        # Sport mapping for internal use
        self.sport_map = {
            "football_cfb": "Football",
            "football_nfl": "Football",
            "basketball_wnba": "Basketball",
            "basketball_nba": "Basketball",
            "baseball_mlb": "Baseball",
        }
        
        # League mapping for SplashSports API
        self.league_map = {
            "football_cfb": "cfb",
            "football_nfl": "nfl",
            "basketball_wnba": "wnba",
            "basketball_nba": "nba",
            "baseball_mlb": "mlb",
        }
        
        # Headers for API requests - updated to match working curl files
        self.headers = {
            "accept": "*/*",
            "content-type": "application/json;charset=utf-8",
            "accept-language": "en-US,en;q=0.9",
            "x-app-platform": "iOS",
            "user-agent": "Splash Sports/com.splash.splashsports/v2.8.1-237/iOS 26.0/iPhone13,4",
            "priority": "u=3",
            "x-app-version": "2.8.1",
        }
        
        logger.info("Initialized SplashSports streamer", sport=self.sport, prop_types=self.prop_types)
    
    async def connect(self) -> bool:
        """Establish connection to SplashSports API."""
        try:
            # Create client with proper decompression support
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            # Test connection with a simple request
            league = self.league_map.get(self.sport)
            if not league:
                logger.error("Unsupported sport", sport=self.sport)
                return False
            
            # Test with first prop type
            test_prop = self.prop_types[0] if self.prop_types else "points"
            params = {
                "limit": 1,
                "offset": 0,
                "type": test_prop,
                "league": league
            }
            
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Test JSON parsing
            try:
                test_data = response.json()
                logger.info("Successfully connected to SplashSports API", sport=self.sport)
                return True
            except Exception as json_error:
                logger.error("Connection test failed - JSON decode error", error=str(json_error))
                return False
            
        except Exception as e:
            logger.error("Failed to connect to SplashSports API", error=str(e))
            if self.client:
                await self.client.aclose()
                self.client = None
            return False
    
    async def disconnect(self):
        """Close connection to SplashSports API."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from SplashSports API")
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch data from SplashSports API."""
        if not self.client:
            raise Exception("Not connected to SplashSports API")
        
        league = self.league_map.get(self.sport)
        if not league:
            raise Exception(f"Unsupported sport: {self.sport}")
        
        all_props = []
        
        # Fetch data for each prop type
        for prop_type in self.prop_types:
            try:
                params = {
                    "limit": self.limit,
                    "offset": 0,
                    "type": prop_type,
                    "league": league
                }
                
                response = await self.client.get(self.base_url, params=params)
                
                # Log response details for debugging
                logger.debug("API Response", 
                           prop_type=prop_type, 
                           status_code=response.status_code,
                           content_type=response.headers.get('content-type'),
                           content_length=len(response.content))
                
                response.raise_for_status()
                
                # Handle potential encoding issues
                try:
                    data = response.json()
                except Exception as json_error:
                    logger.error("JSON decode error", 
                               prop_type=prop_type, 
                               error=str(json_error), 
                               status_code=response.status_code,
                               content_type=response.headers.get('content-type'),
                               response_text=response.text[:200] if hasattr(response, 'text') else 'N/A')
                    continue
                
                props = data.get('data', [])
                
                # Add prop type to each prop for processing
                for prop in props:
                    prop['_prop_type'] = prop_type
                
                all_props.extend(props)
                
                logger.debug("Fetched props", prop_type=prop_type, count=len(props))
                
            except Exception as e:
                logger.error("Error fetching prop type", prop_type=prop_type, error=str(e))
                continue
        
        return {
            "sport": self.sport,
            "league": league,
            "props": all_props,
            "timestamp": datetime.utcnow().isoformat(),
            "total_props": len(all_props)
        }
    
    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the raw SplashSports data without normalization."""
        props = raw_data.get("props", [])
        return {
            "book": "splashsports",
            "sport": raw_data.get("sport"),
            "league": raw_data.get("league"),
            "raw_props": props,
            "timestamp": raw_data.get("timestamp"),
            "total_props": len(props),
            "metadata": {
                "has_odds": False,
                "has_multipliers": False,
                "market_types": ["player_props"],
                "book_type": "over_under_no_odds",
                "note": "Raw SplashSports payload returned; normalization pending"
            }
        }
    
    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports."""
        return ["football_cfb", "football_nfl", "basketball_wnba", "basketball_nba", "baseball_mlb"]
    
    @classmethod
    def get_default_prop_types(cls, sport: str) -> List[str]:
        """Get default prop types for a sport."""
        prop_types_map = {
            "football_nfl": [
                "passing_touchdowns", "passing_yards", "rushing_yards", "rushing_touchdowns",
                "receiving_yards", "receiving_touchdowns", "interceptions", "sacks"
            ],
            "football_cfb": [
                "passing_touchdowns", "passing_yards", "rushing_yards", "rushing_touchdowns",
                "receiving_yards", "receiving_touchdowns", "interceptions", "sacks"
            ],
            "basketball_nba": [
                "points", "rebounds", "assists", "steals", "blocks", "turnovers",
                "pts_rebs_ast", "pts_rebs", "pts_ast", "rebs_ast"
            ],
            "basketball_wnba": [
                "points", "rebounds", "assists", "steals", "blocks", "turnovers",
                "pts_rebs_ast", "pts_rebs", "pts_ast", "rebs_ast"
            ],
            "baseball_mlb": [
                "strikeouts", "hits", "runs", "rbis", "walks", "home_runs",
                "singles", "doubles", "triples", "total_bases"
            ],
        }
        
        return prop_types_map.get(sport, ["points"])
    
    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        """Get default configuration for a sport."""
        return {
            "sport": sport,
            "prop_types": cls.get_default_prop_types(sport),
            "limit": 100
        }

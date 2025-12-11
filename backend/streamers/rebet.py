"""
Rebet data streamer for KashRock Data Stream service.
"""

import asyncio
import httpx
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from pathlib import Path

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class RebetStreamer(BaseStreamer):
    """Streamer for Rebet sportsbook data."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Rebet configuration
        self.sport = config.get("sport", "football_nfl")
        self.limit = config.get("limit", 10000)
        
        # API configuration from endpoints.yml
        self.base_url = "https://api.rebet.app/prod/sportsbook-v3"
        self.client: Optional[httpx.AsyncClient] = None
        
        # Load environment variables from .env files
        self._load_env_from_files()
        
        # Get API credentials from environment
        api_key = os.getenv('REBET_API_KEY')
        bearer_token = os.getenv('REBET_BEARER')
        
        if not api_key:
            raise ValueError("REBET_API_KEY environment variable must be set")
        
        # Headers for API requests
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "user-agent": "rebetMobileApp/1430 CFNetwork/3826.600.41 Darwin/24.6.0",
            "x-api-key": api_key,
        }
        
        # Add authorization header if bearer token is available
        if bearer_token:
            self.headers["authorization"] = f"Bearer {bearer_token}"
        
        # Tournament IDs from backend discovery
        self.tournament_ids_map = {
            # Soccer (sr:sport:1)
            "soccer_epl": ["sr:tournament:17"],
            "soccer_championship": ["sr:tournament:18"],
            "soccer_efl_cup": ["sr:tournament:21"],
            "soccer_serie_a": ["sr:tournament:23"],
            "soccer_ligue_1": ["sr:tournament:34"],
            "soccer_bundesliga": ["sr:tournament:35"],
            "soccer_premiership": ["sr:tournament:36"],
            "soccer_eredivisie": ["sr:tournament:37"],
            "soccer_superliga": ["sr:tournament:39"],
            "soccer_2_bundesliga": ["sr:tournament:44"],
            "soccer_super_lig": ["sr:tournament:52"],
            "soccer_laliga_2": ["sr:tournament:54"],
            "soccer_k_league_1": ["sr:tournament:410"],
            "soccer_conmebol_sudamericana": ["sr:tournament:480"],
            "soccer_champions_league": ["sr:tournament:7"],
            "soccer_laliga": ["sr:tournament:8"],
            "soccer_world_cup_qualification_uefa": ["sr:tournament:11"],
            "soccer_world_cup_qualification_caf": ["sr:tournament:13"],
            
            # American Football (sr:sport:16)
            "football_nfl": ["sr:tournament:31"],
            "football_cfl": ["sr:tournament:790"],
            "football_cfb": ["sr:tournament:27653"],
            
            # Basketball (sr:sport:2)
            "basketball_nbl": ["sr:tournament:250"],
            "basketball_wnba": ["sr:tournament:486"],
            
            # Baseball (sr:sport:3)
            "baseball_mlb": ["sr:tournament:109"],
            
            # Ice Hockey (sr:sport:4)
            "hockey_asia_league": ["sr:tournament:19200"],
            
            # Handball (sr:sport:6)
            "handball_ehf_european_league_women": ["sr:tournament:60"],
            "handball_hla_meisterliga": ["sr:tournament:85"],
            
            # Rugby (sr:sport:12)
            "rugby_top_14": ["sr:tournament:420"],
            
            # Volleyball (sr:sport:23)
            "volleyball_super_cup_women": ["sr:tournament:20200"],
        }
        
        self.tournament_ids = self.tournament_ids_map.get(self.sport, [])
        
        logger.info("Initialized Rebet streamer", sport=self.sport, tournament_count=len(self.tournament_ids))
    
    def _load_env_from_files(self):
        """Load environment variables from .env files."""
        try:
            # Look for .env files in multiple locations
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent.parent  # Go up to !KashRockAPI
            kashrock_root = project_root.parent  # Go up to KashRock™️
            
            candidates = [
                project_root / '.env',
                kashrock_root / '.env',
                kashrock_root / 'bot' / '.env'
            ]
            
            for env_path in candidates:
                if env_path.exists():
                    logger.debug("Loading environment from", path=str(env_path))
                    for line in env_path.read_text().splitlines():
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        key, val = line.split('=', 1)
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = val
                    break  # Stop after loading the first found .env file
        except Exception as e:
            logger.warning("Error loading .env file", error=str(e))
            pass
    
    async def connect(self) -> bool:
        """Establish connection to Rebet API."""
        try:
            # Create client with proper headers
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            # Test connection with a simple request
            if not self.tournament_ids:
                logger.error("No tournament IDs configured for sport", sport=self.sport)
                return False
            
            # Test with first tournament ID
            test_payload = {
                "tournament_id": self.tournament_ids[0],
                "game_type": 1,  # Main markets
                "custom_filter": False,
                "include_past": True,
                "include_future": True
            }
            
            url = f"{self.base_url}/load-sportsbook-data-v3"
            response = await self.client.post(url, json=test_payload)
            
            if response.status_code == 200:
                test_data = response.json()
                logger.info("Successfully connected to Rebet API", sport=self.sport)
                return True
            elif response.status_code == 401:
                logger.error("Authentication failed - check REBET_BEARER and REBET_API_KEY")
                return False
            elif response.status_code == 403:
                logger.error("Access forbidden - check API permissions")
                return False
            else:
                logger.error("Connection test failed", status_code=response.status_code)
                return False
            
        except Exception as e:
            logger.error("Failed to connect to Rebet API", error=str(e))
            if self.client:
                await self.client.aclose()
                self.client = None
            return False
    
    async def disconnect(self):
        """Close connection to Rebet API."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from Rebet API")
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch raw data from Rebet API."""
        if not self.client:
            raise Exception("Not connected to Rebet API")
        
        all_events = []
        url = f"{self.base_url}/load-sportsbook-data-v3"
        
        # Fetch data from all tournament IDs
        for tournament_id in self.tournament_ids:
            try:
                # Fetch main markets (game_type=1)
                main_events = await self._fetch_tournament_data(url, tournament_id, game_type=1)
                all_events.extend(main_events)
                
                # Fetch alternate markets (game_type=2) if limit allows
                if len(all_events) < self.limit:
                    alt_events = await self._fetch_tournament_data(url, tournament_id, game_type=2)
                    all_events.extend(alt_events)
                
                logger.debug("Fetched events from tournament", 
                           tournament_id=tournament_id[:8], 
                           count=len(main_events) + len(alt_events if 'alt_events' in locals() else []))
                
            except Exception as e:
                logger.error("Error fetching tournament data", 
                           tournament_id=tournament_id, 
                           error=str(e))
                continue
        
        # Limit results if specified
        if self.limit and len(all_events) > self.limit:
            all_events = all_events[:self.limit]
        
        return all_events
    
    async def _fetch_tournament_data(self, url: str, tournament_id: str, game_type: int) -> List[Dict[str, Any]]:
        """Fetch data for a specific tournament with pagination."""
        events = []
        cursor = None
        page = 1
        max_pages = 10  # Reasonable limit for streaming
        seen_event_ids = set()
        
        while page <= max_pages:
            payload = {
                "tournament_id": tournament_id,
                "game_type": game_type,
                "custom_filter": False,
                "include_past": True,
                "include_future": True
            }
            
            # Add cursor for pagination if available
            if cursor:
                payload["last_evaluated_key"] = cursor
            
            try:
                response = await self.client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and 'data' in data and 'events' in data['data']:
                        page_events = data['data']['events']
                        
                        # Deduplicate events
                        new_events = 0
                        for event in page_events:
                            event_id = event.get('id')
                            if event_id and event_id in seen_event_ids:
                                continue
                            if event_id:
                                seen_event_ids.add(event_id)
                            events.append(event)
                            new_events += 1
                        
                        logger.debug("Fetched page", 
                                   page=page, 
                                   tournament_id=tournament_id[:8],
                                   game_type=game_type,
                                   new_events=new_events)
                        
                        # Check for pagination
                        new_cursor = data.get('data', {}).get('last_evaluated_key')
                        if new_cursor and new_cursor != cursor and len(page_events) > 0:
                            cursor = new_cursor
                            page += 1
                            await asyncio.sleep(0.1)  # Small delay
                        else:
                            break
                    else:
                        break
                else:
                    logger.warning("API error", 
                                 status_code=response.status_code,
                                 tournament_id=tournament_id)
                    break
                    
            except Exception as e:
                logger.error("Error fetching page", 
                           page=page, 
                           tournament_id=tournament_id,
                           error=str(e))
                break
        
        return events
    
    async def process_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Returns the raw Rebet data without normalization."""
        return {
            "book": "rebet",
            "sport": self.sport,
            "raw_events": raw_data,
            "timestamp": datetime.utcnow().isoformat(),
            "total_events": len(raw_data),
            "metadata": {
                "has_odds": True,
                "has_multipliers": False,
                "market_types": ["moneyline", "spread", "total", "player_props"],
                "book_type": "sportsbook"
            }
        }
    
    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports."""
        return [
            # Soccer
            "soccer_epl", "soccer_championship", "soccer_efl_cup", "soccer_serie_a",
            "soccer_ligue_1", "soccer_bundesliga", "soccer_premiership", "soccer_eredivisie",
            "soccer_superliga", "soccer_2_bundesliga", "soccer_super_lig", "soccer_laliga_2",
            "soccer_k_league_1", "soccer_conmebol_sudamericana", "soccer_champions_league",
            "soccer_laliga", "soccer_world_cup_qualification_uefa", "soccer_world_cup_qualification_caf",
            
            # American Football
            "football_nfl", "football_cfl", "football_cfb",
            
            # Basketball
            "basketball_nbl", "basketball_wnba",
            
            # Baseball
            "baseball_mlb",
            
            # Ice Hockey
            "hockey_asia_league",
            
            # Handball
            "handball_ehf_european_league_women", "handball_hla_meisterliga",
            
            # Rugby
            "rugby_top_14",
            
            # Volleyball
            "volleyball_super_cup_women",
        ]
    
    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        """Get default configuration for a sport."""
        return {
            "sport": sport,
            "limit": 10000
        }

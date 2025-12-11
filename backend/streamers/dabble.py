"""
Dabble data streamer for KashRock Data Stream service.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .base import BaseStreamer

logger = structlog.get_logger()


class DabbleStreamer(BaseStreamer):
    """Streamer for Dabble DFS player props data."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Dabble configuration
        self.sport = config.get("sport", "basketball_wnba")
        self.limit = config.get("limit", 100000)
        
        # API configuration
        self.base_url = "https://api.dabble.com"
        self.client: Optional[httpx.AsyncClient] = None
        
        # Competition IDs for different sports (from Dabble backend API)
        self.competition_ids = {
            # Traditional Sports
            "basketball_wnba": "94edc3b0-009f-4369-88cb-d6a43f917f53",
            "basketball_nba": "51a2f625-e556-4c23-a091-4f135591d576",
            "basketball_ncaa": "3c8ae166-3d40-4916-a23f-6d1dc370d117",
            "football_nfl": "7f7c2f8f-ff04-4e5a-a3c8-d503a523d9ad",
            "football_cfb": "402c1612-4f2b-44fa-8061-3bafdb4b673d",
            "baseball_mlb": "dac474f4-2e9f-432d-a503-80f27452c41f",
            "icehockey_nhl": "9a345ae1-caf1-4b1d-ac56-5fe4fe58cd2c",
            "soccer_epl": "b3ab59f2-631c-413a-b727-c8e49571cb64",
            "soccer_mls": "f0ee7b69-e7af-49b8-bc2c-34851b34ffa4",
            "tennis": "5cd5c44c-3f74-41c8-8055-96400c6f916c",
            "tennis_atp": "1609723f-3209-4306-9aa7-a153b21cef22",
            "tennis_wta": "691b8594-0f4d-44c7-8a78-2d921bb0a4d6",
            "mma": "0637e248-092a-408c-8ff9-0fca8b4d8d56",
            "mma_ufc": "aa4cbcb7-f944-4530-a3a2-1155a1565836",
            "golf_pga": "eb653364-7935-4a4c-83ea-a1acac10218d",
            "nascar": "b37c44ed-a18f-4be6-9679-d49e81ca6619",
            "f1": "ec4ec474-087b-4fd6-a481-f462f4577f22",
            "boxing": "2acf8935-8d89-455b-bb4b-dbfba9c4ae3b",
            "cricket": "1e3940c0-b636-4fae-b806-7a4504455794",
            "afl": "3a3c94b6-9e74-4ad2-92ec-eade1dbb3ea6",
            "lacrosse": "3257d229-4ef5-4a73-b278-d02eb01a30fb",
            "handball": "584e0df1-37a5-41e6-9c10-a63455d5bbf9",
            "beachvolleyball": "1e6cd14b-0c1c-423a-9619-e739c6616111",
            "darts": "3ae9ee54-8604-4749-be59-477b9a4ab5ea",
            "pwhl": "6306fd27-224f-4b34-aa9f-52e0bd1c682c",
            # Esports
            "esports_cs2": "acd5b3f6-dd7a-484f-a4e5-a747badb32c6",
            "esports_lol": "086211fd-5445-4955-be1b-9ed7ba84641d",
            "esports_valorant": "4de0349e-6657-4f63-aa4f-6034cfef867a",
            "esports_dota2": "eab2bf14-c4d4-4c08-a6cb-bc13bebb9147",
            "esports_cod": "36f5cddd-a003-4bed-90f4-518f77777372",
            "esports_halo": "3b12cbb3-805e-4921-8798-b176e01abc9d",
            "esports_rocketleague": "cb921e5b-a442-4fcd-9ace-ca0aaa8ada90",
            "esports_apex": "55febce6-7002-43dd-aca0-98b7f4c0ce97",
            "esports_r6": "8a432fb6-02e1-4c0d-895e-786624255b4c"
        }
        
        # Sport mapping for internal use
        self.sport_map = {
            # Traditional Sports
            "basketball_wnba": "Basketball",
            "basketball_nba": "Basketball",
            "basketball_ncaa": "Basketball",
            "football_nfl": "Football",
            "football_cfb": "Football",
            "baseball_mlb": "Baseball",
            "icehockey_nhl": "Hockey",
            "soccer_epl": "Soccer",
            "soccer_mls": "Soccer",
            "tennis": "Tennis",
            "tennis_atp": "Tennis",
            "tennis_wta": "Tennis",
            "mma": "MMA",
            "mma_ufc": "MMA",
            "golf_pga": "Golf",
            "nascar": "Motorsports",
            "f1": "Motorsports",
            "boxing": "Boxing",
            "cricket": "Cricket",
            "afl": "Australian Football",
            "lacrosse": "Lacrosse",
            "handball": "Handball",
            "beachvolleyball": "Volleyball",
            "darts": "Darts",
            "pwhl": "Hockey",
            # Esports
            "esports_cs2": "Esports",
            "esports_lol": "Esports",
            "esports_valorant": "Esports",
            "esports_dota2": "Esports",
            "esports_cod": "Esports",
            "esports_halo": "Esports",
            "esports_rocketleague": "Esports",
            "esports_apex": "Esports",
            "esports_r6": "Esports"
        }
        
        # League mapping
        self.league_map = {
            "basketball_wnba": "WNBA",
            "football_cfb": "NCAAF",
            "baseball_mlb": "MLB",
            "football_nfl": "NFL",
            "esports_cs2": "CS2",
            "esports_lol": "LoL"
        }
        
        # Default market groups by sport
        self.default_market_groups = {
            "basketball_wnba": [
                "Points", "Rebounds", "Assists", "Steals", "Blocks",
                "Points + Rebound + Assists", "Point + Rebound", "Turnovers",
                "Three Pointers Made", "Double Double", "Triple Double"
            ],
            "football_cfb": [
                "Passing Yards", "Receiving Yards", "Rushing Yards",
                "Passing Touchdowns", "Receiving + Rushing Touchdowns",
                "Receiving yards + rushing yards", "Receptions",
                "Passing Attempts", "Passing Completions",
                "Passing Yards + Rushing Yards", "Rushing Attempts", "Interceptions"
            ],
            "baseball_mlb": [
                "Hits", "Runs", "RBIs", "Pitcher Strikeouts",
                "Pitcher Total Outs", "Hits Allowed", "Total Bases",
                "Stolen Bases", "Pitcher Owned Runs", "Single",
                "Batter Walks", "Pitcher Walks"
            ],
            "football_nfl": [
                "Passing Yards", "Rushing Yards", "Receiving Yards",
                "Passing Touchdowns", "Receiving + Rushing Touchdowns",
                "Rushing Touchdown", "Receiving Touchdowns",
                "Receiving + Rushing Yards", "Receptions",
                "Passing Attempts", "Passing Completions",
                "Passing + Rushing Yards", "Sacks", "Extra Point Made", "Field Goal"
            ],
            "esports_cs2": ["Game 1 Kills", "Game 2 Kills"],
            "esports_lol": ["Game 1 Kills", "Game 2 Kills"],
            "soccer_epl": ["Shots", "Shots on Target", "Tackles", "Saves", "Passes Attempted"],
            "soccer_mls": ["Shots", "Goals", "Assists", "Passes", "Tackles", "Saves", "Cards", "Fouls"],
            "tennis_atp": ["Match Total Games", "Break Points Won"],
            "tennis_wta": ["Match Total Games", "Break Points Won"],
            "mma_ufc": ["Significant Strikes", "Takedowns", "Fight Time (Mins)"]
        }
        
        # Headers for API requests (using a working bearer token)
        self.headers = {
            "accept": "application/json",
            "x-app-version": "3.9.0-313f6d17",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Dabble/1000030900 CFNetwork/3860.100.1 Darwin/25.0.0",
            "authorization": "Bearer eyJraWQiOiJrNFhodFppYTFUcjZPdG1OQTJUQXhYaWlIMjhSV0hmdG9Fb21lVDRzbUhvPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI4ZGU0ZGZkNC1iYmNmLTQ2NWYtODQ1MC1kN2MyMGNhMWJmZjkiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0yLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMl8zcW44SFYydXkiLCJjbGllbnRfaWQiOiI0dmltc2kzOHQ5NzVrdTM4NmQ3ZGVycTAwYyIsIm9yaWdpbl9qdGkiOiI1OTA1MjA3YS05NzU5LTQxY2YtOWI3Mi05MWM0NGZiZjU2MGMiLCJldmVudF9pZCI6ImQyMDgxMmJjLWE3ZjctNDUxYS04ODBiLTQwYzUxYTdmMTM4OCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTc3MTY2OTEsImV4cCI6MTc1OTUyNzczMiwiaWF0IjoxNzU5NTI0MTMyLCJqdGkiOiIzMjhkNjJmNC03YWQxLTRiNjQtYmFiMi1jNWNmMWViMTE2MzMiLCJ1c2VybmFtZSI6ImI1NGRkMWFiLWZkNmQtNDYyOC1iM2Y1LWUxNTcwZjgyZjdkMiJ9.qaCchj1y2q9aEh6_UNi0iwZUYWeDzCGSZ3qKwOj19TDpEQ66h4SedBuUilXqbNuS9OEoArG1RGMv9cAVh_yBluF3pvC4QIQD0T-2g1e2UhGKYi1dQgPiF_7etczoHfFAQSSXoGKdA_lM91tyqjs9iKCItMHSvwu0etEEaWIV9v_9dXcpbnvHjP5gVVXbleJgyPUkP3B4DA8uKQvIA7LG9qqaONCZLcFNcoqkOx2NZu5eUx7FzHFeFKghsnyKOyvAtzFkK-zVmhdK2eHTEUr3u5xn-HwOkdEoxoy9cgoWLlvwfpn3gRDu6EL-ZnkIIVniPD1H4w_yNZvohAASB90esA",
            "accept-encoding": "gzip, deflate, br"
        }
        
        # Set market_groups from config or use default for the sport
        self.market_groups = config.get("market_groups", self.default_market_groups.get(self.sport, []))
        
        logger.info("Initialized Dabble streamer", sport=self.sport, market_groups=len(self.market_groups))
    
    async def connect(self) -> bool:
        """Establish connection to Dabble API."""
        try:
            # Create client
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            # Determine competition ID
            competition_id = self.competition_ids.get(self.sport)
            if not competition_id:
                logger.error("Dabble: Unsupported sport, no competition ID found", sport=self.sport)
                return False
            
            # Test with a simple market group
            test_market = "Points"  # Most common market group
            url = f"{self.base_url}/search/dfs/competitions/{competition_id}/props"
            params = {"marketGroupName": test_market}
            
            logger.info("Dabble: Sending connection test request", url=url, params=params)
            response = await self.client.get(url, params=params)
            logger.info("Dabble: Received connection test response", status_code=response.status_code, reason=response.reason_phrase)
            
            response.raise_for_status()
            
            # Test JSON parsing
            try:
                test_data = response.json()
                logger.info("Dabble: Successfully connected", competition_id=competition_id)
                return True
            except Exception as json_error:
                logger.error("Dabble: Connection test failed - JSON decode error", competition_id=competition_id, error=str(json_error), response_text=response.text)
                return False
            
        except httpx.HTTPStatusError as http_error:
            logger.error("Dabble: HTTP error during connection", 
                         competition_id=self.sport, 
                         error=str(http_error),
                         request_url=http_error.request.url,
                         response_status=http_error.response.status_code,
                         response_text=http_error.response.text)
            if self.client:
                await self.client.aclose()
                self.client = None
            return False
        except Exception as e:
            logger.error("Dabble: Failed to connect to Dabble API", competition_id=self.sport, error=str(e))
            if self.client:
                await self.client.aclose()
                self.client = None
            return False
    
    async def disconnect(self):
        """Close connection to Dabble API."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from Dabble API")
    
    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch data from Dabble API using competition ID."""
        if not self.client:
            raise Exception("Not connected to Dabble API")
        
        # Determine the competition ID
        competition_id = self.competition_ids.get(self.sport)
        if not competition_id:
            logger.error("Dabble: Unsupported sport in fetch_data", sport=self.sport)
            raise Exception(f"Unsupported sport: {self.sport}")

        all_props = []

        # The API requires a marketGroupName. We must iterate through a list of potential
        # market groups to discover which ones are available for this competition.
        market_groups_to_try = self.market_groups if self.market_groups else self.get_comprehensive_market_groups()
        logger.info("Dabble: Attempting to fetch props", 
                    count=len(market_groups_to_try), 
                    competition_id=competition_id)

        for market_group in market_groups_to_try:
            try:
                url = f"{self.base_url}/search/dfs/competitions/{competition_id}/props"
                params = {"marketGroupName": market_group}
                
                logger.info("Dabble: Fetching market group", url=url, params=params)
                response = await self.client.get(url, params=params)
                logger.info("Dabble: Got response for market group", market_group=market_group, status_code=response.status_code)

                # A 400 status likely means the market doesn't exist for this competition, which is fine.
                if response.status_code >= 400:
                    logger.error("Dabble: Market group not found or error", 
                                   market_group=market_group, 
                                   status_code=response.status_code, 
                                   response_text=response.text)
                    continue # Skip to the next market group

                data = response.json()
                
                props = []
                if isinstance(data, list):
                    props = data
                elif isinstance(data, dict):
                    props = data.get('data') or data.get('props') or data.get('results') or []

                if props and isinstance(props, list):
                    for prop in props:
                        if isinstance(prop, dict):
                            prop['market_group'] = market_group # Add for consistency
                    
                    all_props.extend(props)
                    logger.info("Dabble: Fetched props", competition_id=competition_id[:8], market_group=market_group, count=len(props))

                await asyncio.sleep(0.1) # Small delay
                
            except httpx.HTTPStatusError as http_error:
                logger.error("Dabble: HTTP error fetching market group", 
                             market_group=market_group, 
                             error=str(http_error),
                             response_text=http_error.response.text)
                continue
            except Exception as e:
                logger.error("Dabble: Error fetching market group", competition_id=competition_id[:8], market_group=market_group, error=str(e))
                continue
        
        logger.info("Dabble: Finished fetching all market groups", total_props=len(all_props))
        return all_props
    
    def _get_league_from_competition_id(self, competition_id: str) -> str:
        """Get league name from competition ID."""
        competition_mapping = {
            "7f7c2f8f-ff04-4e5a-a3c8-d503a523d9ad": "NFL",
            "402c1612-4f2b-44fa-8061-3bafdb4b673d": "CFB", 
            "3c8ae166-3d40-4916-a23f-6d1dc370d117": "NFL 2H",
            "dac474f4-2e9f-432d-a503-80f27452c41f": "MLB",
            "94edc3b0-009f-4369-88cb-d6a43f917f53": "WNBA",
            "2acf8935-8d89-455b-bb4b-dbfba9c4ae3b": "NBA",
            "584e0df1-37a5-41e6-9c10-a63455d5bbf9": "CBB",
            "ab37a56f-0131-41e8-8a5f-e29bce546f9a": "NHL",
            "691b8594-0f4d-44c7-8a78-2d921bb0a4d6": "WTA",
            "1609723f-3209-4306-9aa7-a153b21cef22": "ATP",
            "e7b578eb-674e-4b2d-a790-11050adcc0a9": "ATP/WTA",
            "b3ab59f2-631c-413a-b727-c8e49571cb64": "Premier League",
            "ea1f99fd-dc39-4d65-80a8-843eadde2272": "LaLiga",
            "4ad11b1e-e3a6-4bac-8969-d91ad222739e": "Serie A",
            "acd5b3f6-dd7a-484f-a4e5-a747badb32c6": "CS2",
            "086211fd-5445-4955-be1b-9ed7ba84641d": "LoL",
            "4de0349e-6657-4f63-aa4f-6034cfef867a": "Dota 2",
            "6b73cd8b-b2bd-4de5-8c2b-5d7553806f99": "Valorant",
            "aa4cbcb7-f944-4530-a3a2-1155a1565836": "UFC",
            "0f818bbc-aaf1-4c8f-9b25-7b8e6a20a54c": "Boxing"
        }
        return competition_mapping.get(competition_id, "Unknown")
    
    def get_comprehensive_market_groups(self) -> List[str]:
        """Returns a large list of market groups to try for discovery."""
        return [
            "Points", "Rebounds", "Assists", "Steals", "Blocks",
            "Passing Yards", "Rushing Yards", "Receiving Yards", 
            "Passing Touchdowns", "Receptions", "Interceptions",
            "Hits", "Runs", "RBIs", "Pitcher Strikeouts", "Total Bases", "Stolen Bases",
            "Game 1 Kills", "Game 2 Kills", "Points + Rebound + Assists", "Point + Rebound",
            "Turnovers", "Three Pointers Made", "Double Double", "Triple Double",
            "Receiving + Rushing Touchdowns", "Receiving yards + rushing yards",
            "Passing Attempts", "Passing Completions", "Passing Yards + Rushing Yards",
            "Rushing Attempts", "Rushing Touchdown", "Receiving Touchdowns",
            "Sacks", "Extra Point Made", "Field Goal", "Pitcher Total Outs", "Hits Allowed",
            "Pitcher Owned Runs", "Single", "Batter Walks", "Pitcher Walks"
        ]

    async def process_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return raw Dabble data with NO processing - pure raw API response."""
        
        # raw_data is now the pure list of props from the API
        # Just wrap it with minimal metadata for the API response
        return {
            "book": "dabble",
            "raw_api_response": raw_data,  # This is the pure raw API response
            "total_props": len(raw_data),
            "metadata": {
                "book_type": "dfs_multipliers",
                "data_format": "pure_dabble_api_response",
                "normalization_required": True,
                "note": "This is the exact raw API response from Dabble - no fields added or modified",
                "sample_structure": {
                    "props_count": len(raw_data),
                    "sample_prop_keys": list(raw_data[0].keys()) if raw_data else [],
                    "has_selection_options": any(prop.get("selectionOptions") for prop in raw_data),
                    "has_prop_values": any(prop.get("propValue") is not None for prop in raw_data),
                    "has_multipliers": any(
                        option.get("multiplier") is not None 
                        for prop in raw_data 
                        for option in prop.get("selectionOptions", [])
                    )
                }
            }
        }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports - now dynamically discovered."""
        # Return competition IDs instead of hardcoded sport names
        # These are the actual competition IDs from Dabble's API
        return [
            # American Football
            "7f7c2f8f-ff04-4e5a-a3c8-d503a523d9ad",  # NFL
            "402c1612-4f2b-44fa-8061-3bafdb4b673d",  # CFB
            "3c8ae166-3d40-4916-a23f-6d1dc370d117",  # NFL 2H
            "fdb6c2a3-58a0-4e1b-a2da-3485e0bc28b8",  # NFL Preseason
            
            # Baseball
            "dac474f4-2e9f-432d-a503-80f27452c41f",  # US Major League Baseball
            "eb653364-7935-4a4c-83ea-a1acac10218d",  # MLB All Star Game
            
            # Basketball
            "94edc3b0-009f-4369-88cb-d6a43f917f53",  # WNBA
            "2acf8935-8d89-455b-bb4b-dbfba9c4ae3b",  # NBA
            "584e0df1-37a5-41e6-9c10-a63455d5bbf9",  # CBB
            
            # Ice Hockey
            "ab37a56f-0131-41e8-8a5f-e29bce546f9a",  # US NHL
            
            # Tennis
            "691b8594-0f4d-44c7-8a78-2d921bb0a4d6",  # Women's Tennis
            "1609723f-3209-4306-9aa7-a153b21cef22",  # Men's Tennis
            "e7b578eb-674e-4b2d-a790-11050adcc0a9",  # ATP/WTA Tennis
            
            # Football/Soccer
            "b3ab59f2-631c-413a-b727-c8e49571cb64",  # England - Premier League
            "ea1f99fd-dc39-4d65-80a8-843eadde2272",  # Spain - LaLiga
            "4ad11b1e-e3a6-4bac-8969-d91ad222739e",  # Italy - Serie A
            
            # Esports
            "acd5b3f6-dd7a-484f-a4e5-a747badb32c6",  # Counter-Strike 2
            "086211fd-5445-4955-be1b-9ed7ba84641d",  # LoL
            "4de0349e-6657-4f63-aa4f-6034cfef867a",  # Dota 2
            "6b73cd8b-b2bd-4de5-8c2b-5d7553806f99",  # Valorant
            
            # MMA
            "aa4cbcb7-f944-4530-a3a2-1155a1565836",  # UFC
            
            # Boxing
            "0f818bbc-aaf1-4c8f-9b25-7b8e6a20a54c",  # Boxing
        ]

    @classmethod
    def get_default_market_groups(cls, sport: str) -> List[str]:
        """Get default market groups for a sport."""
        default_groups = {
            "basketball_wnba": [
                "Points", "Rebounds", "Assists", "Steals", "Blocks",
                "Points + Rebound + Assists", "Point + Rebound", "Turnovers"
            ],
            "football_cfb": [
                "Passing Yards", "Receiving Yards", "Rushing Yards",
                "Passing Touchdowns", "Receptions", "Interceptions"
            ],
            "baseball_mlb": [
                "Hits", "Runs", "RBIs", "Pitcher Strikeouts",
                "Total Bases", "Stolen Bases"
            ],
            "football_nfl": [
                "Passing Yards", "Rushing Yards", "Receiving Yards",
                "Passing Touchdowns", "Receptions", "Interceptions"
            ],
            "esports_cs2": ["Game 1 Kills", "Game 2 Kills"],
            "esports_lol": ["Game 1 Kills", "Game 2 Kills"]
        }
        
        return default_groups.get(sport, ["Points"])

"""
NoVig data streamer for KashRock Data Stream service.
Based on the working scrapers/novig.py implementation.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import structlog

from streamers.base import BaseStreamer

logger = structlog.get_logger()


class NovigStreamer(BaseStreamer):
    """Streamer for NoVig GraphQL API data - using working scraper implementation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # NoVig configuration
        self.sport = config.get("sport", "americanfootball_nfl")
        self.limit = config.get("limit", 10000)
        
        # API configuration - from working scraper
        self.base_url = "https://gql.novig.us/v1/graphql"
        self.client: Optional[httpx.AsyncClient] = None
        
        # Sport league mappings for NoVig API - from working scraper
        self.sport_league_map = {
            "baseball_mlb": "MLB",
            "basketball_wnba": "WNBA", 
            "americanfootball_nfl": "NFL",
            "americanfootball_ncaaf": "NCAAF",
            "basketball_nba": "NBA",
            "basketball_ncaa": "NCAAB"
        }
        
        self.league = self.sport_league_map.get(self.sport)
        if not self.league:
            raise ValueError(f"Unsupported sport: {self.sport}")
        
        # Headers from working scraper
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        logger.info("Initialized NoVig streamer", sport=self.sport, league=self.league)
    
    async def connect(self) -> bool:
        """Establish connection to NoVig GraphQL API."""
        try:
            # Create client
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
            
            # Simple connection test - just create the client
            logger.info("Successfully connected to NoVig GraphQL API", sport=self.sport, league=self.league)
            return True
            
        except Exception as e:
            logger.error("Failed to connect to NoVig GraphQL API", error=str(e))
            if self.client:
                await self.client.aclose()
                self.client = None
            return False
    
    async def disconnect(self):
        """Close connection to NoVig GraphQL API."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from NoVig GraphQL API")
    
    async def fetch_data(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Fetch data from NoVig GraphQL API - using working scraper implementation."""
        if not self.client:
            raise Exception("Not connected to NoVig GraphQL API")
        
        # GraphQL query from working scraper
        query = """
        query Home_Query($where_event: event_bool_exp!, $limit: Int!, $offset: Int!, $order_by: [event_order_by!]) {
          event(where: $where_event, limit: $limit, offset: $offset, order_by: $order_by) {
            id
            type
            description
            status
            league
            scheduled_start
            markets {
              is_consensus
              id
              type
              strike
              description
              status
              re_settled_at
              player {
                id
                full_name
                __typename
              }
              outcomes {
                id
                description
                available
                last
                competitor {
                  id
                  name
                }
              }
            }
          }
        }
        """
        
        # Working variables structure from original scraper
        start_date = datetime.now() - timedelta(days=2)  # include slight lookback
        end_date = datetime.now().replace(month=12, day=31)  # End of year
        
        # Pagination loop with rate limiting
        page_size = limit or 100  # Reduced page size to be gentler on API
        offset = 0
        all_events = []
        page_idx = 0
        max_pages = 3  # Limit total pages to prevent excessive requests

        while page_idx < max_pages:
            variables = {
                "where_event": {
                    "league": {"_eq": self.league},
                    # Include a broader set of statuses; we will filter later if needed
                    "status": {"_in": ["OPEN_PREGAME", "OPEN", "LIVE", "SCHEDULED", "PENDING"]},
                    "scheduled_start": {
                        "_gte": start_date.strftime("%Y-%m-%d"),
                        "_lte": end_date.strftime("%Y-%m-%d")
                    }
                },
                "limit": page_size,
                "offset": offset,
                "order_by": [{"scheduled_start": "asc"}]
            }

            payload = {"query": query, "variables": variables}

            logger.debug("NoVig GraphQL Payload", payload=json.dumps(payload, indent=2))
            # Add delay between requests to respect rate limits
            if page_idx > 0:
                await asyncio.sleep(1.0)  # 1 second delay between requests

            response = await self.client.post(self.base_url, json=payload)
            response.raise_for_status()

            response_data = response.json()
            logger.debug("NoVig Raw Response", response=json.dumps(response_data, indent=2))
            logger.info("NoVig page received", page=page_idx)
            
            # Debug: log the raw response structure
            if response_data:
                logger.info("Response keys", keys=list(response_data.keys()))
                if 'data' in response_data:
                    logger.info("Data keys", keys=list(response_data['data'].keys()))
                if 'errors' in response_data:
                    logger.error("GraphQL errors", errors=response_data['errors'])
            
            # Extract events
            events = response_data.get('data', {}).get('event', [])
            all_events.extend(events)
            
            logger.info("NoVig page processed", page=page_idx, events=len(events), total=len(all_events))
            
            # Check if we have more data
            if len(events) < page_size:
                break  # No more data
            
            offset += page_size
            page_idx += 1

        return {
            "sport": self.sport,
            "league": self.league,
            "events": all_events,
            "total_events": len(all_events),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return raw NoVig data with NO processing - pure raw GraphQL response."""
        
        # Just return the raw data with basic metadata - NO NORMALIZATION AT ALL
        return {
            "book": "novig",
            "sport": raw_data.get("sport"),
            "league": raw_data.get("league"),
            "total_events": raw_data.get("total_events", 0),
            "raw_events": raw_data.get("events", []),
            "timestamp": raw_data.get("timestamp"),
            "metadata": {
                "book_type": "sharp_pricing_graphql",
                "data_format": "raw_novig_graphql_response",
                "normalization_required": True,
                "note": "This is pure raw GraphQL data from NoVig API - no processing applied",
                "sample_structure": {
                    "events_count": len(raw_data.get("events", [])),
                    "sample_event_keys": list(raw_data.get("events", [{}])[0].keys()) if raw_data.get("events") else [],
                    "has_markets": any(event.get("markets") for event in raw_data.get("events", [])),
                    "sample_market_keys": list(
                        raw_data.get("events", [{}])[0].get("markets", [{}])[0].keys()
                    ) if raw_data.get("events", [{}]) and raw_data.get("events", [{}])[0].get("markets") else [],
                    "has_player_props": any(
                        market.get("player") 
                        for event in raw_data.get("events", []) 
                        for market in event.get("markets", [])
                    ),
                    "market_types_sample": list(set(
                        market.get("type") 
                        for event in raw_data.get("events", []) 
                        for market in event.get("markets", [])
                        if market.get("type")
                    ))[:10]  # Show first 10 unique market types
                }
            }
        }
    
    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports."""
        return [
            "baseball_mlb", "basketball_wnba", "americanfootball_nfl", "americanfootball_ncaaf",
            "basketball_nba", "basketball_ncaa", "hockey_nhl", "soccer_mls",
            "tennis_atp", "tennis_wta"
        ]
    
    @classmethod
    def get_default_leagues(cls, sport: str) -> str:
        """Get default league for a sport."""
        sport_league_map = {
            "baseball_mlb": "MLB",
            "basketball_wnba": "WNBA", 
            "americanfootball_nfl": "NFL",
            "americanfootball_ncaaf": "NCAAF",
            "basketball_nba": "NBA",
            "basketball_ncaa": "NCAAB",
            "hockey_nhl": "NHL",
            "soccer_mls": "MLS",
            "tennis_atp": "ATP",
            "tennis_wta": "WTA"
        }
        return sport_league_map.get(sport, "Unknown")

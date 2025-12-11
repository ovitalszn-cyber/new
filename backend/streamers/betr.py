import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

class BetrStreamer:
    """Streamer for Betr fantasy sports data."""
    
    def __init__(self, sport: str, limit: Optional[int] = None):
        self.sport = sport
        self.limit = limit
        self.client: Optional[httpx.AsyncClient] = None

        # Get API credentials from environment
        auth_token = os.getenv('BETR_AUTH_TOKEN')
        
        if not auth_token:
            logger.error("BETR_AUTH_TOKEN environment variable must be set")
            raise ValueError("BETR_AUTH_TOKEN environment variable must be set")
        
        logger.info("Betr streamer initialized with auth token", extra={"token_length": len(auth_token)})
        
        # Headers for API requests
        self.headers = {
            "x-datadog-parent-id": "6732671290219954554",
            "content-type": "application/json",
            "accept": "application/graphql-response+json, application/graphql+json, application/json, text/event-stream, multipart/mixed",
            "authorization": auth_token,
            "channel": "IOS",
            "fantasy-application-version": "3.29.3",
            "jurisdiction": "FL",
            "x-datadog-sampling-priority": "0",
            "x-datadog-trace-id": "6662943194800812298",
            "fantasy-api-version": "12.0",
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=3, i",
            "user-agent": "Betr/4720 CFNetwork/3860.100.1 Darwin/25.0.0",
            "cookie": "_ga_YNVSXM82RX=GS2.1.s1759065631$o1$g1$t1759065716$j52$l0$h0; _ga=GA1.1.620930274.1759065632",
            "x-datadog-origin": "rum"
        }
        
        # League mapping - only supported leagues
        self.league_map = {
            "football_nfl": "NFL",
            "basketball_nba": "NBA",
            "basketball_wnba": "WNBA",
            "baseball_mlb": "MLB",
            "soccer_epl": "EPL",
            "soccer_mls": "LLG",  # Soccer uses "LLG" league
            "mma_ufc": "UFC",
        }
        
        self.league = self.league_map.get(self.sport, "NFL")
        
        # GraphQL query for upcoming events
        self.graphql_query = """
        query LeagueUpcomingEvents($league: League!) {
          getUpcomingEventsV2(league: $league) {
            ...EventInfoData
            ... on TeamTournamentEvent {
              teams {
                ...TeamInfoWithPlayers
                __typename
              }
              __typename
            }
            ... on TeamVersusEvent {
              teams {
                ...TeamInfoWithPlayers
                __typename
              }
              __typename
            }
            ... on IndividualTournamentEvent {
              players {
                ...PlayerInfoWithProjections
                __typename
              }
              __typename
            }
            ... on IndividualVersusEvent {
              players {
                ...PlayerInfoWithProjections
                __typename
              }
              __typename
            }
            __typename
          }
        }
        fragment EventInfoData on EventV2 {
          id
          date
          status
          sport
          league
          competitionType
          dataFeedSourceIds {
            id
            source
            __typename
          }
          playerStructure
          venueDetails {
            name
            city
            country
            __typename
          }
          headerImage
          attributes {
            key
            value
            __typename
          }
          name
          icon
          dedicated
          __typename
        }
        fragment TeamInfoWithPlayers on Team {
          ...TeamInfo
          players {
            ...PlayerInfoWithProjections
            __typename
          }
          __typename
        }
        fragment TeamInfo on Team {
          id
          name
          league
          sport
          icon
          color
          secondaryColor
          largeIcon
          __typename
        }
        fragment PlayerInfoWithProjections on Player {
          ...PlayerInfo
          projections {
            ...PlayerProjection
            __typename
          }
          __typename
        }
        fragment PlayerInfo on Player {
          id
          firstName
          lastName
          icon
          position
          jerseyNumber
          attributes {
            key
            value
            __typename
          }
          record
          rank
          __typename
        }
        fragment PlayerProjection on Projection {
          marketId
          marketStatus
          isLive
          type
          playerRecentStats {
            stats {
              ...RecentStat
              __typename
            }
            averageValue
            __typename
          }
          label
          name
          key
          order
          value
          nonRegularPercentage
          nonRegularValue
          allowedOptions {
            marketOptionId
            outcome
            __typename
          }
          currentValue
          __typename
        }
        fragment RecentStat on PlayerRecentStat {
          value
          matchupDescription
          date
          __typename
        }
        """
        
        logger.info("Initialized Betr streamer", sport=self.sport, league=self.league)
    
    async def connect(self) -> None:
        """Connect to Betr API."""
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            follow_redirects=True
        )
        logger.info("Connected to Betr API")

    async def disconnect(self) -> None:
        """Disconnect from Betr API."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Disconnected from Betr API")

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch raw data from Betr API."""
        if not self.client:
            raise Exception("Not connected to Betr API")
        
        logger.info(f"Fetching Betr data for {self.sport} (league: {self.league})")
        url = "https://api.fantasy.betr.app/graphql"
        
        payload = {
            "operationName": "LeagueUpcomingEvents",
            "query": self.graphql_query,
            "variables": {
                "league": self.league
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            events = data.get("data", {}).get("getUpcomingEventsV2", [])
            
            # Limit results if specified
            if self.limit and isinstance(self.limit, int) and len(events) > self.limit:
                events = events[:self.limit]
            
            logger.info(f"Fetched {len(events)} events from Betr")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching Betr data: {e}")
            return []
    
    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports."""
        return [
            "football_nfl",
            "basketball_nba", 
            "basketball_wnba",
            "baseball_mlb",
            "soccer_epl",
            "soccer_mls",
            "mma_ufc",
        ]
    
    @classmethod
    def get_default_config(cls, sport: str) -> Dict[str, Any]:
        """Get default configuration for a sport."""
        return {
            "sport": sport,
            "limit": 1000,
            "market_types": ["player_props"],
            "book_type": "fantasy"
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get streamer information."""
        return {
            "name": "Betr",
            "sport": self.sport,
            "league": self.league,
            "limit": self.limit,
            "supported_sports": self.get_supported_sports(),
            "market_types": ["player_props"],
            "book_type": "fantasy"
        }


# Test the streamer
if __name__ == "__main__":
    async def test_betr():
        streamer = BetrStreamer("football_nfl", limit=1000)
        await streamer.connect()
        
        try:
            data = await streamer.fetch_data()
            print(f"Fetched {len(data)} events")
            if data:
                print(json.dumps(data[0], indent=2))
        finally:
            await streamer.disconnect()
    
    asyncio.run(test_betr())
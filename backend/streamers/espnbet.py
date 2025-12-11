"""ESPN BET streamer that fetches live data from ESPN BET Sportsbook API."""

import httpx
import structlog
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .base import BaseStreamer

logger = structlog.get_logger(__name__)


class ESPNBetStreamer(BaseStreamer):
    """Streamer that fetches live data from ESPN BET Sportsbook API."""

    BASE_URL = "https://sportsbook-espnbet.us-default.thescore.bet/graphql/persisted_queries"
    
    # Default headers extracted from curl command
    DEFAULT_HEADERS = {
        "x-client": "espn",
        "user-agent": "ESPN BET/25.22.1 iOS/26.2 (iPhone; Retina, 1284x2778)",
        "x-apollo-operation-name": "PageSection",
        "x-app": "ESPN BET iOS",
        "apollographql-client-name": "ESPN BET iOS",
        "priority": "u=3, i",
        "apollographql-client-version": "25.22.1",
        "x-app-version": "25.22.1",
        "x-platform": "ios",
        "accept-language": "en-US,en;q=0.9",
        "accept": "multipart/mixed;deferSpec=20220824,application/graphql-response+json,application/json",
        "content-type": "application/json",
        "x-apollo-operation-type": "query",
    }

    # Default GraphQL operation ID from curl command
    DEFAULT_OPERATION_ID = "df82f5689778aab89009f1393f894a34aa8ea6ba7d3b8344d6edcfe07837c489"

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None
        self.sport = config.get("sport", "americanfootball_nfl")
        self.section_id = config.get("section_id", "Section:647c3091-b79f-47bc-a96c-b053cc3a4a6a")
        
        # Optional auth headers from config
        self.auth_token = config.get("auth_token")
        self.cookies = config.get("cookies", {})
        self.baggage = config.get("baggage")
        self.install_id = config.get("install_id", "F2D66D43-3B12-4148-A13F-8B49E472A0D0")
        self.traceparent = config.get("traceparent")
        self.tracestate = config.get("tracestate")

    async def connect(self) -> bool:
        """Connect to ESPN BET API."""
        try:
            headers = self.DEFAULT_HEADERS.copy()
            
            # Add optional auth headers
            if self.auth_token:
                headers["x-anonymous-authorization"] = f"Bearer {self.auth_token}"
            
            if self.baggage:
                headers["baggage"] = self.baggage
            
            if self.install_id:
                headers["x-install-id"] = self.install_id
            
            if self.traceparent:
                headers["traceparent"] = self.traceparent
            
            if self.tracestate:
                headers["tracestate"] = self.tracestate
            
            # Add cookies if provided
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()]) if self.cookies else None
            
            self.session = httpx.AsyncClient(
                headers=headers,
                cookies=self.cookies if self.cookies else None,
                timeout=30.0,
                follow_redirects=True,
            )
            self.is_connected = True
            logger.info("Connected to ESPN BET API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ESPN BET API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from ESPN BET API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from ESPN BET API")

    async def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from ESPN BET API."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to ESPN BET API")
            return None

        try:
            # Build GraphQL query URL with persisted query
            operation_id = self.config.get("operation_id", self.DEFAULT_OPERATION_ID)
            
            # Build variables for the GraphQL query
            variables = {
                "chipCardIconImageMaxHeight": 28,
                "flagSizes": ["W40H40"],
                "headshotSizes": ["W160XH160"],
                "headshotSportIconSize": {
                    "maxHeight": 40,
                    "maxWidth": 40,
                    "width": 40
                },
                "id": self.section_id,
                "imageCardMaxWidth": 428,
                "imageSize": {"width": 428},
                "includeAdhocCarousel": False,
                "includeBadgeLabel": False,
                "includeEventBoxscore": False,
                "includeFeaturedMarketCardData": True,
                "includeFilters": False,
                "includeFootballPlayOffRankings": True,
                "includeFullEventFragment": False,
                "includeFullSectionFragment": True,
                "includeHeadshots": True,
                "includeMediaUrl": False,
                "includePropsHeadshots": True,
                "includeRichEvent": True,
                "includeStatisticAccrued": False,
                "isMedia": False,
                "jerseyImageSize": {
                    "maxHeight": 44,
                    "maxWidth": 44
                },
                "oddsFormat": "AMERICAN",
                "pageType": "PAGE",
                "playerFlagSizes": ["W40H40"],
                "playerHeadshotSizes": ["W70XH70"],
                "shouldFetchFeaturedBetsLabelImage": True
            }
            
            # Build extensions for persisted query
            extensions = {
                "clientLibrary": {
                    "name": "apollo-ios",
                    "version": "1.21.0"
                },
                "persistedQuery": {
                    "sha256Hash": operation_id,
                    "version": 1
                }
            }
            
            # Build query parameters
            params = {
                "extensions": json.dumps(extensions),
                "operationName": "PageSection",
                "variables": json.dumps(variables)
            }
            
            url = f"{self.BASE_URL}/{operation_id}"
            
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Successfully fetched ESPN BET data")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching ESPN BET data: {e.response.status_code} - {e.response.text[:200]}")
            return {
                "data": None,
                "errors": [{"message": f"HTTP {e.response.status_code}"}],
                "markets": [],
                "player_props": [],
                "events": []
            }
        except httpx.RequestError as e:
            logger.error(f"Request error fetching ESPN BET data: {e}")
            return {
                "data": None,
                "errors": [{"message": str(e)}],
                "markets": [],
                "player_props": [],
                "events": []
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching ESPN BET data: {e}")
            return {
                "data": None,
                "errors": [{"message": str(e)}],
                "markets": [],
                "player_props": [],
                "events": []
            }

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw ESPN BET data into standardized format - extracting EVERYTHING."""
        try:
            if not raw_data:
                logger.warning("No data found in ESPN BET response")
                return {
                    "markets": [],
                    "player_props": [],
                    "events": [],
                    "total_markets": 0,
                    "total_player_props": 0,
                    "total_events": 0,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Extract data from GraphQL response
            graphql_data = raw_data.get("data", {})
            if not graphql_data:
                # Check if there are errors
                errors = raw_data.get("errors", [])
                if errors:
                    logger.warning(f"GraphQL errors: {errors}")
                return {
                    "markets": [],
                    "player_props": [],
                    "events": [],
                    "total_markets": 0,
                    "total_player_props": 0,
                    "total_events": 0,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "errors": errors
                }
            
            # Extract section data - try different possible response structures
            section = None
            
            # Try pageSection first
            if "pageSection" in graphql_data:
                section = graphql_data.get("pageSection", {})
            # Try node (common GraphQL pattern)
            elif "node" in graphql_data:
                node = graphql_data.get("node")
                if isinstance(node, dict) and node.get("__typename") == "Section":
                    section = node
            # Try direct section access
            elif "section" in graphql_data:
                section = graphql_data.get("section", {})
            
            if not section:
                logger.warning("No section found in response. Available keys: %s", list(graphql_data.keys()))
                return {
                    "markets": [],
                    "player_props": [],
                    "events": [],
                    "total_markets": 0,
                    "total_player_props": 0,
                    "total_events": 0,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "raw_graphql_data": graphql_data
                }
            
            # Extract events and markets
            events = []
            markets = []
            player_props = []
            
            # Helper function to extract complete selection data
            def extract_selection(selection: Dict[str, Any]) -> Dict[str, Any]:
                """Extract all data from a selection."""
                extracted = {}
                
                # Basic fields
                extracted["id"] = selection.get("id", "")
                extracted["rawId"] = selection.get("rawId", "")
                extracted["type"] = selection.get("type", "")
                extracted["status"] = selection.get("status", "")
                
                # Odds
                odds = selection.get("odds", {})
                if odds:
                    extracted["odds"] = {
                        "formattedOdds": odds.get("formattedOdds", ""),
                        "numeratorLong": odds.get("numeratorLong", ""),
                        "denominatorLong": odds.get("denominatorLong", ""),
                        "decimal": None  # Calculate if needed
                    }
                    # Calculate decimal odds
                    try:
                        num = float(odds.get("numeratorLong", 0))
                        den = float(odds.get("denominatorLong", 1))
                        if den > 0:
                            if num >= 0:
                                extracted["odds"]["decimal"] = 1 + (num / den)
                            else:
                                extracted["odds"]["decimal"] = 1 + (abs(den) / abs(num))
                    except (ValueError, ZeroDivisionError):
                        pass
                else:
                    extracted["odds"] = {}
                
                # Points/Line
                points = selection.get("points", {})
                if points:
                    extracted["points"] = {
                        "decimalPoints": points.get("decimalPoints"),
                        "formattedPoints": points.get("formattedPoints", ""),
                        "raw": points
                    }
                else:
                    extracted["points"] = None
                
                # Name
                name = selection.get("name", {})
                if name:
                    extracted["name"] = {
                        "defaultName": name.get("defaultName", ""),
                        "fullName": name.get("fullName", ""),
                        "minimalName": name.get("minimalName", "")
                    }
                else:
                    extracted["name"] = {
                        "defaultName": "",
                        "fullName": "",
                        "minimalName": ""
                    }
                
                # Participant
                participant = selection.get("participant")
                if participant and isinstance(participant, dict):
                    extracted["participant"] = {
                        "id": participant.get("id", ""),
                        "name": participant.get("name", ""),
                        "fullName": participant.get("fullName", ""),
                        "shortName": participant.get("shortName", ""),
                        "mediumName": participant.get("mediumName", ""),
                        "abbreviation": participant.get("abbreviation", ""),
                        "type": participant.get("type", ""),
                        "__typename": participant.get("__typename", ""),
                        "resourceUri": participant.get("resourceUri", "")
                    }
                else:
                    extracted["participant"] = None
                
                # Rich participant (for player props)
                rich_participant = selection.get("richParticipant")
                rich_participant_v2 = selection.get("richParticipantV2")
                if rich_participant_v2:
                    extracted["richParticipant"] = {
                        "firstName": rich_participant_v2.get("firstName", ""),
                        "lastName": rich_participant_v2.get("lastName", ""),
                        "fullName": rich_participant_v2.get("fullName", ""),
                        "professionalName": rich_participant_v2.get("professionalName", ""),
                        "position": rich_participant_v2.get("position", ""),
                        "jerseyNumber": rich_participant_v2.get("jerseyNumber"),
                        "teams": rich_participant_v2.get("teams", []),
                        "headshots": rich_participant_v2.get("headshots", []),
                        "resourceUri": rich_participant_v2.get("resourceUri", "")
                    }
                elif rich_participant:
                    extracted["richParticipant"] = rich_participant
                else:
                    extracted["richParticipant"] = None
                
                # Selection name from FeaturedMarketsCarousel
                if "selectionName" in selection:
                    extracted["selectionName"] = selection.get("selectionName", "")
                if "marketName" in selection:
                    extracted["marketName"] = selection.get("marketName", "")
                
                # Keep all other fields
                for key, value in selection.items():
                    if key not in ["id", "rawId", "type", "status", "odds", "points", "name", "participant", "richParticipant", "richParticipantV2", "selectionName", "marketName"]:
                        extracted[key] = value
                
                return extracted
            
            # Helper function to extract complete market data
            def extract_market(market: Dict[str, Any], event_data: Dict[str, Any] = None) -> Dict[str, Any]:
                """Extract all data from a market."""
                extracted = {}
                
                # Basic market fields
                extracted["id"] = market.get("id", "")
                extracted["name"] = market.get("name", "")
                extracted["shortName"] = market.get("shortName", "")
                extracted["type"] = market.get("type", "")
                extracted["classification"] = market.get("classification", "")
                extracted["status"] = market.get("status", "")
                extracted["startTime"] = market.get("startTime")
                extracted["updatedAtTime"] = market.get("updatedAtTime")
                extracted["extraInformation"] = market.get("extraInformation")
                
                # Extract all selections with complete data
                selections = market.get("selections", [])
                extracted["selections"] = [extract_selection(sel) for sel in selections if isinstance(sel, dict)]
                
                # Add event data if provided
                if event_data:
                    extracted["event"] = event_data
                
                # Keep all other fields
                for key, value in market.items():
                    if key not in ["id", "name", "shortName", "type", "classification", "status", "startTime", "updatedAtTime", "extraInformation", "selections"]:
                        extracted[key] = value
                
                return extracted
            
            # Helper function to extract complete event data
            def extract_event(event: Dict[str, Any]) -> Dict[str, Any]:
                """Extract all data from an event."""
                extracted = {}
                
                # Basic event fields
                extracted["id"] = event.get("id", "")
                extracted["name"] = event.get("name", "")
                extracted["status"] = event.get("status") or event.get("eventStatus", "")
                extracted["startTime"] = event.get("startTime") or event.get("startsAt")
                extracted["resourceUri"] = event.get("resourceUri", "")
                
                # Away team/participant
                away = event.get("awayParticipant") or event.get("awayTeam", {})
                if away:
                    extracted["awayTeam"] = {
                        "id": away.get("id", ""),
                        "name": away.get("name", ""),
                        "fullName": away.get("fullName", ""),
                        "shortName": away.get("shortName", ""),
                        "mediumName": away.get("mediumName", ""),
                        "abbreviation": away.get("abbreviation", ""),
                        "resourceUri": away.get("resourceUri", ""),
                        "logos": away.get("logos", {}),
                        "colour1": away.get("colour1", ""),
                        "colour2": away.get("colour2", "")
                    }
                else:
                    extracted["awayTeam"] = None
                
                # Home team/participant
                home = event.get("homeParticipant") or event.get("homeTeam", {})
                if home:
                    extracted["homeTeam"] = {
                        "id": home.get("id", ""),
                        "name": home.get("name", ""),
                        "fullName": home.get("fullName", ""),
                        "shortName": home.get("shortName", ""),
                        "mediumName": home.get("mediumName", ""),
                        "abbreviation": home.get("abbreviation", ""),
                        "resourceUri": home.get("resourceUri", ""),
                        "logos": home.get("logos", {}),
                        "colour1": home.get("colour1", ""),
                        "colour2": home.get("colour2", "")
                    }
                else:
                    extracted["homeTeam"] = None
                
                # Standings
                away_standing = event.get("awayStanding", {})
                home_standing = event.get("homeStanding", {})
                extracted["awayStanding"] = away_standing.get("rankAndRecordString", "") if away_standing else ""
                extracted["homeStanding"] = home_standing.get("rankAndRecordString", "") if home_standing else ""
                
                # Sport/League info
                sport = event.get("sport", {})
                if isinstance(sport, dict):
                    extracted["sport"] = {
                        "slug": sport.get("slug", ""),
                        "name": sport.get("name", "")
                    }
                else:
                    extracted["sport"] = {"slug": str(sport), "name": ""}
                
                competition = event.get("competition", {})
                if isinstance(competition, dict):
                    extracted["competition"] = {
                        "name": competition.get("name", ""),
                        "slug": competition.get("slug", "")
                    }
                else:
                    extracted["competition"] = {"name": "", "slug": ""}
                
                league = event.get("league", {})
                if isinstance(league, dict):
                    extracted["league"] = {
                        "slug": league.get("slug", ""),
                        "leveling": league.get("leveling", "")
                    }
                else:
                    extracted["league"] = {"slug": "", "leveling": ""}
                
                # Keep all other fields
                for key, value in event.items():
                    if key not in ["id", "name", "status", "eventStatus", "startTime", "startsAt", "resourceUri", 
                                  "awayParticipant", "awayTeam", "homeParticipant", "homeTeam", 
                                  "awayStanding", "homeStanding", "sport", "competition", "league"]:
                        extracted[key] = value
                
                return extracted
            
            # Helper function to check if market is a player prop
            def is_player_prop(market):
                """Check if a market is a player prop."""
                # Check classification field
                classification = market.get("classification", "").upper()
                if classification == "PLAYER_PROP":
                    return True
                
                # Check market type
                market_type = market.get("type", "").upper()
                if "PLAYER" in market_type or "PROP" in market_type:
                    return True
                
                # Check selections for Player participants
                selections = market.get("selections", [])
                for selection in selections:
                    participant = selection.get("participant")
                    if participant and isinstance(participant, dict):
                        typename = participant.get("__typename", "")
                        if typename == "Player":
                            return True
                
                # Check market name
                market_name = market.get("name", "").lower()
                if "player" in market_name and ("prop" in market_name or "touchdown" in market_name or "yards" in market_name or "reception" in market_name):
                    return True
                
                return False
            
            # Extract from sectionChildren (main structure in ESPN BET)
            section_children = section.get("sectionChildren", [])
            
            # Process MarketplaceShelf which contains GridMarketCard items
            for child in section_children:
                if not isinstance(child, dict):
                    continue
                
                child_type = child.get("__typename", "")
                
                # MarketplaceShelf contains GridMarketCard items in marketplaceShelfChildren
                if child_type == "MarketplaceShelf":
                    marketplace_children = child.get("marketplaceShelfChildren", [])
                    for marketplace_child in marketplace_children:
                        if isinstance(marketplace_child, dict) and marketplace_child.get("__typename") == "GridMarketCard":
                            # Extract event info first
                            fallback_event = marketplace_child.get("fallbackEvent")
                            rich_event = marketplace_child.get("richEvent")
                            event = rich_event if rich_event else fallback_event
                            event_data = extract_event(event) if event and isinstance(event, dict) else None
                            
                            if event_data:
                                events.append(event_data)
                            
                            # Extract markets - these are main markets (moneyline, spread, total)
                            child_markets = marketplace_child.get("markets", [])
                            for market in child_markets:
                                if isinstance(market, dict):
                                    market_type = market.get("type", "")
                                    classification = market.get("classification", "")
                                    
                                    # Extract complete market data
                                    extracted_market = extract_market(market, event_data)
                                    
                                    if classification == "PLAYER_PROP":
                                        player_props.append(extracted_market)
                                    elif market_type in ("MONEYLINE", "SPREAD", "TOTAL"):
                                        markets.append(extracted_market)
                                    else:
                                        # Default to markets if not clearly a player prop
                                        markets.append(extracted_market)
                            
                            # Check recommendedProps for individual player props
                            recommended_props = marketplace_child.get("recommendedProps", {})
                            if recommended_props:
                                recommended_markets = recommended_props.get("markets", [])
                                for market in recommended_markets:
                                    if isinstance(market, dict) and is_player_prop(market):
                                        extracted_market = extract_market(market, event_data)
                                        player_props.append(extracted_market)
                
                # GridMarketCard can also be directly in sectionChildren
                elif child_type == "GridMarketCard":
                    # Extract event info first
                    fallback_event = child.get("fallbackEvent")
                    rich_event = child.get("richEvent")
                    event = rich_event if rich_event else fallback_event
                    event_data = extract_event(event) if event and isinstance(event, dict) else None
                    
                    if event_data:
                        events.append(event_data)
                    
                    # Extract markets - these are main markets (moneyline, spread, total)
                    child_markets = child.get("markets", [])
                    for market in child_markets:
                        if isinstance(market, dict):
                            market_type = market.get("type", "")
                            classification = market.get("classification", "")
                            
                            # Extract complete market data
                            extracted_market = extract_market(market, event_data)
                            
                            if classification == "PLAYER_PROP":
                                player_props.append(extracted_market)
                            elif market_type in ("MONEYLINE", "SPREAD", "TOTAL"):
                                markets.append(extracted_market)
                            else:
                                # Default to markets if not clearly a player prop
                                markets.append(extracted_market)
                    
                    # Check recommendedProps for individual player props
                    recommended_props = child.get("recommendedProps", {})
                    if recommended_props:
                        recommended_markets = recommended_props.get("markets", [])
                        for market in recommended_markets:
                            if isinstance(market, dict) and is_player_prop(market):
                                extracted_market = extract_market(market, event_data)
                                player_props.append(extracted_market)
                    
                    # Check recommendedProps for individual player props
                    recommended_props = child.get("recommendedProps", {})
                    if recommended_props:
                        recommended_markets = recommended_props.get("markets", [])
                        for market in recommended_markets:
                            if isinstance(market, dict) and is_player_prop(market):
                                extracted_market = extract_market(market, event_data)
                                player_props.append(extracted_market)
                
                # FeaturedMarketsCarousel contains PARLAYS - we skip these as user wants individual player props only
                # Individual player props are not available at the section level in ESPN BET API
                # They would need to be accessed via individual event endpoints
                elif child_type == "FeaturedMarketsCarousel":
                    # Skip parlays - user wants individual player props only
                    # Note: Individual player props are not available at section level
                    # They would require accessing individual event pages/endpoints
                    pass
            
            # Also check for eventGroups (legacy structure)
            event_groups = section.get("eventGroups", [])
            for event_group in event_groups:
                if isinstance(event_group, dict):
                    group_events = event_group.get("events", [])
                    for event in group_events:
                        if isinstance(event, dict):
                            event_data = extract_event(event)
                            events.append(event_data)
                            
                            event_markets = event.get("markets", [])
                            for market in event_markets:
                                if isinstance(market, dict):
                                    extracted_market = extract_market(market, event_data)
                                    if is_player_prop(market):
                                        player_props.append(extracted_market)
                                    else:
                                        markets.append(extracted_market)
            
            processed_data = {
                "markets": markets,
                "player_props": player_props,
                "events": events,
                "total_markets": len(markets),
                "total_player_props": len(player_props),
                "total_events": len(events),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"Processed ESPN BET data: {len(markets)} markets, "
                f"{len(player_props)} player props, {len(events)} events"
            )
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process ESPN BET data: {e}")
            return {
                "markets": [],
                "player_props": [],
                "events": [],
                "error": str(e),
                "processed_at": datetime.now(timezone.utc).isoformat()
            }

    @classmethod
    def get_supported_sports(cls) -> List[str]:
        """Get list of supported sports.
        
        ESPN BET supports:
        - American Football: NFL, CFB
        - Basketball: NBA, WNBA, NCAAB
        - Baseball: MLB
        - Ice Hockey: NHL
        - Soccer: Various leagues
        - And more
        """
        return [
            "football_nfl",
            "football_cfb",
            "basketball_nba",
            "basketball_wnba",
            "basketball_ncaa",
            "baseball_mlb",
            "icehockey_nhl",
        ]

    async def health_check(self) -> bool:
        """Check if ESPN BET API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Try a simple fetch
            data = await self.fetch_data()
            return data is not None and "data" in data

        except Exception as e:
            logger.error(f"ESPN BET health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"ESPNBetStreamer(name={self.name}, connected={self.is_connected}, sport={self.sport})"

    def __repr__(self) -> str:
        return self.__str__()


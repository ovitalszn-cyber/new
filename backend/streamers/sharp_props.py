"""Sharp Proptimizer streamer - fetches player props with EV data from DFS books."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog

from streamers.base import BaseStreamer
from processing.stat_canonicalizer import canonicalize_stat_type

logger = structlog.get_logger()


class SharpPropsStreamer(BaseStreamer):
    """Streamer that fetches player props with EV data from Sharp Proptimizer (DFS books).
    
Note: Sharp Proptimizer includes consensus pricing, projections, and odds-to-hit (EV data).
    This can be wired into both v6/props (without EV fields) and v6/ev (with EV fields).
    """

    BASE_URL = "https://graph.sharp.app/operations/v1/proptimizer"
    BOOKS_URL = "https://graph.sharp.app/operations/v2/sportsbooks/ByGeo"
    API_HASH = "a945f208"
    
    # Canonical sport mapping (Sharp sport codes → KashRock canonical sport keys)
    SPORT_MAP = {
        'nfl': 'americanfootball_nfl',
        'ncaaf': 'americanfootball_ncaaf',
        'nba': 'basketball_nba',
        'ncaab': 'basketball_ncaab',
        'nhl': 'icehockey_nhl',
        'mlb': 'baseball_mlb',
    }
    
    # Reverse mapping for lookups
    CANONICAL_TO_SHARP = {v: k for k, v in SPORT_MAP.items()}
    
    # Book mapping - will be populated dynamically from API
    BOOK_MAP = {}
    
    DEFAULT_HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "wg-sdk-version": "0.184.2",
        "user-agent": "SharpApp/2406 CFNetwork/3860.300.21 Darwin/25.2.0",
        "priority": "u=3, i",
        "accept-language": "en-US,en;q=0.9",
    }

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        super().__init__(name, config)
        self.is_connected = False
        self.session: Optional[httpx.AsyncClient] = None
        
        # books=None means fetch ALL discovered books (will skip 404s)
        # books=[...] means only fetch specific books
        self.books = config.get("books", None)
        self.fetch_all_books = self.books is None

    async def connect(self) -> bool:
        """Connect to Sharp API and fetch available books."""
        try:
            if self.session is None:
                self.session = httpx.AsyncClient(
                    headers=self.DEFAULT_HEADERS,
                    timeout=30.0,
                    follow_redirects=True,
                )
            
            # Fetch available books
            await self._fetch_available_books()
            
            self.is_connected = True
            logger.info(f"Connected to Sharp API with {len(self.BOOK_MAP)} books available")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Sharp API: {e}")
            self.is_connected = False
            return False

    async def _fetch_available_books(self) -> None:
        """Fetch list of available books from Sharp API."""
        try:
            response = await self.session.get(
                self.BOOKS_URL,
                params={"wg_api_hash": self.API_HASH}
            )
            response.raise_for_status()
            data = response.json()
            
            # Sharp uses specific slugs that don't match book names
            # Mapping discovered via mitmproxy and testing
            SHARP_SLUG_MAP = {
                "PrizePicks": "prizepicks",
                "Sleeper": "sleeper",
                "Underdog Sportsbook": "underdog",  # NOT underdogsportsbook!
                "DraftKings Pick 6": "draftkings-pick6", # Discovered via brute-force
                "Fliff": "fliff",
                "Novig": "novig",
                "Betr": "betr",
                "Betr Picks": "betr-picks",
                "ParlayPlay": "parlayplay",
                "HotStreak": "hotstreak",
                "Polymarket": "polymarket",
                "Kalshi": "kalshi",
                "OwnersBox": "ownersbox",
                "Thrillzz": "thrillzz",
                "Boom Fantasy": "boom-fantasy", # Discovered via brute-force
                "Dabble Fantasy": "dabble",
                "Rebet": "rebet",
                "Rebet Props City": "rebetpropscity",
                "Stake US": "stakeus",
                "Onyx Odds": "onyx",
                "Sporttrade": "sporttrade",
                "Kutt": "kutt",
            }
            
            # Parse books from ALL categories dynamically
            all_categories = data.get('data', {}).keys()
            
            for category in all_categories:
                books = data.get('data', {}).get(category, [])
                
                # Handle both list and dict responses
                if isinstance(books, list):
                    for book in books:
                        if not isinstance(book, dict):
                            continue
                            
                        # CRITICAL: Proptimizer endpoint ONLY works for DFS/Pickem books
                        if not (book.get('isFantasy') or book.get('isPickem')):
                            continue
                            
                        book_id = book.get('sportsbookId')
                        book_name = book.get('sportsbook')
                        
                        if not book_id or not book_name:
                            continue
                        
                        # Only add if not already in map (avoid duplicates)
                        if book_id not in [b['id'] for b in self.BOOK_MAP.values()]:
                            # Use mapping if available, otherwise fallback
                            slug = SHARP_SLUG_MAP.get(book_name, book_name.lower().replace(' ', ''))
                            
                            self.BOOK_MAP[slug] = {
                                'id': book_id,
                                'name': book_name,
                                'slug': slug,
                                'isFantasy': book.get('isFantasy', False),
                                'isPickem': book.get('isPickem', False),
                                'category': category,
                            }
            
            logger.info(f"Fetched {len(self.BOOK_MAP)} DFS/Pick'em books from Sharp API")
            
        except Exception as e:
            logger.warning(f"Failed to fetch Sharp books list: {e}, using defaults")
            # Fallback to known working books
            self.BOOK_MAP = {
                'prizepicks': {'id': 30, 'name': 'PrizePicks', 'slug': 'prizepicks', 'isFantasy': True, 'isPickem': True},
                'sleeper': {'id': 42, 'name': 'Sleeper', 'slug': 'sleeper', 'isFantasy': True, 'isPickem': True},
                'underdog': {'id': 41, 'name': 'Underdog Sportsbook', 'slug': 'underdog', 'isFantasy': True, 'isPickem': True},
            }

    async def disconnect(self) -> None:
        """Disconnect from Sharp API."""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from Sharp API")

    async def fetch_data(self, sport: str = None, markets: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Fetch data from Sharp API for all configured books."""
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            logger.error("Not connected to Sharp API")
            return None

        all_data = {
            'books': {},
            'total_markets': 0,
            'total_players': 0,
            'total_events': 0,
        }

        # Determine which books to fetch
        if self.fetch_all_books:
            # Fetch ALL 104 books
            books_to_fetch = list(self.BOOK_MAP.keys())
            logger.info(f"Fetching data from ALL {len(books_to_fetch)} Sharp books")
        else:
            books_to_fetch = self.books
            logger.info(f"Fetching data from {len(books_to_fetch)} configured Sharp books")

        # Fetch data for each book
        for book_slug in books_to_fetch:
            if book_slug not in self.BOOK_MAP:
                logger.warning(f"Unknown book: {book_slug}, skipping")
                continue
            
            try:
                book_data = await self._fetch_book_data(book_slug)
                if book_data:
                    all_data['books'][book_slug] = book_data
                    all_data['total_markets'] += len(book_data.get('data', {}).get('markets', []))
                    all_data['total_players'] += len(book_data.get('data', {}).get('players', []))
                    all_data['total_events'] += len(book_data.get('data', {}).get('events', []))
            except Exception as e:
                logger.error(f"Failed to fetch data for {book_slug}: {e}")
                continue

        logger.info(f"Fetched Sharp data: {all_data['total_markets']} markets across {len(all_data['books'])} books")
        return all_data

    async def _fetch_book_data(self, book_slug: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a specific book, trying multiple endpoint versions."""
        
        # Endpoints to try (V2 is preferred, but some books like Underdog use V1)
        endpoints = [
            f"{self.BASE_URL}/{book_slug}/ByDatesV2",
            f"{self.BASE_URL}/{book_slug}/ByDates"
        ]
        
        for url in endpoints:
            try:
                params = {"wg_api_hash": self.API_HASH}
                
                # Only log info for the first attempt to avoid noise
                if "ByDatesV2" in url:
                    logger.info(f"Fetching Sharp data for book: {book_slug}")
                else:
                    logger.debug(f"Retrying with V1 endpoint for: {book_slug}")
                
                response = await self.session.get(url, params=params)
                
                # If 404, this endpoint version might not exist for this book
                if response.status_code == 404:
                    continue
                    
                response.raise_for_status()
                
                data = response.json()
                
                markets_count = len(data.get('data', {}).get('markets', []))
                players_count = len(data.get('data', {}).get('players', []))
                events_count = len(data.get('data', {}).get('events', []))
                
                if markets_count > 0:
                    logger.info(f"Fetched {book_slug}: {markets_count} markets (via {url.split('/')[-1]})")
                    return data
                
            except Exception as e:
                # Log error but continue to next endpoint if available
                logger.debug(f"Failed fetching {book_slug} via {url}: {e}")
                continue
                
        # If we get here, all endpoints failed or returned no data
        logger.warning(f"No data found for {book_slug} (tried V2 and V1 endpoints)")
        return None

    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Sharp data into standardized format."""
        try:
            if not raw_data or 'books' not in raw_data:
                return {"error": "No data found in Sharp response"}
            
            all_props = []
            
            # Process each book's data
            for book_slug, book_data in raw_data['books'].items():
                data = book_data.get('data', {})
                markets = data.get('markets', [])
                players_map = {p['playerId']: p for p in data.get('players', [])}
                events_map = {e['eventId']: e for e in data.get('events', [])}
                
                # Process markets
                for market in markets:
                    if not isinstance(market, dict):
                        continue
                    
                    player_id = market.get('playerId')
                    player = players_map.get(player_id, {})
                    
                    event_id = market.get('eventId')
                    event = events_map.get(event_id, {})
                    
                    # Extract sport from event ID (format: "nhl-2025121133505D9E")
                    sharp_sport = event_id.split('-')[0] if event_id and '-' in event_id else ''
                    canonical_sport = self.SPORT_MAP.get(sharp_sport, '')
                    
                    # Get sportsbook info
                    sportsbook_id = market.get('sportsbookId')
                    book_info = self.BOOK_MAP.get(book_slug, {})
                    
                    # Normalize book name for KashRock (lowercase, no spaces)
                    normalized_book = book_slug
                    
                    # Canonicalize stat type using KashRock's stat canonicalizer
                    raw_stat_type = market.get('marketType', '')
                    player_name = player.get('fullName')
                    # Calculate edge metrics
                    consensus_price = market.get('consensusPrice')
                    actual_price = market.get('price')
                    canonical_stat = canonicalize_stat_type(
                        raw_stat_type, 
                        sport=canonical_sport, 
                        player_name=player_name
                    )
                    
                    
                    
                    # Calculate edge metrics from Sharp's data
                    consensus_price = market.get('consensusPrice')
                    actual_price = market.get('price')

                    all_props.append({
                        # Player info
                        'player_id': player_id,
                        'player_id': player_id,
                        'player_name': player.get('fullName'),
                        'team': player.get('teamKey') or player.get('team') or player.get('teamAbbr'),
                        'player_team': player.get('teamKey') or player.get('team') or player.get('teamAbbr'),
                        'position': player.get('position'),
                        'headshot_url': player.get('headshotUrl'),
                        'injury_status': player.get('injuryStatus'),
                        'injury_notes': player.get('injuryNotes'),
                        
                        # Market info (canonical only)
                        'market_key': market.get('marketKey'),
                        'stat_type': canonical_stat,  # Canonicalized stat type only
                        'line': market.get('line'),
                        'direction': market.get('outcomeType', '').lower(),  # over/under
                        'odds': actual_price,  # American odds
                        'is_alt': market.get('isAlt', False),
                        
                        # Consensus & EV data (Sharp provides this)
                        'consensus_line': market.get('consensusLine'),
                        'consensus_price': consensus_price,
                        'ev_edge': market.get('edge') or market.get('ev'), # Use API provided edge if avaiable
                        
                        # Sharp projections
                        'sportsbook_projection': market.get('sportsbookProjection'),
                        'odds_to_hit': market.get('oddsToHit'),
                        
                        # Book info (normalized for KashRock)
                        'book_id': normalized_book,
                        'book': normalized_book,
                        'book_name': book_info.get('name'),
                        'sportsbook_id': sportsbook_id,
                        'is_fantasy': book_info.get('isFantasy', False),
                        'is_pickem': book_info.get('isPickem', False),
                        
                        # Event & Sport info (canonical)
                        'game_id': event_id,
                        'game_date': event.get('gameDate'),
                        'home_team_id': event.get('homeTeamId'),
                        'away_team_id': event.get('awayTeamId'),
                        'sport': canonical_sport,  # KashRock canonical sport key
                        
                        # Source
                        'source': 'kashrock',
                        
                        # Links
                        'link': market.get('link'),
                        'links': market.get('links', []),
                    })
            
            processed_data = {
                'player_props': all_props,
                'total_props': len(all_props),
                'total_books': len(raw_data['books']),
                'books_processed': list(raw_data['books'].keys()),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed Sharp data: {len(all_props)} props from {len(raw_data['books'])} books")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process Sharp data: {e}")
            return {"error": str(e)}

    def get_supported_books(self) -> List[str]:
        """Get list of supported books."""
        return list(self.BOOK_MAP.keys())

    def get_book_info(self, book_slug: str) -> Optional[Dict[str, Any]]:
        """Get info for a specific book."""
        return self.BOOK_MAP.get(book_slug)

    async def health_check(self) -> bool:
        """Check if Sharp API is healthy."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                return False

            # Test with PrizePicks
            data = await self._fetch_book_data('prizepicks')
            return data is not None and len(data.get('data', {}).get('markets', [])) > 0

        except Exception as e:
            logger.error(f"Sharp health check failed: {e}")
            return False

    def __str__(self) -> str:
        return f"SharpStreamer(name={self.name}, connected={self.is_connected}, books={len(self.books)})"

    def __repr__(self) -> str:
        return self.__str__()

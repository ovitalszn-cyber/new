"""
Player roster database for team assignment and player enrichment.

Lightweight in-memory roster cache backed by Redis for fast lookups.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json

import structlog
from redis.asyncio import Redis

from config import get_settings

logger = structlog.get_logger(__name__)


class PlayerRosterDB:
    """Redis-backed player roster database for fast lookups."""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.settings = get_settings()
        
    async def connect(self) -> None:
        """Establish Redis connection."""
        if self.redis is not None:
            return
            
        try:
            self.redis = Redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to player roster Redis")
            
        except Exception as e:
            logger.error("Failed to connect to player roster Redis", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("Disconnected from player roster Redis")
    
    async def upsert_player(
        self,
        player_name: str,
        team_name: str,
        sport: str,
        position: Optional[str] = None,
        jersey_number: Optional[str] = None,
        player_id: Optional[str] = None,
        source: str = "manual",
        season: Optional[str] = None,
        is_active: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Insert or update a player roster entry in Redis."""
        if not self.redis:
            await self.connect()
        
        # Normalize names for consistent lookups
        player_normalized = player_name.lower().strip()
        team_normalized = team_name.lower().strip()
        
        # Store player data
        player_data = {
            "player_name": player_name,
            "team_name": team_name,
            "sport": sport,
            "position": position,
            "jersey_number": jersey_number,
            "player_id": player_id,
            "source": source,
            "season": season or str(datetime.now().year),
            "is_active": is_active,
            "last_updated": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Primary key: player_normalized:sport:season
        primary_key = f"roster:player:{player_normalized}:{sport}:{season or 'current'}"
        await self.redis.setex(
            primary_key,
            86400 * 30,  # 30 days TTL
            json.dumps(player_data)
        )
        
        # Index by team for reverse lookups
        team_key = f"roster:team:{team_normalized}:{sport}:{season or 'current'}"
        await self.redis.sadd(team_key, player_normalized)
        await self.redis.expire(team_key, 86400 * 30)
        
        # Index for game-context lookups (player -> team mapping)
        mapping_key = f"roster:mapping:{player_normalized}:{sport}"
        await self.redis.setex(
            mapping_key,
            86400 * 30,
            team_name  # Store canonical team name
        )

    async def upsert_matchup(
        self,
        sport: str,
        event_id: str,
        home_team: str,
        away_team: str,
        date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store matchup information for quick team lookup."""
        if not self.redis:
            await self.connect()

        if not sport or not event_id or not home_team or not away_team:
            logger.debug(
                "Skipping matchup upsert due to missing data",
                sport=sport,
                event_id=event_id,
                home_team=home_team,
                away_team=away_team,
            )
            return

        matchup_payload = {
            "sport": sport,
            "event_id": event_id,
            "home_team": home_team,
            "away_team": away_team,
            "date": date,
            "metadata": metadata or {},
        }

        matchup_key = f"matchup:{sport}:{event_id}"
        await self.redis.setex(matchup_key, 86400 * 30, json.dumps(matchup_payload))

        # Also store lookup by slug (home vs away) to support event-name based lookups
        home_slug = home_team.lower().strip()
        away_slug = away_team.lower().strip()

        slug = f"{home_slug}|{away_slug}"
        slug_key = f"matchup_slug:{sport}:{slug}"
        await self.redis.setex(slug_key, 86400 * 30, json.dumps(matchup_payload))

        reverse_slug = f"{away_slug}|{home_slug}"
        reverse_key = f"matchup_slug:{sport}:{reverse_slug}"
        await self.redis.setex(reverse_key, 86400 * 30, json.dumps(matchup_payload))

    async def lookup_matchup(
        self,
        sport: str,
        event_id: Optional[str] = None,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve stored matchup information."""
        if not self.redis:
            await self.connect()

        if event_id:
            matchup_key = f"matchup:{sport}:{event_id}"
            payload = await self.redis.get(matchup_key)
            if payload:
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    logger.warning("Failed to decode matchup payload", key=matchup_key)

        if home_team and away_team:
            slug = f"{home_team.lower().strip()}|{away_team.lower().strip()}"
            slug_key = f"matchup_slug:{sport}:{slug}"
            payload = await self.redis.get(slug_key)
            if payload:
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    logger.warning("Failed to decode matchup slug payload", key=slug_key)

        return None

    async def lookup_player_team(
        self,
        player_name: str,
        sport: str,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        season: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Look up a player's team given their name and game context.
        
        Args:
            player_name: Player's name to look up
            sport: Sport key (e.g., 'basketball_nba')
            home_team: Home team for the game (optional, helps disambiguate)
            away_team: Away team for the game (optional, helps disambiguate)
            season: Season identifier (optional, defaults to current)
            
        Returns:
            Dict with player_team, opponent_team, position, etc. or None if not found
        """
        if not self.redis:
            await self.connect()
        
        player_normalized = player_name.lower().strip()
        season_key = season or "current"
        
        # Try exact lookup first
        primary_key = f"roster:player:{player_normalized}:{sport}:{season_key}"
        player_data_str = await self.redis.get(primary_key)
        
        # If not found, try without common suffixes (Jr, Sr, III, IV, etc.)
        if not player_data_str:
            import re
            # Strip common suffixes
            name_without_suffix = re.sub(r'\s+(jr\.?|sr\.?|iii|iv|v|ii)$', '', player_normalized, flags=re.IGNORECASE).strip()
            if name_without_suffix != player_normalized:
                primary_key = f"roster:player:{name_without_suffix}:{sport}:{season_key}"
                player_data_str = await self.redis.get(primary_key)
        
        if player_data_str:
            player_data = json.loads(player_data_str)
            player_team = player_data["team_name"]
            
            # Determine opponent if game context provided
            opponent_team = None
            if home_team and away_team:
                # Canonicalize all team names for comparison
                from utils.team_names import canonicalize_team
                
                canonical_player_team = canonicalize_team(player_team, sport) or player_team
                canonical_home = canonicalize_team(home_team, sport) or home_team
                canonical_away = canonicalize_team(away_team, sport) or away_team
                
                # Compare canonical names (case-insensitive)
                player_team_lower = canonical_player_team.lower().strip()
                home_lower = canonical_home.lower().strip()
                away_lower = canonical_away.lower().strip()
                
                if player_team_lower == home_lower:
                    opponent_team = canonical_away
                elif player_team_lower == away_lower:
                    opponent_team = canonical_home
            
            return {
                "player_name": player_data["player_name"],
                "player_team": player_team,
                "opponent_team": opponent_team,
                "position": player_data.get("position"),
                "jersey_number": player_data.get("jersey_number"),
                "player_id": player_data.get("player_id"),
                "metadata": player_data.get("metadata", {}),
                "match_confidence": "high"
            }
        
        # Fallback: check quick mapping
        mapping_key = f"roster:mapping:{player_normalized}:{sport}"
        team_name = await self.redis.get(mapping_key)
        
        if team_name:
            # Verify against game context if provided
            if home_team and away_team:
                team_normalized = team_name.lower().strip()
                home_normalized = home_team.lower().strip()
                away_normalized = away_team.lower().strip()
                
                if team_normalized not in [home_normalized, away_normalized]:
                    logger.warning(
                        "Player team mismatch with game context",
                        player=player_name,
                        roster_team=team_name,
                        game_teams=f"{home_team} vs {away_team}"
                    )
                    return None
                
                opponent_team = away_team if team_normalized == home_normalized else home_team
            else:
                opponent_team = None
            
            return {
                "player_name": player_name,
                "player_team": team_name,
                "opponent_team": opponent_team,
                "position": None,
                "jersey_number": None,
                "player_id": None,
                "metadata": {},
                "match_confidence": "medium"
            }
        
        return None
    
    async def get_team_roster(
        self,
        team_name: str,
        sport: str,
        season: Optional[str] = None
    ) -> List[str]:
        """Get all players for a team."""
        if not self.redis:
            await self.connect()
        
        team_normalized = team_name.lower().strip()
        season_key = season or "current"
        
        team_key = f"roster:team:{team_normalized}:{sport}:{season_key}"
        players = await self.redis.smembers(team_key)
        
        return list(players) if players else []

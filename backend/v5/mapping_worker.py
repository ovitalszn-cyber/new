"""
Mapping Worker - Transforms source envelopes to canonical schema.

Uses versioned mapping repository (JSON) with unit tests.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, replace
from datetime import datetime
import structlog
import json
from pathlib import Path

from v5.connector_adapter import SourceEnvelope
from db.player_roster_db import PlayerRosterDB

logger = structlog.get_logger()


@dataclass
class CanonicalEnvelope:
    """Canonical schema for events/markets."""
    sport: str
    start_ts: str  # ISO timestamp
    markets: List[Dict[str, Any]]  # [{key, runners, ...}]
    provenance: Dict[str, Any]  # Full provenance tracking
    source: str
    source_event_id: str
    # Optional fields (must come after required fields)
    canonical_event_id: Optional[str] = None  # Set by entity resolver
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MappingWorker:
    """Stateless mapping worker that transforms source → canonical."""
    
    def __init__(self, mapping_repo_path: Optional[str] = None):
        """
        Initialize mapping worker.
        
        Args:
            mapping_repo_path: Path to versioned mapping repository (JSON files)
        """
        if mapping_repo_path is None:
            # Default to mappings directory (project root)
            # __file__ is src/v5/mapping_worker.py, so go up 3 levels to project root
            mapping_repo_path = Path(__file__).parent.parent.parent.parent / "mappings"
        
        self.mapping_repo_path = Path(mapping_repo_path)
        self.mapping_repo_path.mkdir(exist_ok=True)
        
        # Load mapping rules
        self.mapping_rules = self._load_mapping_rules()
        
        # Initialize roster database for team enrichment
        self.roster_db = PlayerRosterDB()
        self._roster_connected = False
        
        logger.info("Mapping worker initialized", repo_path=str(self.mapping_repo_path))
    
    def _load_mapping_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load versioned mapping rules from repository."""
        rules = {}
        
        # Load default mappings
        default_mappings_file = self.mapping_repo_path / "default_mappings.json"
        if default_mappings_file.exists():
            try:
                with open(default_mappings_file, "r") as f:
                    rules = json.load(f)
            except Exception as e:
                logger.warning("Failed to load default mappings", error=str(e))
        
        # Load source-specific mappings
        for source_file in self.mapping_repo_path.glob("*_mappings.json"):
            source_name = source_file.stem.replace("_mappings", "")
            try:
                with open(source_file, "r") as f:
                    source_rules = json.load(f)
                    rules[source_name] = source_rules
            except Exception as e:
                logger.warning("Failed to load source mappings", source=source_name, error=str(e))
        
        return rules
    
    async def _ensure_roster_connection(self) -> bool:
        """Ensure we have an active roster DB connection."""
        if self._roster_connected:
            return True

        try:
            await self.roster_db.connect()
            self._roster_connected = True
            return True
        except Exception as e:
            logger.warning("Failed to connect to roster DB", error=str(e))
            return False

    async def _enrich_matchup(self, envelope: SourceEnvelope) -> Optional[SourceEnvelope]:
        """Enrich missing team names using matchup data from roster DB."""
        if not envelope.sport:
            return None

        if not await self._ensure_roster_connection():
            return None

        try:
            matchup = await self.roster_db.lookup_matchup(
                sport=envelope.sport,
                event_id=envelope.source_event_id,
                home_team=envelope.home_team,
                away_team=envelope.away_team,
            )

            if not matchup:
                return None

            home_team = matchup.get("home_team")
            away_team = matchup.get("away_team")

            if not home_team or not away_team:
                return None

            enriched_envelope = replace(
                envelope,
                home_team=home_team,
                away_team=away_team,
            )

            logger.info(
                "Enriched matchup teams from roster",
                source=envelope.source,
                event_id=envelope.source_event_id,
                sport=envelope.sport,
                home_team=home_team,
                away_team=away_team,
            )

            return enriched_envelope

        except Exception as e:
            logger.warning(
                "Error enriching matchup from roster",
                source=envelope.source,
                event_id=envelope.source_event_id,
                error=str(e),
            )
            return None

    async def _enrich_player_team(self, envelope: SourceEnvelope) -> Optional[SourceEnvelope]:
        """
        Enrich envelope with player team data from roster database.
        
        Attempts to determine home_team and away_team for player props
        when the source doesn't provide them.
        """
        if not await self._ensure_roster_connection():
            return None

        try:
            # Look up player's team
            roster_info = await self.roster_db.lookup_player_team(
                player_name=envelope.player_name,
                sport=envelope.sport or "basketball_nba",
                home_team=envelope.home_team,
                away_team=envelope.away_team
            )
            
            if not roster_info:
                return None
            
            player_team = roster_info.get("player_team")
            opponent_team = roster_info.get("opponent_team")
            
            if not player_team:
                return None
            
            # Create enriched envelope
            # Determine home/away based on player_team field if available
            envelope_player_team = envelope.player_team
            # Handle case where player_team is a dict (some sources like SplashSports)
            if isinstance(envelope_player_team, dict):
                envelope_player_team = envelope_player_team.get("name") or envelope_player_team.get("team_name") or ""
            
            if envelope_player_team and isinstance(envelope_player_team, str):
                # Source provided player_team, use it to determine home/away
                home_team = player_team if envelope_player_team.lower() in player_team.lower() else opponent_team
                away_team = opponent_team if home_team == player_team else player_team
            elif opponent_team:
                # Roster lookup found opponent, assume player is home team
                home_team = player_team
                away_team = opponent_team
            else:
                # Can't determine home/away, skip enrichment
                return None
            
            # Create new envelope with enriched data
            enriched_envelope = replace(
                envelope,
                home_team=home_team,
                away_team=away_team,
                player_team=player_team
            )
            
            return enriched_envelope
            
        except Exception as e:
            logger.warning(
                "Error enriching player team",
                player=envelope.player_name,
                source=envelope.source,
                error=str(e),
                exc_info=True
            )
            return None
    
    async def map_to_canonical(self, envelope: SourceEnvelope) -> Optional[CanonicalEnvelope]:
        """
        Map source envelope to canonical schema.
        
        Args:
            envelope: SourceEnvelope from connector
            
        Returns:
            CanonicalEnvelope or None if mapping fails
        """
        # PrizePicks-specific debug at the very start (disabled for performance)
        # if envelope.source == "prizepicks":
        #     print(f"[DEBUG] PrizePicks envelope received:")
        #     print(f"  Event ID: {envelope.source_event_id}")
        #     print(f"  Teams: {envelope.home_team} vs {envelope.away_team}")
        #     print(f"  Sport: {envelope.sport}")
        #     print(f"  Player: {envelope.player_name}")
        #     print(f"  Stat: {envelope.stat_type}")
        #     print(f"  Line: {envelope.line}")
        #     print(f"  Direction: {envelope.direction}")
        #     print(f"  Player Team: {envelope.player_team}")
        #     print(f"  Commence Time: {envelope.commence_time}")
        #     print(f"  Odds: {envelope.odds}")
        
        try:
            # First, attempt matchup-level enrichment using roster DB
            if (not envelope.home_team or not envelope.away_team) and envelope.sport:
                matchup_enriched = await self._enrich_matchup(envelope)
                if matchup_enriched:
                    envelope = matchup_enriched

            # Enrich missing team data using roster lookup for player props
            if (not envelope.home_team or not envelope.away_team) and envelope.player_name and envelope.market_type == "player_props":
                enriched = await self._enrich_player_team(envelope)
                if enriched:
                    envelope = enriched
                    logger.info(
                        "Enriched player team from roster",
                        player=envelope.player_name,
                        team=envelope.player_team,
                        source=envelope.source
                    )
            
            # Basic validation
            if not envelope.home_team or not envelope.away_team:
                if envelope.source == "dabble":
                    print(f"[DEBUG] Dabble envelope REJECTED - missing teams:")
                    print(f"  Event ID: {envelope.source_event_id}")
                    print(f"  Home team: '{envelope.home_team}'")
                    print(f"  Away team: '{envelope.away_team}'")
                    print(f"  Player: {envelope.player_name}")
                    print(f"  Stat: {envelope.stat_type}")
                # DFS books (SplashSports, Dabble, PrizePicks, Underdog) often omit explicit team names.
                # Log at debug level for these to avoid noisy warnings while still skipping
                # unusable props; keep warnings for traditional books where this is unexpected.
                if envelope.source in ("splashsports", "dabble", "prizepicks", "underdog"):
                    logger.debug("Missing team names", source=envelope.source, event_id=envelope.source_event_id)
                else:
                    logger.warning("Missing team names", source=envelope.source, event_id=envelope.source_event_id)
                return None
            
            # Get source-specific mapping rules
            source_rules = self.mapping_rules.get(envelope.source, {})
            
            # Initialize canonical_event_id at function level
            canonical_event_id = None
            
            # Normalize sport
            sport = self._normalize_sport(envelope.sport or "", source_rules)
            
            # Normalize teams
            home_team = self._normalize_team(envelope.home_team or "", sport, envelope.source)
            away_team = self._normalize_team(envelope.away_team or "", sport, envelope.source)
            
            # Normalize market
            market_key = self._normalize_market_key(envelope.market_type, envelope.market_key, source_rules)
            
            # Canonicalize stat type for all markets (needed for runner dict)
            canonical_stat = None
            if envelope.stat_type:
                try:
                    from processing.player_prop_matcher import canonicalize_stat_type
                    canonical_stat = canonicalize_stat_type(
                        envelope.stat_type, 
                        envelope.sport or "", 
                        player_name=envelope.player_name
                    )
                    logger.info(
                        "Stat canonicalization in v5 mapping",
                        source=envelope.source,
                        sport=envelope.sport,
                        raw_stat=envelope.stat_type,
                        canonical_stat=canonical_stat
                    )
                except Exception as e:
                    logger.warning(
                        "Stat canonicalization failed in v5 mapping",
                        source=envelope.source,
                        sport=envelope.sport,
                        raw_stat=envelope.stat_type,
                        error=str(e)
                    )
                    canonical_stat = envelope.stat_type  # Fallback to original
            
            # Normalize player name for downstream use (even if canonical ID fails)
            canonical_player = (envelope.player_name or "").strip()

            # For player props, generate canonical prop ID for cross-book matching
            runner_id = envelope.runner_id
            if (
                market_key == "player_props"
                and envelope.player_name
                and envelope.stat_type
                and envelope.line is not None
            ):
                # Use canonical prop matcher to generate stable ID
                try:
                    from processing.player_prop_matcher import (
                        CanonicalPlayerProp,
                        generate_canonical_prop_id,
                        canonicalize_player_name,
                        canonicalize_stat_type as matcher_canonicalize_stat_type,
                    )
                    from utils.team_names import canonicalize_team
                    from utils.canonical_id_generator import generate_canonical_event_id
                    from datetime import datetime as dt

                    # Canonicalize player and stat
                    canonical_player = canonicalize_player_name(envelope.player_name or "", envelope.sport or "")
                    if not canonical_stat:
                        canonical_stat = matcher_canonicalize_stat_type(
                            envelope.stat_type or "", 
                            envelope.sport or "", 
                            player_name=envelope.player_name
                        )

                    # Use already-normalized team names where possible
                    canonical_home = home_team or (envelope.home_team or "")
                    canonical_away = away_team or (envelope.away_team or "")

                    # Determine event start time (fallback to envelope timestamp if commence_time missing)
                    event_start = envelope.commence_time or envelope.ts
                    
                    # Initialize player_team - will be resolved via roster DB
                    player_team: Optional[str] = None
                    opponent_team: Optional[str] = None
                    
                    # 1) ALWAYS try PlayerRosterDB first (theScore rosters are authoritative)
                    # This is the canonical source - player name -> team mapping
                    roster_connected = await self._ensure_roster_connection()
                    if roster_connected:
                        try:
                            if canonical_player:
                                roster_info = await self.roster_db.lookup_player_team(
                                    player_name=canonical_player,
                                    sport=sport,
                                    home_team=canonical_home if canonical_home else None,
                                    away_team=canonical_away if canonical_away else None,
                                )
                                
                                if roster_info:
                                    raw_player_team = roster_info.get("player_team")
                                    raw_opponent_team = roster_info.get("opponent_team")
                                    
                                    # Use raw team name directly - it's already canonical from theScore
                                    if raw_player_team:
                                        player_team = raw_player_team
                                    if raw_opponent_team:
                                        opponent_team = raw_opponent_team
                                        
                                    logger.info(
                                        "Resolved player_team via PlayerRosterDB",
                                        player=canonical_player,
                                        team=player_team,
                                        opponent=opponent_team,
                                        source=envelope.source,
                                    )
                        except Exception as e:
                            logger.warning(
                                "PlayerRosterDB lookup failed in mapping",
                                player=envelope.player_name,
                                sport=sport,
                                error=str(e),
                            )
                    else:
                        logger.warning(
                            "Roster DB not connected",
                            player=canonical_player,
                            source=envelope.source,
                        )
                    
                    # 2) Fallback: Use envelope.player_team if roster lookup failed
                    if not player_team and envelope.player_team:
                        env_player_team = envelope.player_team
                        if isinstance(env_player_team, dict):
                            env_player_team = env_player_team.get("name") or env_player_team.get("team_name") or ""
                        if env_player_team and isinstance(env_player_team, str):
                            pt = canonicalize_team(env_player_team, sport)
                            if pt:
                                player_team = pt
                                logger.debug(
                                    "Using player_team from envelope (roster lookup failed)",
                                    player=canonical_player,
                                    team=player_team,
                                    source=envelope.source,
                                )

                    # Generate canonical event ID using shared utility
                    if canonical_home and canonical_away and event_start:
                        canonical_event_id = generate_canonical_event_id(
                            sport=sport,
                            home_team=canonical_home,
                            away_team=canonical_away,
                            commence_time=event_start,
                        )

                        try:
                            commence_time = dt.fromisoformat(event_start.replace("Z", "+00:00")) if event_start else dt.utcnow()
                        except Exception:
                            commence_time = dt.utcnow()

                        # 3) Extract from raw payload (source-specific fields) as a fallback
                        if not player_team:
                            raw_payload = envelope.raw_payload if isinstance(envelope.raw_payload, dict) else {}
                            potential_team = (
                                raw_payload.get("team")
                                or raw_payload.get("player_team")
                                or raw_payload.get("team_name")
                                or raw_payload.get("team_abbreviation")
                                or raw_payload.get("player_team_name")
                                or raw_payload.get("player_team_abbreviation")
                            )
                            if potential_team:
                                pt = canonicalize_team(potential_team, sport)
                                if pt:
                                    player_team = pt
                                    logger.debug(
                                        "Extracted player_team from raw payload",
                                        player=canonical_player,
                                        team=player_team,
                                        source=envelope.source,
                                        method="raw_payload_extraction",
                                    )

                        # 4) Heuristic match on team names if still unresolved
                        if not player_team and (canonical_home or canonical_away):
                            player_name_lower = canonical_player.lower()
                            home_lower = canonical_home.lower() if canonical_home else ""
                            away_lower = canonical_away.lower() if canonical_away else ""

                            if home_lower and (
                                home_lower in player_name_lower
                                or any(word in player_name_lower for word in home_lower.split() if len(word) > 3)
                            ):
                                player_team = canonical_home
                                logger.debug(
                                    "Matched player_team via heuristic (home team in name)",
                                    player=canonical_player,
                                    team=player_team,
                                    source=envelope.source,
                                )
                            elif away_lower and (
                                away_lower in player_name_lower
                                or any(word in player_name_lower for word in away_lower.split() if len(word) > 3)
                            ):
                                player_team = canonical_away
                                logger.debug(
                                    "Matched player_team via heuristic (away team in name)",
                                    player=canonical_player,
                                    team=player_team,
                                    source=envelope.source,
                                )

                        # Derive opponent team from player_team + matchup if needed
                        if player_team and canonical_home and canonical_away and not opponent_team:
                            if player_team == canonical_home:
                                opponent_team = canonical_away
                            elif player_team == canonical_away:
                                opponent_team = canonical_home

                        # If any required field missing, skip canonical ID generation
                        # For DFS books (underdog, prizepicks, etc.), opponent_team is optional
                        # since they don't always provide matchup context
                        dfs_books = {"underdog", "prizepicks", "dabble", "splashsports", "novig"}
                        require_opponent = envelope.source not in dfs_books
                        
                        has_required_fields = (
                            canonical_player 
                            and canonical_stat 
                            and player_team 
                            and canonical_event_id
                            and (opponent_team or not require_opponent)
                        )
                        
                        if has_required_fields:
                            temp_prop = CanonicalPlayerProp(
                                player_name=canonical_player,
                                team_name=player_team,
                                opponent_team_name=opponent_team or "UNKNOWN",
                                stat_type=canonical_stat,
                                line=float(envelope.line),
                                direction=(envelope.direction or "OVER").upper(),
                                commence_time=commence_time,
                                canonical_event_id=canonical_event_id,
                                source_key=envelope.source,
                                source_prop_id=envelope.source_event_id,
                            )
                            runner_id = generate_canonical_prop_id(temp_prop)
                            if runner_id and runner_id.startswith("prop_"):
                                logger.debug(
                                    "Generated canonical prop ID",
                                    prop_id=runner_id,
                                    player=canonical_player,
                                    stat=canonical_stat,
                                    line=envelope.line,
                                    direction=envelope.direction,
                                    team=player_team,
                                    opponent=opponent_team or "UNKNOWN",
                                    event_id=canonical_event_id,
                                    source=envelope.source,
                                )
                            else:
                                logger.error(
                                    "Failed to generate valid canonical prop ID",
                                    runner_id=runner_id,
                                    player=canonical_player,
                                    stat=canonical_stat,
                                    line=envelope.line,
                                    source=envelope.source,
                                )
                                runner_id = None
                        else:
                            missing_fields = []
                            if not canonical_player:
                                missing_fields.append("player_name")
                            if not canonical_stat:
                                missing_fields.append("stat_type")
                            if not player_team:
                                missing_fields.append("player_team")
                            if not opponent_team and require_opponent:
                                missing_fields.append("opponent_team")
                            if not canonical_event_id:
                                missing_fields.append("canonical_event_id")
                            logger.warning(
                                "Cannot generate canonical prop ID - missing required fields",
                                missing_fields=missing_fields,
                                player=canonical_player,
                                stat=canonical_stat,
                                source=envelope.source,
                            )
                except Exception as e:
                    logger.error(
                        "Failed to generate canonical prop ID - exception occurred",
                        error=str(e),
                        player=envelope.player_name,
                        stat=envelope.stat_type,
                        source=envelope.source,
                        exc_info=True,
                    )
                    # Don't fall back to original runner_id - it won't match across sources
                    runner_id = None
            
            # Build market entry
            # Use canonicalized stat type if available, otherwise use original
            runner_stat_type = canonical_stat if canonical_stat else envelope.stat_type
            runner = {
                "id": runner_id,
                "odds": envelope.odds,
                "line": envelope.line,
                "player_name": envelope.player_name,
                "stat_type": runner_stat_type,  # Use canonicalized stat type
                "direction": envelope.direction,  # "over" or "under"
                "source": envelope.source,  # Add source to runner for merge service
            }
            
            # For player props, skip if we don't have a canonical ID (can't match without it)
            if market_key == "player_props" and (not runner_id or not str(runner_id).startswith("prop_")):
                if envelope.source == "prizepicks":
                    print(f"[DEBUG] PrizePicks runner filtered out - no canonical ID: {runner_id}")
                    print(f"  Player: {envelope.player_name}, Stat: {envelope.stat_type}")
                    print(f"  Home: {envelope.home_team}, Away: {envelope.away_team}")
                    print(f"  Player Team: {envelope.player_team}, Commence: {envelope.commence_time}")
                logger.warning("Skipping player prop without canonical ID",
                             player=envelope.player_name,
                             stat=envelope.stat_type,
                             source=envelope.source)
                return None

            market = {
                "key": market_key,
                "runners": [runner],
                "source": envelope.source,
                "source_event_id": envelope.source_event_id,
            }
            
            # Build provenance
            provenance = {
                "source": envelope.source,
                "source_event_id": envelope.source_event_id,
                "timestamp": envelope.ts,
                "raw_payload_hash": self._hash_payload(envelope.raw_payload),
            }
            
            return CanonicalEnvelope(
                sport=sport,
                start_ts=envelope.commence_time or envelope.ts,
                markets=[market],
                provenance=provenance,
                home_team=home_team,
                away_team=away_team,
                source=envelope.source,
                source_event_id=envelope.source_event_id,
                canonical_event_id=canonical_event_id,  # Add the generated canonical event ID
            )
            
        except Exception as e:
            logger.warning("Mapping failed", source=envelope.source, error=str(e))
            return None
    
    def _normalize_sport(self, sport: str, source_rules: Dict[str, Any]) -> str:
        """Normalize sport key to canonical form."""
        # Default sport mappings
        sport_map = {
            "basketball_nba": "basketball_nba",
            "nba": "basketball_nba",
            "americanfootball_nfl": "americanfootball_nfl",
            "nfl": "americanfootball_nfl",
            "baseball_mlb": "baseball_mlb",
            "mlb": "baseball_mlb",
            "icehockey_nhl": "icehockey_nhl",
            "nhl": "icehockey_nhl",
            "golf": "golf",
            "golf_pga": "golf",
            "golf_lpga": "golf",
            "pga": "golf",
        }
        
        # Check source-specific rules
        source_sport_map = source_rules.get("sport_mappings", {})
        sport_map.update(source_sport_map)
        
        normalized = sport.lower().strip()
        return sport_map.get(normalized, normalized)
    
    def _normalize_team(self, team_name: str, sport: str, source: str = "") -> str:
        """Normalize team name using existing team name utilities."""
        from utils.team_names import canonicalize_team
        
        if not team_name:
            return team_name
        
        return canonicalize_team(team_name, sport)
    
    def _normalize_market_key(self, market_type: str, market_key: str, source_rules: Dict[str, Any]) -> str:
        """Normalize market key to canonical form."""
        # Default market mappings
        market_map = {
            "h2h": "h2h",
            "moneyline": "h2h",
            "money": "h2h",
            "spreads": "spreads",
            "spread": "spreads",
            "totals": "totals",
            "total": "totals",
            "over_under": "totals",
            "team_total": "team_totals",
            "team_totals": "team_totals",
            "player_props": "player_props",
            "player_points": "player_props",
            "player_rebounds": "player_props",
            "player_assists": "player_props",
            # NHL player prop market types
            "player_goals": "player_props",
            "points": "player_props",  # NHL points = goals + assists
            "shots_on_goal": "player_props",
            "assists": "player_props",
            "saves": "player_props",
            "power_play_points": "player_props",
            # NFL player prop market types
            "passing": "player_props",
            "rushing": "player_props",
            "receiving": "player_props",
            "touchdowns": "player_props",
            "receptions": "player_props",
            "passing_yards": "player_props",
            "rushing_yards": "player_props",
            "receiving_yards": "player_props",
            "rushing_attempts": "player_props",
            "longest": "player_props",  # Longest reception/rush
            "interceptions": "player_props",
            "field": "player_props",  # Field goals
            "kicking": "player_props",
        }
        
        # Check source-specific rules
        source_market_map = source_rules.get("market_mappings", {})
        market_map.update(source_market_map)
        
        # Try market_type first, then market_key
        normalized = market_type.lower().strip()
        
        # Check if it's a player prop market (any market with "player" in it or specific sport types)
        player_prop_types = [
            "player_goals", "points", "shots_on_goal", "assists", "saves", "power_play_points",  # NHL
            "passing", "rushing", "receiving", "touchdowns", "receptions", "passing_yards", 
            "rushing_yards", "receiving_yards", "rushing_attempts", "longest", "interceptions", 
            "field", "kicking"  # NFL
        ]
        if "player" in normalized or normalized in player_prop_types:
            return "player_props"
        
        if normalized not in market_map:
            normalized = market_key.lower().strip().split("_")[0]  # Take first part
        
        return market_map.get(normalized, normalized)
    
    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        """Create hash of raw payload for provenance tracking."""
        import hashlib
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()[:16]

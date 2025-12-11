"""
Player Prop Canonicalization and Matching Logic

This module provides functions to canonicalize and match player props from various sportsbooks,
enabling unique identification of player props across different sources.
"""

from typing import Optional, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import hashlib
import structlog

from data.player_aliases import get_player_aliases
from processing.stat_canonicalizer import canonicalize_stat_type as yaml_canonicalize_stat_type

logger = structlog.get_logger()


class CanonicalPlayerProp(BaseModel):
    """
    Canonical representation of a player prop in a standardized, sport-agnostic format.
    
    This model represents a player prop after canonicalization, ready for cross-book matching.
    """
    player_name: str = Field(..., description="Canonical player name (e.g., 'LeBron James')")
    team_name: str = Field(..., description="Canonical form of the player's team")
    opponent_team_name: str = Field(..., description="Canonical form of the opposing team")
    stat_type: str = Field(..., description="Canonical stat type (e.g., 'POINTS', 'REBOUNDS', 'PASSING_YARDS')")
    line: float = Field(..., description="The over/under number (e.g., 25.5)")
    direction: Literal["OVER", "UNDER"] = Field(..., description="Direction: OVER or UNDER")
    commence_time: datetime = Field(..., description="Event start time")
    canonical_event_id: str = Field(..., description="ID of the game this prop belongs to")
    source_key: str = Field(..., description="Source identifier (e.g., 'novig', 'pinnacle', 'dabble')")
    source_prop_id: Optional[str] = Field(None, description="Unique ID from the original book")
    raw_prop_data: Dict[str, Any] = Field(default_factory=dict, description="Original source-specific details for provenance")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


def canonicalize_player_name(raw_name: str, sport: str = "") -> str:
    """
    Canonicalize a player's name from various formats to a consistent canonical form.
    
    Args:
        raw_name: Player name as provided by source (e.g., "L. James", "LeBron James", "LEBRON")
        sport: Optional sport identifier for sport-specific handling
        
    Returns:
        Canonical player name (e.g., "LeBron James")
        
    Examples:
        >>> canonicalize_player_name("L. James")
        'LeBron James'
        >>> canonicalize_player_name("lebron")
        'LeBron James'
        >>> canonicalize_player_name("Unknown Player")
        'Unknown Player'
    """
    if not raw_name or not isinstance(raw_name, str):
        return raw_name or ""
    
    # Normalize input: strip whitespace
    normalized = raw_name.strip()
    if not normalized:
        return ""
    
    # Normalize common variations: remove periods from initials, normalize spaces
    # "P.J. Washington" -> "PJ Washington", "P. J. Washington" -> "PJ Washington"
    import re
    # Remove all periods (handles "P.J.", "P. J.", etc.)
    normalized_clean = normalized.replace('.', '')
    # Normalize multiple spaces to single space
    normalized_clean = re.sub(r'\s+', ' ', normalized_clean).strip()
    # Combine single-letter initials at the start (e.g., "P J Washington" -> "PJ Washington")
    # Match pattern: start of string, single letter, space, single letter, space, then rest
    normalized_clean = re.sub(r'^([A-Z])\s+([A-Z])\s+', r'\1\2 ', normalized_clean)
    
    # Check exact alias match first (case-insensitive)
    aliases = get_player_aliases()
    normalized_lower = normalized.lower()
    normalized_clean_lower = normalized_clean.lower()
    
    # Try original first
    if normalized_lower in aliases:
        canonical = aliases[normalized_lower]
        logger.debug("Player name matched via alias", raw=raw_name, canonical=canonical)
        return canonical
    
    # Try cleaned version
    if normalized_clean_lower != normalized_lower and normalized_clean_lower in aliases:
        canonical = aliases[normalized_clean_lower]
        logger.debug("Player name matched via alias (cleaned)", raw=raw_name, canonical=canonical)
        return canonical
    
    # Try fuzzy matching as fallback (use cleaned version)
    try:
        from fuzzywuzzy import fuzz, process  # type: ignore
        
        # Get all canonical names
        canonical_names = list(set(aliases.values()))
        
        # Try with cleaned version first
        best_match = process.extractOne(
            normalized_clean,
            canonical_names,
            scorer=fuzz.ratio,
            score_cutoff=80
        )
        
        if not best_match:
            # Fallback to original
            best_match = process.extractOne(
                normalized,
                canonical_names,
                scorer=fuzz.ratio,
                score_cutoff=80
            )
        
        if best_match:
            canonical = best_match[0]
            score = best_match[1]
            logger.debug("Player name matched via fuzzy matching", 
                        raw=raw_name, canonical=canonical, score=score)
            return canonical
        
    except ImportError:
        logger.warning("fuzzywuzzy not available, skipping fuzzy matching", raw_name=raw_name)
    except Exception as e:
        logger.debug("Fuzzy matching failed", raw_name=raw_name, error=str(e))
    
    # Fallback: Use cleaned version, title case if needed
    # This handles cases like "LEBRON JAMES" -> "Lebron James", "P.J. WASHINGTON" -> "PJ Washington"
    if normalized_clean.isupper() or normalized_clean.islower():
        canonical = normalized_clean.title()
        logger.debug("Player name normalized to title case", raw=raw_name, canonical=canonical)
        return canonical
    
    # Return cleaned version if already in reasonable format
    return normalized_clean


def canonicalize_stat_type(raw_stat: str, sport: str = "", player_name: Optional[str] = None) -> str:
    """
    Canonicalize a stat type from various formats to a consistent canonical form.
    
    Args:
        raw_stat: Stat name as provided by source (e.g., "Pts", "Points", "Points Scored")
        sport: Optional sport identifier for sport-specific handling
        player_name: Optional player name to strip from stat string if present
        
    Returns:
        Canonical stat type (e.g., "POINTS", "REBOUNDS", "PASSING_YARDS")
        
    Examples:
        >>> canonicalize_stat_type("Pts")
        'POINTS'
        >>> canonicalize_stat_type("Points")
        'POINTS'
        >>> canonicalize_stat_type("Passing Yards")
        'PASSING_YARDS'
    """
    # Preserve existing non-string handling semantics
    if not raw_stat or not isinstance(raw_stat, str):
        return raw_stat or ""

    # Delegate to YAML-driven canonicalizer for actual logic
    return yaml_canonicalize_stat_type(raw_stat, sport, player_name=player_name)


def normalize_line_for_matching(line: float, stat_type: str, tolerance: float = 0.5) -> float:
    """
    Normalize line for matching with configurable tolerance.
    
    This function ensures that lines within tolerance match each other.
    For example, 18.5 and 19.0 should match (both require 19+ to win).
    
    Args:
        line: The line value to normalize
        stat_type: The stat type (to determine if combo prop)
        tolerance: Tolerance for matching (default 0.5 for single stats, 1.0+ for combos)
        
    Returns:
        Normalized line value for matching
        
    Examples:
        >>> normalize_line_for_matching(18.5, "POINTS")
        19.0
        >>> normalize_line_for_matching(19.0, "POINTS")
        19.0
        >>> normalize_line_for_matching(38.5, "POINTS_REBOUNDS_ASSISTS")
        38.0
    """
    import math
    
    # Check if this is a combo stat (contains multiple stat types separated by underscores)
    is_combo_stat = "_" in stat_type and stat_type.count("_") >= 1
    
    if is_combo_stat:
        # For combo props, use wider tolerance (round to nearest 2)
        # This matches lines like 37.5 and 38.5 (both normalize to 38.0)
        # Strategy: Round to nearest 2, handling .5 values by rounding up
        # 38.5 -> 38, 37.5 -> 38, 37.0 -> 38, 26.0 -> 26, 26.5 -> 26
        # For combo props, we want 37.0-38.5 to all match (round to 38)
        # So we round to nearest 2, but if it's exactly on .5, round up
        if line % 1 == 0.5:
            # 37.5 -> 38, 38.5 -> 40 (round up to next even)
            line_rounded = math.ceil(line / 2) * 2
        else:
            # 37.0 -> 38, 38.0 -> 38, 26.0 -> 26
            line_rounded = round(line / 2) * 2
    else:
        # For single stats, normalize to nearest 0.5, then round up
        # This ensures 18.5 and 19.0 both normalize to 19.0
        # Strategy: Round to nearest 0.5, then round up to next whole number
        # 18.5 -> 19.0, 19.0 -> 19.0, 18.25 -> 18.5 -> 19.0, 18.75 -> 19.0 -> 19.0
        line_rounded_to_half = round(line * 2) / 2  # Round to nearest 0.5
        # If it's exactly on a .5, round up; otherwise round normally
        if line_rounded_to_half % 1 == 0.5:
            line_rounded = math.ceil(line_rounded_to_half)  # 18.5 -> 19, 19.5 -> 20
        else:
            line_rounded = round(line_rounded_to_half)  # 19.0 -> 19, 18.0 -> 18
    
    return float(line_rounded)


def generate_canonical_prop_id(prop: CanonicalPlayerProp) -> str:
    """
    Generate a stable, unique hash ID for a player prop.
    
    This ID is used for cross-book matching - the same prop from different sources
    should generate the same ID.
    
    The ID is based on:
    - canonical_event_id (the game)
    - player_name (canonical)
    - stat_type (canonical)
    - line (normalized for matching tolerance)
    - direction (OVER/UNDER)
    
    Source-specific fields (source_key, source_prop_id) are NOT included,
    as the purpose is to link the same prop across different sources.
    
    Args:
        prop: CanonicalPlayerProp object
        
    Returns:
        Stable hash ID string (e.g., "prop_abc123def456...")
        
    Examples:
        >>> prop1 = CanonicalPlayerProp(
        ...     player_name="LeBron James",
        ...     stat_type="POINTS",
        ...     line=25.5,
        ...     direction="OVER",
        ...     canonical_event_id="evt_123",
        ...     team_name="Lakers",
        ...     opponent_team_name="Warriors",
        ...     commence_time=datetime.now(),
        ...     source_key="novig"
        ... )
        >>> prop2 = CanonicalPlayerProp(
        ...     player_name="LeBron James",  # Same player
        ...     stat_type="POINTS",  # Same stat
        ...     line=25.5,  # Same line
        ...     direction="OVER",  # Same direction
        ...     canonical_event_id="evt_123",  # Same game
        ...     team_name="Lakers",
        ...     opponent_team_name="Warriors",
        ...     commence_time=datetime.now(),
        ...     source_key="pinnacle"  # Different source
        ... )
        >>> generate_canonical_prop_id(prop1) == generate_canonical_prop_id(prop2)
        True
    """
    # Use enhanced line normalization for better matching
    line_normalized = normalize_line_for_matching(prop.line, prop.stat_type)
    
    # Build a deterministic string from the key fields
    # Order matters for consistency
    key_fields = [
        prop.canonical_event_id,
        prop.player_name.lower().strip(),
        prop.stat_type.upper().strip(),
        str(line_normalized),
        prop.direction.upper().strip(),
    ]
    
    # Join with a delimiter and create hash
    key_string = "|".join(key_fields)
    hash_obj = hashlib.sha256(key_string.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars for readability
    
    canonical_id = f"prop_{hash_hex}"
    
    logger.debug("Generated canonical prop ID", 
                prop_id=canonical_id,
                event_id=prop.canonical_event_id,
                player=prop.player_name,
                stat=prop.stat_type,
                line_original=prop.line,
                line_normalized=line_normalized,
                direction=prop.direction)
    
    return canonical_id


def create_canonical_prop_from_envelope(
    envelope: Any,
    canonical_event_id: str,
    team_name: str,
    opponent_team_name: str,
    commence_time: datetime
) -> Optional[CanonicalPlayerProp]:
    """
    Create a CanonicalPlayerProp from a SourceEnvelope (from v5 connector adapter).
    
    This is a convenience function to convert v5 envelope format to canonical prop format.
    
    Args:
        envelope: SourceEnvelope object from v5 connector adapter
        canonical_event_id: The canonical event ID for the game
        team_name: Canonical team name (player's team)
        opponent_team_name: Canonical opponent team name
        commence_time: Event start time
        
    Returns:
        CanonicalPlayerProp if envelope is a player prop, None otherwise
    """
    # Only process player props
    if envelope.market_type != "player_props":
        return None
    
    # Extract and canonicalize player name
    raw_player_name = envelope.player_name or ""
    if not raw_player_name:
        logger.warning("Envelope missing player_name", source=envelope.source, event_id=envelope.source_event_id)
        return None
    
    canonical_player = canonicalize_player_name(raw_player_name, envelope.sport or "")
    
    # Extract and canonicalize stat type
    raw_stat_type = envelope.stat_type or ""
    if not raw_stat_type:
        logger.warning("Envelope missing stat_type", source=envelope.source, event_id=envelope.source_event_id)
        return None
    
    canonical_stat = canonicalize_stat_type(raw_stat_type, envelope.sport or "")
    
    # Extract line
    line = envelope.line
    if line is None:
        logger.warning("Envelope missing line", source=envelope.source, event_id=envelope.source_event_id)
        return None
    
    # Extract direction
    direction_raw = envelope.direction or ""
    if not direction_raw:
        logger.warning("Envelope missing direction", source=envelope.source, event_id=envelope.source_event_id)
        return None
    
    direction = direction_raw.upper()
    if direction not in ("OVER", "UNDER"):
        logger.warning("Invalid direction", direction=direction_raw, source=envelope.source)
        return None
    
    # Build canonical prop
    prop = CanonicalPlayerProp(
        player_name=canonical_player,
        team_name=team_name,
        opponent_team_name=opponent_team_name,
        stat_type=canonical_stat,
        line=float(line),
        direction=direction,  # type: ignore
        commence_time=commence_time,
        canonical_event_id=canonical_event_id,
        source_key=envelope.source,
        source_prop_id=str(envelope.source_event_id) if envelope.source_event_id else None,
        raw_prop_data=envelope.raw_payload if hasattr(envelope, 'raw_payload') else {}
    )
    
    return prop


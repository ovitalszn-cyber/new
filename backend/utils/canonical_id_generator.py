"""
Canonical ID Generator - Shared utility for generating consistent canonical IDs.

This module provides a single source of truth for generating canonical event IDs
across the entire v5 system, ensuring consistency between entity resolution and
prop matching.
"""

from typing import Optional
from datetime import datetime, timezone
import hashlib
import re
import structlog

logger = structlog.get_logger()


def _normalize_team_for_matching(team_name: str) -> str:
    """
    Normalize team name for consistent matching.
    
    Removes special characters, lowercases, and strips whitespace.
    This ensures team name variations can be matched consistently.
    
    Args:
        team_name: Raw team name
        
    Returns:
        Normalized team name for matching
    """
    if not team_name:
        return ""
    # Remove special characters, lowercase, strip
    normalized = re.sub(r'[^a-z0-9\s]', '', team_name.lower().strip())
    # Remove extra spaces
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def generate_canonical_event_id(
    sport: str,
    home_team: str,
    away_team: str,
    commence_time: str
) -> str:
    """
    Generate a deterministic canonical event ID.
    
    This is the single source of truth for canonical event IDs across the system.
    All components (entity_resolver, mapping_worker, etc.) should use this function
    to ensure consistency.
    
    The ID is based on:
    - Sport key
    - Team names (sorted alphabetically for order independence)
    - Date from commence_time (normalized to YYYYMMDD format)
    
    Args:
        sport: Sport key (e.g., "basketball_nba")
        home_team: Home team name (e.g., "Team A")
        away_team: Away team name (e.g., "Team B")
        commence_time: ISO timestamp string (e.g., "2024-01-15T20:00:00Z")
        
    Returns:
        Canonical event ID in format: "evt_{16_char_hex_hash}"
        Example: "evt_abc123def4567890"
        
    Examples:
        >>> generate_canonical_event_id(
        ...     "basketball_nba",
        ...     "Team A",
        ...     "Team B",
        ...     "2024-01-15T20:00:00Z"
        ... )
        'evt_abc123def4567890'
        
        # Order-independent (same result regardless of home/away order)
        >>> id1 = generate_canonical_event_id("nba", "Team A", "Team B", "2024-01-15T20:00:00Z")
        >>> id2 = generate_canonical_event_id("nba", "Team B", "Team A", "2024-01-15T20:00:00Z")
        >>> id1 == id2
        True
    """
    # Normalize teams for consistent matching
    home_normalized = _normalize_team_for_matching(home_team)
    away_normalized = _normalize_team_for_matching(away_team)
    
    if not home_normalized or not away_normalized:
        logger.warning("Missing team names for canonical event ID", 
                     home=home_team, away=away_team)
        # Fallback: use raw team names if normalization fails
        home_normalized = home_team.lower().strip() if home_team else "unknown"
        away_normalized = away_team.lower().strip() if away_team else "unknown"
    
    # Sort teams alphabetically for order independence
    # This ensures the same ID is generated regardless of which team is home/away
    teams_sorted = sorted([home_normalized, away_normalized])
    
    # Extract and normalize date from commence_time
    # Normalize to UTC and use the date (handles timezone differences)
    try:
        # Handle both 'Z' and '+00:00' formats
        time_str = commence_time.replace('Z', '+00:00')
        dt = datetime.fromisoformat(time_str)
        # Convert to UTC if timezone-aware
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        date_str = dt.strftime('%Y%m%d')
    except (ValueError, AttributeError, TypeError) as e:
        # Silently handle invalid date formats by using current date
        logger.debug("Invalid commence_time format, using current date", 
                    commence_time=commence_time, error=str(e))
        # Use current date as fallback for invalid formats
        date_str = datetime.utcnow().strftime('%Y%m%d')
    
    # Normalize sport key
    sport_normalized = sport.lower().strip() if sport else "unknown"
    
    # Create deterministic ID string
    # Format: "{sport}:{team1}_vs_{team2}:{date}"
    id_string = f"{sport_normalized}:{teams_sorted[0]}_vs_{teams_sorted[1]}:{date_str}"
    
    # Generate hash-based ID
    hash_obj = hashlib.sha256(id_string.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()[:16]  # Use first 16 chars for readability
    
    canonical_id = f"evt_{hash_hex}"
    
    logger.debug("Generated canonical event ID",
                canonical_id=canonical_id,
                sport=sport_normalized,
                teams=teams_sorted,
                date=date_str)
    
    return canonical_id


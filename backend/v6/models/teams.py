"""
Team-related models for theScore API responses.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from .common import BaseModelWithTimestamps, Sport, League, Location


class TeamStats(BaseModel):
    """Team statistics - flexible for different API responses."""
    games_played: int = 0
    
    # Football stats
    points_for: int = 0
    points_against: int = 0
    yards_total: Optional[int] = None
    pass_yards: Optional[int] = None
    rush_yards: Optional[int] = None
    turnovers: Optional[int] = None
    
    # Additional fields from theScore API
    points_for_conference: Optional[int] = None
    points_against_conference: Optional[int] = None
    
    class Config:
        extra = "allow"


class Team(BaseModelWithTimestamps):
    """Complete team information - flexible for theScore API format."""
    id: int
    name: str
    abbreviation: str
    
    # Multiple name fields from theScore API
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    medium_name: Optional[str] = None
    short_name: Optional[str] = None
    search_name: Optional[str] = None
    
    # Sport/League info - optional since not in all responses
    sport: Optional[Union[str, Sport]] = None
    league: Optional[Union[str, League]] = None
    
    # Location - handle both string and dict formats
    location: Optional[Union[str, Location]] = None
    
    # Conference/Division
    conference: Optional[str] = None
    division: Optional[str] = None
    
    # Performance - keep as flexible dicts for normalization
    record: Optional[Dict[str, Any]] = None
    standing: Optional[Dict[str, Any]] = None
    stats: Optional[TeamStats] = None
    
    # Visuals - theScore API specific
    logo_url: Optional[str] = None
    logos: Optional[Dict[str, Optional[str]]] = None  # Allow None values in logos dict
    colour_1: Optional[str] = None
    colour_2: Optional[str] = None
    
    # API metadata
    api_url: Optional[str] = None
    api_uri: Optional[str] = None
    resource_uri: Optional[str] = None
    
    # Flags from theScore API
    has_injuries: Optional[bool] = None
    has_rosters: Optional[bool] = None
    has_extra_info: Optional[bool] = None
    
    # Subscription info
    subscription_count: Optional[int] = None
    
    class Config:
        extra = "allow"  # Allow extra fields for flexible normalization
    
    @property
    def primary_name(self) -> str:
        """Get the primary team name for display."""
        return self.medium_name or self.full_name or self.name
    
    @property
    def primary_logo_url(self) -> Optional[str]:
        """Get the primary logo URL from available options."""
        if self.logos and isinstance(self.logos, dict):
            return self.logos.get('large') or self.logos.get('small') or self.logos.get('tiny')
        return self.logo_url


class Standing(BaseModel):
    """League standing information - matches actual theScore API structure."""
    rank: int = 0
    id: int  # This is the standing ID, not team ID
    team: Dict[str, Any]  # Nested team object from theScore API
    
    # Basic record fields
    wins: int = 0
    losses: int = 0
    ties: Optional[Union[int, None]] = 0  # Handle both int and None (NHL)
    
    # Points
    points_for: int = 0
    points_against: int = 0
    points_for_conference: Optional[int] = None
    points_against_conference: Optional[int] = None
    
    # Ranking info
    place: Optional[int] = None
    division_rank: Optional[int] = None
    conference_rank: Optional[int] = None
    playoff_seed: Optional[int] = None
    conference_seed: Optional[int] = None
    
    # Streak and percentage - handle both string and float formats
    streak: Optional[str] = None
    winning_percentage: Optional[Union[str, float]] = None
    
    # Record fields from theScore API
    short_record: Optional[str] = None
    last_five_games_record: Optional[str] = None
    
    # Conference/Division
    conference: Optional[str] = None
    division: Optional[str] = None
    
    # Playoff status
    clinched_division: bool = False
    clinched_playoffs: bool = False
    eliminated_from_playoffs: Optional[bool] = None  # Handle None for MLB
    
    # theScore specific fields
    formatted_rank: Optional[str] = None
    division_ranking: Optional[int] = None
    
    # Season info
    season: Optional[Dict[str, Any]] = None
    season_type: Optional[str] = None
    
    class Config:
        extra = "allow"
    
    @property
    def team_id(self) -> int:
        """Extract team ID from nested team object."""
        return self.team.get("id") if self.team else None
    
    @property
    def team_name(self) -> str:
        """Get team name from nested team object."""
        if self.team:
            return self.team.get("medium_name") or self.team.get("full_name") or self.team.get("name", "")
        return ""


class LeagueStandings(BaseModelWithTimestamps):
    """Complete league standings - flexible structure."""
    league: Union[str, League]
    season: Optional[Dict[str, Any]] = None
    updated_at: str  # Keep as string for RFC 2822 format
    divisions: Dict[str, List[Standing]] = Field(default_factory=dict)
    conferences: Dict[str, List[Standing]] = Field(default_factory=dict)
    overall: List[Standing] = Field(default_factory=list)
    
    class Config:
        extra = "allow"

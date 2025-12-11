"""
Game-related models for theScore API responses.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from .common import BaseModelWithTimestamps, Sport, League, Location


class GameScore(BaseModel):
    """Game score information - flexible for different API responses."""
    current_score: Dict[str, int] = Field(default_factory=dict)
    final_score: Optional[Dict[str, int]] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    period_scores: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class GameEvent(BaseModel):
    """Individual game event/play."""
    id: int
    type: str
    description: str
    timestamp: str  # Keep as string for RFC 2822 format
    player_id: Optional[int] = None
    team_id: Optional[int] = None
    score_value: Optional[int] = None
    
    class Config:
        extra = "allow"


class Game(BaseModelWithTimestamps):
    """Complete game information - matches actual theScore API structure."""
    id: int
    sport: Optional[Union[str, Sport]] = None
    league: Optional[Dict[str, Any]] = None  # API returns dict, not enum
    
    # Timing - use actual API field names
    game_date: str  # RFC 2822 format from API
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str  # "scheduled", "in_progress", "final", "postponed"
    event_status: Optional[str] = None
    
    # Teams - nested objects from API
    home_team: Dict[str, Any]  # Full team object from API
    away_team: Dict[str, Any]  # Full team object from API
    
    # Game information
    game_type: Optional[str] = None
    game_description: Optional[str] = None
    location: Optional[str] = None
    stadium: Optional[str] = None
    
    # Box score and scoring
    box_score: Optional[Dict[str, Any]] = None
    score: Optional[Dict[str, Any]] = None  # Final scores here
    
    # Betting information
    odd: Optional[Dict[str, Any]] = None
    
    # Properties for convenience - extract from nested objects
    @property
    def scheduled_at(self) -> str:
        """Alias for game_date to maintain compatibility."""
        return self.game_date
    
    @property
    def home_team_id(self) -> int:
        """Extract home team ID from nested object."""
        return self.home_team.get('id') if self.home_team else None
    
    @property
    def away_team_id(self) -> int:
        """Extract away team ID from nested object."""
        return self.away_team.get('id') if self.away_team else None
    
    @property
    def home_team_name(self) -> str:
        """Extract home team name from nested object."""
        if self.home_team:
            return self.home_team.get('medium_name') or self.home_team.get('full_name', '')
        return ''
    
    @property
    def away_team_name(self) -> str:
        """Extract away team name from nested object."""
        if self.away_team:
            return self.away_team.get('medium_name') or self.away_team.get('full_name', '')
        return ''
    
    @property
    def final_score(self) -> Optional[Dict[str, int]]:
        """Extract final score from box_score.score object."""
        if self.box_score and 'score' in self.box_score:
            score_data = self.box_score['score']
            return {
                'home': score_data.get('home', {}).get('score', 0),
                'away': score_data.get('away', {}).get('score', 0)
            }
        return None
    
    @property
    def display_status(self) -> str:
        """Get human-readable status."""
        if self.status == 'final':
            return 'Final'
        elif self.status == 'in_progress':
            if self.box_score and 'progress' in self.box_score:
                return self.box_score['progress'].get('clock_label', 'In Progress')
            return 'In Progress'
        elif self.status == 'scheduled':
            return 'Scheduled'
        return self.status.title()
    
    @property
    def formatted_time(self) -> str:
        """Convert RFC 2822 game_date to human-readable 12-hour format."""
        try:
            from datetime import datetime
            import re
            
            # Parse RFC 2822 format: "Sat, 23 Aug 2025 16:00:00 -0000"
            if self.game_date:
                # Extract the datetime part (ignore timezone for now)
                dt_match = re.search(r'(\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2})', self.game_date)
                if dt_match:
                    dt_str = dt_match.group(1)
                    dt = datetime.strptime(dt_str, '%a, %d %b %Y %H:%M:%S')
                    return dt.strftime('%I:%M %p').lstrip('0')  # Remove leading zero
            return self.game_date or ''
        except Exception:
            return self.game_date or ''
    
    @property
    def formatted_date_time(self) -> str:
        """Convert RFC 2822 game_date to full human-readable format."""
        try:
            from datetime import datetime
            import re
            
            # Parse RFC 2822 format: "Sat, 23 Aug 2025 16:00:00 -0000"
            if self.game_date:
                # Extract the datetime part
                dt_match = re.search(r'(\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2})', self.game_date)
                if dt_match:
                    dt_str = dt_match.group(1)
                    dt = datetime.strptime(dt_str, '%a, %d %b %Y %H:%M:%S')
                    return dt.strftime('%A, %B %d, %Y at %I:%M %p').lstrip('0').replace(' 0', ' ')
            return self.game_date or ''
        except Exception:
            return self.game_date or ''
    
    class Config:
        extra = "allow"  # Allow extra fields from API


class GameSchedule(BaseModel):
    """Game schedule response."""
    games: List[Game]
    total_count: int
    page: Optional[int] = None
    per_page: int = 50
    
    class Config:
        extra = "allow"

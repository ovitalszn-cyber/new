"""
Common models and enums used across theScore API responses.
"""

from enum import Enum
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel


class Sport(str, Enum):
    """Supported sports."""
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    BASEBALL = "baseball"
    HOCKEY = "hockey"
    SOCCER = "soccer"


class League(str, Enum):
    """Supported leagues."""
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    NCAA_FOOTBALL = "ncaaf"
    NCAA_BASKETBALL = "ncaa"


class BaseModelWithTimestamps(BaseModel):
    """Base model with common timestamp fields - keeps RFC 2822 format."""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Location(BaseModel):
    """Location information for games/teams."""
    city: str
    state: Optional[str] = None
    country: str = "US"
    
    @classmethod
    def from_string(cls, location_str: str) -> "Location":
        """Create Location from string (fallback for theScore API)."""
        return cls(city=location_str, country="US")


class Record(BaseModel):
    """Team win-loss record."""
    wins: int
    losses: int
    ties: int = 0
    winning_percentage: Optional[float] = None

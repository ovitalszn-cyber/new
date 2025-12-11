from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import structlog
import json

from ..historical.database import get_historical_db, HistoricalOddsDatabase

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["v6-esports"])

# Response Models
class EsportsMatchResponse(BaseModel):
    id: int
    match_id: int
    sport: str
    discipline: str
    slug: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    team1_name: Optional[str] = None
    team2_name: Optional[str] = None
    score_team1: Optional[int] = Field(None, alias="team1_score")
    score_team2: Optional[int] = Field(None, alias="team2_score")
    winner_team_id: Optional[int] = None
    bo_type: Optional[int] = None
    status: Optional[str] = None
    tournament_id: Optional[int] = None
    tier: Optional[str] = None
    raw_stats: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

@router.get("/esports/matches", response_model=List[EsportsMatchResponse])
async def get_esports_matches(
    discipline: Optional[str] = Query(None, description="Esport discipline (e.g., lol, cs2, dota2, val)"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=1000)
):
    """
    Get a list of esports matches from the historical database.
    """
    db = await get_historical_db()
    
    # Convert date to datetime if provided (assuming start of day for start_date and end of day for end_date?)
    # The DB method handles ISO string or datetime.
    
    dt_from = datetime.combine(start_date, datetime.min.time()) if start_date else None
    dt_to = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    matches = await db.fetch_esports_matches(
        discipline=discipline,
        date_from=dt_from,
        date_to=dt_to,
        limit=limit
    )
    
    # Parse raw stats if needed
    results = []
    for match in matches:
        if "raw_stats_json" in match and isinstance(match["raw_stats_json"], str):
             try:
                 match["raw_stats"] = json.loads(match["raw_stats_json"])
             except:
                 pass
        results.append(match)
        
    return results

@router.get("/esports/matches/{match_id}", response_model=EsportsMatchResponse)
async def get_esports_match_details(
    match_id: int = Path(..., description="The unique BO3 match ID")
):
    """
    Get detailed information for a specific esports match.
    """
    db = await get_historical_db()
    matches = await db.fetch_esports_matches(match_id=match_id, limit=1)
    
    if not matches:
        raise HTTPException(status_code=404, detail="Match not found")
        
    match = matches[0]
    if "raw_stats_json" in match and isinstance(match["raw_stats_json"], str):
         try:
             match["raw_stats"] = json.loads(match["raw_stats_json"])
         except:
             pass
             
    return match

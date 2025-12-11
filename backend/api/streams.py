from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
import structlog

router = APIRouter()

# Import all streamers
from streamers.splashsports import SplashSportsStreamer
from streamers.dabble import DabbleStreamer
from streamers.novig import NovigStreamer
from streamers.rebet import RebetStreamer
from streamers.bovada import BovadaStreamer
from streamers.betonline import BetOnlineStreamer
from streamers.fliff import FliffStreamer
from streamers.prizepicks import PrizePicksStreamer
from streamers.prophetx import ProphetXStreamer
from streamers.propscash import PropsCashStreamer
from streamers.underdog import UnderdogStreamer
from streamers.betr import BetrStreamer

logger = structlog.get_logger()

# ============================================================================
# BOOKS ENDPOINT
# ============================================================================

@router.get("/books")
async def get_available_books() -> Dict[str, Any]:
    """Get list of all available sportsbooks/books."""
    # Import the book mapping from odds.py to keep consistency
    from api.odds import BOOK_MAP
    
    books = []
    for book_name, streamer_class in BOOK_MAP.items():
        try:
            book_sports = streamer_class.get_supported_sports()
            books.append({
                "name": book_name,
                "status": "active",
                "sports": book_sports
            })
        except Exception as e:
            logger.warning(f"Failed to get sports for {book_name}: {e}")
            books.append({
                "name": book_name,
                "status": "error",
                "sports": []
            })
    
    return {"books": books}

# ============================================================================
# SPORTS ENDPOINTS
# ============================================================================

@router.get("/{book}/sports")
async def get_book_sports(book: str) -> Dict[str, Any]:
    """Get supported sports for a specific book."""
    from api.odds import BOOK_MAP
    
    if book not in BOOK_MAP:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
    
    streamer_class = BOOK_MAP[book]
    try:
        sports = streamer_class.get_supported_sports()
        return {
            "book": book,
            "sports": sports,
            "total_sports": len(sports)
        }
    except Exception as e:
        logger.error(f"Failed to get sports for {book}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sports for {book}")

@router.get("/{book}/{sport}/fetch")
async def fetch_book_sport_data(book: str, sport: str) -> Dict[str, Any]:
    """Fetch data for a specific book and sport."""
    from api.odds import BOOK_MAP
    
    if book not in BOOK_MAP:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found")
    
    streamer_class = BOOK_MAP[book]
    try:
        config = {"sport": sport}
        streamer = streamer_class(f"{book}_{sport}", config)
        
        if hasattr(streamer, "connect"):
            await streamer.connect()
        
        data = await streamer.fetch_data()
        
        if hasattr(streamer, "disconnect"):
            await streamer.disconnect()
        
        return {
            "book": book,
            "sport": sport,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to fetch data for {book}/{sport}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data for {book}/{sport}")

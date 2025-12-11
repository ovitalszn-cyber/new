"""V6 Export API - streaming CSV/JSON exports for odds, props, and stats."""

from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from v6.api.unified import get_engines
from v6.export import ExportJob
from v6.export.service import ExportService
from v6.export.writers import CSVWriter, JSONLinesWriter
from v6.historical import get_historical_db
from v6.stats.engine import StatsEngine

router = APIRouter(prefix="/v6", tags=["v6-export"])

DEFAULT_DATASETS = [
    "live_odds",
    "live_props",
    "game_stats",
    "historical_odds",
    "historical_props",
    "historical_games",
    "historical_team_stats",
    "historical_team_stat_leaders",
    "historical_players",
    "historical_player_boxscores",
]

MEDIA_TYPES = {
    "json": "application/x-ndjson",
    "csv": "text/csv",
}


@router.get("/export")
async def export_data(
    format: str = Query("json", description="Export format: json or csv"),
    datasets: Optional[str] = Query(
        None,
        description=(
            "Comma-separated datasets: "
            "live_odds, live_props, game_stats, "
            "historical_odds, historical_props, historical_games, "
            "historical_team_stats, historical_team_stat_leaders, historical_players, "
            "historical_player_boxscores"
        ),
    ),
    scope: str = Query("all", description="Scope: live, historical, or all"),
    sport: Optional[str] = Query(None, description="Sport filter (e.g., americanfootball_nfl)"),
    books: Optional[str] = Query(None, description="Comma-separated sportsbook keys"),
    book_name: Optional[str] = Query(None, description="Exact book name for historical queries"),
    date_from: Optional[str] = Query(None, description="ISO8601 start timestamp for historical data"),
    date_to: Optional[str] = Query(None, description="ISO8601 end timestamp for historical data"),
    team_id: Optional[int] = Query(None, description="Team id filter for boxscore datasets"),
    player_id: Optional[int] = Query(None, description="Player id filter for boxscore datasets"),
    game_id: Optional[int] = Query(None, description="Game id filter for boxscore datasets"),
    limit: Optional[int] = Query(5000, description="Row limit for historical datasets"),
) -> StreamingResponse:
    """Stream export data in NDJSON or CSV format."""
    export_format = format.strip().lower()
    if export_format not in MEDIA_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported format. Use json or csv.")

    dataset_list = _parse_datasets(datasets) or DEFAULT_DATASETS
    invalid = [d for d in dataset_list if d not in DEFAULT_DATASETS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported datasets: {', '.join(invalid)}")

    odds_engine, props_engine = await get_engines()
    stats_engine = StatsEngine()
    historical_db = await get_historical_db()

    service = ExportService(
        odds_engine=odds_engine,
        props_engine=props_engine,
        stats_engine=stats_engine,
        historical_db=historical_db,
    )

    filters: Dict[str, Any] = {
        "sport": sport,
        "books": books,
        "book_name": book_name,
        "date_from": date_from,
        "date_to": date_to,
        "team_id": team_id,
        "player_id": player_id,
        "game_id": game_id,
        "limit": limit,
    }

    job = ExportJob(
        datasets=dataset_list,
        export_format=export_format,
        scope=scope,
        filters=filters,
    )

    async def row_generator() -> AsyncIterator[Dict[str, Any]]:
        try:
            async for row in service.iterate(job):
                yield row
        finally:
            await service.shutdown()

    writer = JSONLinesWriter() if export_format == "json" else CSVWriter()
    stream = writer.stream(row_generator())

    filename = _build_filename(dataset_list, export_format)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return StreamingResponse(
        stream,
        media_type=MEDIA_TYPES[export_format],
        headers=headers,
    )


def _parse_datasets(raw: Optional[str]) -> Optional[List[str]]:
    if not raw:
        return None
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


def _build_filename(datasets: List[str], export_format: str) -> str:
    dataset_part = "-".join(datasets) if datasets else "export"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    extension = "jsonl" if export_format == "json" else "csv"
    return f"{dataset_part}-{timestamp}.{extension}"

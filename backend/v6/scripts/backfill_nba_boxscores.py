import asyncio
import json
import subprocess
from datetime import date, datetime, timedelta, time
from typing import Any, Dict, List, Optional

import httpx

from v6.historical.database import get_historical_db


API_BASE = "https://api.thescore.com"


async def fetch_events_for_date(
    client: httpx.AsyncClient,
    target_date: date,
    sport: str = "nba",
) -> List[Dict[str, Any]]:
    """Fetch all NBA events for a given date using the dedicated nba/events endpoint."""
    # TheScore expects local time with offset; target the full local day
    start_iso = target_date.strftime("%Y-%m-%dT00:00:00-0500")
    end_iso = target_date.strftime("%Y-%m-%dT23:59:59-0500")

    params = {
        "game_date.in": f"{start_iso},{end_iso}",
        "rpp": "-1",
    }

    url = f"{API_BASE}/{sport}/events"
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    # Normalise to a list of event objects
    if isinstance(data, dict):
        events_raw = data.get("events") or data.get("data") or []
    elif isinstance(data, list):
        events_raw = data
    else:
        events_raw = []

    events: List[Dict[str, Any]] = []
    for ev in events_raw:
        if isinstance(ev, dict):
            events.append(ev)
            continue
        if isinstance(ev, str):
            try:
                parsed = json.loads(ev)
                if isinstance(parsed, dict):
                    events.append(parsed)
            except Exception:
                continue
    return events


async def fetch_boxscore_player_records(
    client: httpx.AsyncClient,
    game_id: int,
    sport: str = "nba",
) -> List[Dict[str, Any]]:
    """Fetch player boxscore records for a single NBA game.

    This uses the same endpoint as the boxstats curl:
    /{sport}/box_scores/{game_id}/player_records?rpp=-1
    """
    url = f"{API_BASE}/{sport}/box_scores/{game_id}/player_records"
    resp = await client.get(url, params={"rpp": "-1"})
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return data
    return []


def _parse_game_date(ev: Dict[str, Any]) -> Optional[datetime]:
    raw = ev.get("game_date") or ev.get("game_time")
    if not raw:
        return None
    try:
        # TheScore format example: "Sun, 08 Feb 2026 23:30:00 -0000"
        return datetime.strptime(str(raw), "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        try:
            return datetime.fromisoformat(str(raw))
        except Exception:
            return None


def normalize_player_record(
    record: Dict[str, Any],
    game_id: int,
    game_dt: Optional[datetime],
    season_year: Optional[int],
    season_type: Optional[str],
    sport: str = "nba",
) -> Dict[str, Any]:
    """Flatten a single TheScore player_record into the nba_player_boxscores schema."""
    player = record.get("player") or {}
    teams = player.get("teams") or []
    team = teams[0] if teams else {}

    return {
        "sport": sport,
        "game_id": game_id,
        "game_date": game_dt,
        "season_year": season_year,
        "season_type": season_type,
        "team_id": team.get("id"),
        "team_name": team.get("full_name"),
        "team_key": team.get("abbreviation"),
        "alignment": record.get("alignment"),
        "player_id": player.get("id"),
        "player_name": player.get("full_name"),
        "position": record.get("position") or player.get("position"),
        "minutes": record.get("minutes"),
        "total_seconds": record.get("total_seconds"),
        "points": record.get("points"),
        "rebounds_offensive": record.get("rebounds_offensive"),
        "rebounds_defensive": record.get("rebounds_defensive"),
        "rebounds_total": record.get("rebounds_total"),
        "assists": record.get("assists"),
        "steals": record.get("steals"),
        "blocked_shots": record.get("blocked_shots"),
        "turnovers": record.get("turnovers"),
        "personal_fouls": record.get("personal_fouls"),
        "flagrant_fouls": record.get("flagrant_fouls"),
        "technical_fouls_player": record.get("technical_fouls_player"),
        "field_goals_attempted": record.get("field_goals_attempted"),
        "field_goals_made": record.get("field_goals_made"),
        "field_goals_percentage": record.get("field_goals_percentage"),
        "three_point_field_goals_attempted": record.get("three_point_field_goals_attempted"),
        "three_point_field_goals_made": record.get("three_point_field_goals_made"),
        "three_point_field_goals_percentage": record.get("three_point_field_goals_percentage"),
        "free_throws_attempted": record.get("free_throws_attempted"),
        "free_throws_made": record.get("free_throws_made"),
        "free_throws_percentage": record.get("free_throws_percentage"),
        "plus_minus": record.get("plus_minus"),
        "started_game": record.get("started_game"),
        "games_started": record.get("games_started"),
        "on_court": record.get("on_court"),
        "fouled_out": record.get("fouled_out"),
        "ejected": record.get("ejected"),
        "raw_player_json": json.dumps(record),
    }


def _extract_boxscore_id(ev: Dict[str, Any]) -> Optional[int]:
    """Derive the box score id from an event payload."""
    box_score = ev.get("box_score")
    if not isinstance(box_score, dict):
        return None

    api_uri = box_score.get("api_uri")
    if isinstance(api_uri, str):
        parts = api_uri.strip().split("/")
        if parts:
            last = parts[-1] or (parts[-2] if len(parts) >= 2 else "")
            if str(last).isdigit():
                return int(last)

    box_id = box_score.get("id")
    if box_id is not None:
        try:
            return int(box_id)
        except (TypeError, ValueError):
            return None

    return None


async def ingest_nba_boxscores_for_date(
    client: httpx.AsyncClient,
    target_date: date,
    semaphore: asyncio.Semaphore,
    sport: str = "nba",
) -> int:
    """Ingest all NBA player boxscores for a given date using nba/events + box_scores APIs.

    Returns the number of player rows prepared (not necessarily distinct players).
    """

    events = await fetch_events_for_date(client, target_date, sport=sport)
    print(f"[{sport}_boxscores] {target_date}: fetched {len(events)} events from {sport}/events")
    if not events:
        return 0

    # 1) Build tasks to fetch boxscores for each event with a valid box_score id
    tasks = []
    for ev in events:
        boxscore_id = _extract_boxscore_id(ev)
        if not boxscore_id:
            continue

        game_dt = _parse_game_date(ev)
        season_year: Optional[int] = game_dt.year if isinstance(game_dt, datetime) else None
        season_type = ev.get("season_type") or ev.get("game_type")

        async def _fetch_for_game(
            gid: int,
            gdt: Optional[datetime],
            sy: Optional[int],
            st: Optional[str],
        ) -> List[Dict[str, Any]]:
            async with semaphore:
                records = await fetch_boxscore_player_records(client, gid, sport=sport)
            return [
                normalize_player_record(r, gid, gdt, sy, st, sport=sport)
                for r in records
            ]

        tasks.append(_fetch_for_game(boxscore_id, game_dt, season_year, season_type))

    player_rows: List[Dict[str, Any]] = []
    if tasks:
        for coro in asyncio.as_completed(tasks):
            try:
                rows = await coro
                player_rows.extend(rows)
            except Exception:
                # Skip failures for individual games; could add logging here
                continue

    if not player_rows:
        return 0

    db = await get_historical_db()

    # Bulk insert using simple executemany on the underlying engine via text() insert
    # We avoid adding a new method on the DB class for now to keep this script standalone.
    insert_sql = """
    INSERT INTO nba_player_boxscores (
        sport, game_id, game_date, season_year, season_type,
        team_id, team_name, team_key, alignment,
        player_id, player_name, position,
        minutes, total_seconds, points,
        rebounds_offensive, rebounds_defensive, rebounds_total,
        assists, steals, blocked_shots, turnovers,
        personal_fouls, flagrant_fouls, technical_fouls_player,
        field_goals_attempted, field_goals_made, field_goals_percentage,
        three_point_field_goals_attempted, three_point_field_goals_made, three_point_field_goals_percentage,
        free_throws_attempted, free_throws_made, free_throws_percentage,
        plus_minus, started_game, games_started, on_court, fouled_out, ejected,
        raw_player_json
    ) VALUES (
        :sport, :game_id, :game_date, :season_year, :season_type,
        :team_id, :team_name, :team_key, :alignment,
        :player_id, :player_name, :position,
        :minutes, :total_seconds, :points,
        :rebounds_offensive, :rebounds_defensive, :rebounds_total,
        :assists, :steals, :blocked_shots, :turnovers,
        :personal_fouls, :flagrant_fouls, :technical_fouls_player,
        :field_goals_attempted, :field_goals_made, :field_goals_percentage,
        :three_point_field_goals_attempted, :three_point_field_goals_made, :three_point_field_goals_percentage,
        :free_throws_attempted, :free_throws_made, :free_throws_percentage,
        :plus_minus, :started_game, :games_started, :on_court, :fouled_out, :ejected,
        :raw_player_json
    )
    """

    from sqlalchemy import text

    async with db.session_maker() as session:  # type: ignore[attr-defined]
        await session.execute(text(insert_sql), player_rows)
        await session.commit()

    return len(player_rows)


async def backfill_nba_boxscores(
    start_date: date,
    end_date: date,
    concurrency: int = 8,
    sport: str = "nba",
) -> None:
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=15.0) as client:
        current = start_date
        while current <= end_date:
            count = await ingest_nba_boxscores_for_date(
                client,
                current,
                semaphore,
                sport=sport,
            )
            print(
                f"{sport} {current.isoformat()}: inserted {count} player boxscore rows"
            )
            current += timedelta(days=1)


def _fetch_schedule_via_curl() -> Optional[Any]:
    """Call the nba/schedule endpoint via curl using recorded headers/cookies."""
    url = f"{API_BASE}/nba/schedule?utc_offset=-18000"
    curl_cmd = [
        "curl",
        "-H",
        "accept: application/json",
        "-H",
        "x-country-code: US",
        "-H",
        "priority: u=3, i",
        "-H",
        "accept-language: en-US;q=1",
        "-H",
        "x-api-version: 1.8.2",
        "-H",
        "cache-control: max-age=0",
        "-H",
        "user-agent: theScore/25.19.0 iOS/26.2 (iPhone; Retina, 1284x2778)",
        "-H",
        "x-app-version: 25.19.0",
        "-H",
        "x-region-code: FL",
        "-H",
        (
            "cookie: __cf_bm=yCc2QYXrJsUlTe3FIOHujWv3ElIGiUXOfVG4MPHZm2s-1765210784-1.0.1.1-"
            "Hwn5qxj4XQTFiaEmLophMjUJlMFa_Zb8cf6KirabQWYg_AWUOC0awt_ExXTeNxc.f5umOU41"
            "YzsiGFd21iyqLnTQTDAvhtbmdZyfEYbVqoo; "
            "_cfuvid=AYFYWO15yv4z8_SJXTDHd5x4jKGqfxq7YaES288LSXg-1765210784899-0.0.1.1-604800000; "
            "_ga_K2ECMCJBFQ=GS2.1.s1765035472$o1$g0$t1765035490$j42$l0$h0; "
            "_ga_SQ24F7Q7YW=GS2.1.s1765035472$o1$g0$t1765035490$j42$l0$h0; "
            "_ga=GA1.1.845315072.1765035472"
        ),
        url,
    ]
    try:
        result = subprocess.run(
            curl_cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return None

    raw = result.stdout.strip()
    # Trim non-JSON prefixes/suffixes (curl sometimes appends % or progress info)
    start_idx = raw.find("{")
    end_idx = raw.rfind("}")
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return None
    candidate = raw[start_idx : end_idx + 1]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backfill NBA player boxscores into historical DB")
    parser.add_argument("--from", dest="start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--concurrency", type=int, default=8, help="Max concurrent boxscore requests")
    parser.add_argument(
        "--sport",
        dest="sport",
        default="nba",
        choices=["nba", "nhl", "mlb"],
        help="Sport to backfill (nba, nhl, mlb)",
    )

    args = parser.parse_args()
    start = _parse_date(args.start)
    end = _parse_date(args.end)

    asyncio.run(
        backfill_nba_boxscores(
            start,
            end,
            concurrency=args.concurrency,
            sport=args.sport,
        )
    )

"""Helpers for building cached sport snapshots for odds/props endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def build_sport_snapshot(
    sport: str,
    canonical_events: List[Dict[str, Any]],
    fetched_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a sport-level snapshot (per-book games + metadata) from canonical events.

    This structure mirrors the legacy `get_all_odds` payload so the `/v6/odds`
    endpoint can respond instantly using Redis without re-fetching upstream data.
    """
    timestamp = fetched_at or datetime.now(timezone.utc).isoformat()
    books: Dict[str, Dict[str, Any]] = {}

    for event in canonical_events:
        event_id = event.get("canonical_event_id")
        if not event_id:
            continue

        base_game_payload = {
            "canonical_event_id": event_id,
            "sport": event.get("sport", sport),
            "home_team": event.get("home_team"),
            "away_team": event.get("away_team"),
            "commence_time": event.get("commence_time"),
            "markets": event.get("markets", []),
            "props": event.get("props", []),
            "generated_at": event.get("generated_at", timestamp),
            "source": "kashrock"
        }

        for book_key, book_data in event.get("books", {}).items():
            book_entry = books.setdefault(
                book_key,
                {
                    "book": {"key": book_key},
                    "sport": sport,
                    "games": [],
                    "fetched_at": timestamp,
                    "cached": True,
                },
            )

            game_payload = dict(base_game_payload)
            game_payload["odds"] = book_data.get("odds", [])
            game_payload["book_has_props"] = book_data.get("has_props", False)
            game_payload["book_has_odds"] = book_data.get("has_odds", False)
            if book_data.get("has_props"):
                game_payload["book_props"] = book_data.get("props", [])

            book_entry["games"].append(game_payload)

    for book_entry in books.values():
        book_entry["total_games"] = len(book_entry["games"])

    snapshot = {
        "sport": sport,
        "books": books,
        "event_count": len(canonical_events),
        "total_books": len(books),
        "successful_books": len([b for b in books.values() if b["total_games"] > 0]),
        "fetched_at": timestamp,
    }
    return snapshot

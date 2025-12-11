"""Stats engine scaffolding for V6 unified endpoint.

This module orchestrates ingestion and normalization of schedule, box score,
player, and team data sourced from upstream providers (initially theScore).

Responsibilities (to be implemented):
- Configure and run data ingestion workers.
- Normalize teams/players into canonical IDs reused across the platform.
- Publish finalized game snapshots into the unified cache for downstream use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class StatsIngestor(Protocol):
    """Protocol for upstream stats ingestors."""

    async def run(self) -> None:
        """Fetch new data from the upstream provider and persist results."""


@dataclass
class StatsSnapshot:
    """Canonical representation of a game after normalization."""

    game_id: str
    sport: str
    commence_time: str
    home_team: str
    away_team: str
    box_score: dict
    metadata: dict


__all__ = ["StatsIngestor", "StatsSnapshot"]

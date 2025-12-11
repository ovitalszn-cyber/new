"""Odds engine scaffolding for V6 unified endpoint.

Handles per-book ingestion, normalization, and storage of odds data. The module
will coordinate multiple bookmaker connectors, apply mapping rules, compute
consensus prices, and publish results into the unified cache.

Key responsibilities (planned):
- Manage connector lifecycle for individual books (US + EU).
- Normalize market structures and identifiers.
- Persist line history with timestamps for downstream analytics.
- Surface merged book and market views for API consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class BookConnector(Protocol):
    """Protocol for individual bookmaker connectors."""

    book_key: str

    async def fetch(self, sport: str) -> Sequence[dict]:
        """Fetch raw odds payloads for a single sport."""


@dataclass
class OddsSnapshot:
    """Canonical odds payload ready for caching or export."""

    canonical_event_id: str
    sport: str
    markets: dict
    books: dict
    generated_at: str


__all__ = ["BookConnector", "OddsSnapshot"]

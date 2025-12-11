"""Props engine scaffolding for V6 unified endpoint.

Responsible for consolidating player and team proposition markets from every
book, applying normalization, and linking data to canonical roster identities.

Planned responsibilities:
- Normalize player names and stat types using roster enrichment services.
- Reconcile markets across books to generate comparable runners.
- Track availability and best-price information per proposition.
- Expose prop-specific caches for quick API access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class PropsConnector(Protocol):
    """Protocol for connectors that supply proposition data."""

    book_key: str

    async def fetch_props(self, sport: str) -> Sequence[dict]:
        """Fetch raw proposition payloads for a given sport."""


@dataclass
class PropSnapshot:
    """Normalized proposition entry ready for caching or export."""

    canonical_prop_id: str
    canonical_event_id: str
    player_name: str
    stat_type: str
    line: float | None
    odds_view: dict
    metadata: dict


__all__ = ["PropsConnector", "PropSnapshot"]

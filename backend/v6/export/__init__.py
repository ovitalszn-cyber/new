"""Export engine scaffolding for V6 unified endpoint.

Provides mechanisms to expose odds, stats, and props snapshots via CSV/JSON
formats as well as any future transports (e.g., webhooks, s3 dumps).

Planned responsibilities:
- Read canonical snapshots from caches or historical storage.
- Transform data into schema-compliant tabular/JSON payloads.
- Handle pagination, filtering, and time-range queries for historical requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterable


class ExportWriter(Protocol):
    """Protocol describing a sink that emits formatted exports."""

    async def write(self, records: Iterable[dict]) -> bytes:
        """Serialize the provided records into the target format."""


@dataclass
class ExportJob:
    """Represents a single export request."""

    export_type: str  # e.g., "odds", "props", "game_stats"
    format: str       # e.g., "csv", "json"
    filters: dict
    generated_at: str


__all__ = ["ExportWriter", "ExportJob"]

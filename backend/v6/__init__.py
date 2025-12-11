"""V6 Unified Endpoint package scaffolding.

This namespace houses the four primary engines for the unified AI developer
endpoint:

- stats: ingest and normalize game statistics from upstream feeds.
- odds: aggregate live and pregame odds with per-book provenance.
- props: standardize player and team proposition markets.
- export: provide CSV/JSON exports for odds, stats, and props.

The package currently contains lightweight interfaces and placeholders that will
be expanded as we port battle-tested logic from v5 and new integrations.
"""

__all__ = [
    "stats",
    "odds",
    "props",
    "export",
]

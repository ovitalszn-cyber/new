"""PrizePicks game type payout tables captured from the mobile API.

These tables map the game type ID (as returned by the PrizePicks
`/game_types` endpoint) to their payout structures. Downstream code can
use these multipliers to compute implied odds for Flex/Power/Goblin/Demon
slips without hitting the authenticated endpoint at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional


@dataclass(frozen=True)
class PrizePicksPayoutTable:
    """Normalized representation of a PrizePicks payout table.

    Attributes:
        name: Human-readable label ("Flex Play", "Power Play", etc.).
        payouts: Mapping of leg count -> mapping of hits -> multiplier.
            For example, ``payouts[6][5]`` is the multiplier when a
            six-leg slip hits five selections.
        payouts_srp: Optional SRP grid supplied by the API. Entries are
            left as-is because their precise semantics depend on
            additional context (e.g. single-rule plays).
        is_adjusted: Whether PrizePicks marks the table as "adjusted".
        is_cashout_eligible: True if slips are eligible for cashout.
        is_max_payout_alert: True if PrizePicks flags maximum payout
            alerts for this table.
    """

    name: str
    payouts: Mapping[int, Mapping[int, float]]
    payouts_srp: Optional[Mapping[str, list[list[float]]]]
    is_adjusted: bool
    is_cashout_eligible: bool
    is_max_payout_alert: bool


# NOTE: The captured response currently only includes Flex and Power play
# tables for six-leg slips. The structure is future-proofed so that
# additional tables (Goblin, Demon, SRP, etc.) can be appended by simply
# extending this dictionary.
PRIZEPICKS_GAME_TYPES: Dict[str, PrizePicksPayoutTable] = {
    "1": PrizePicksPayoutTable(
        name="Flex Play",
        payouts={
            6: {
                6: 15.0,
                5: 2.0,
                4: 0.4,
            }
        },
        payouts_srp={
            "power": [
                [14.5, 0.0, 0.0],
                [7.5, 0.0, 0.0],
                [4.0, 0.0, 0.0],
                [2.25, 0.0, 0.0],
                [1.25, 0.0, 0.0],
            ],
            "flex": [
                [5.0, 2.0, 0.4],
                [4.0, 1.0, 0.0],
                [1.75, 1.0, 0.0],
                [2.6, 0.0, 0.0],
                [1.5, 0.0, 0.0],
            ],
        },
        is_adjusted=True,
        is_cashout_eligible=True,
        is_max_payout_alert=False,
    ),
    "2": PrizePicksPayoutTable(
        name="Power Play",
        payouts={
            6: {
                6: 25.5,
            }
        },
        payouts_srp={
            "power": [
                [14.5, 0.0, 0.0],
                [7.5, 0.0, 0.0],
                [4.0, 0.0, 0.0],
                [2.25, 0.0, 0.0],
                [1.25, 0.0, 0.0],
            ],
            "flex": [
                [5.0, 2.0, 0.4],
                [4.0, 1.0, 0.0],
                [1.75, 1.0, 0.0],
                [2.6, 0.0, 0.0],
                [1.5, 0.0, 0.0],
            ],
        },
        is_adjusted=True,
        is_cashout_eligible=True,
        is_max_payout_alert=False,
    ),
}


def get_game_type_by_name(name: str) -> Optional[PrizePicksPayoutTable]:
    """Return the payout table matching ``name`` (case insensitive)."""

    lowered = name.lower()
    for table in PRIZEPICKS_GAME_TYPES.values():
        if table.name.lower() == lowered:
            return table
    return None


def get_game_type(game_type_id: str) -> Optional[PrizePicksPayoutTable]:
    """Fetch a payout table by its string ID."""

    return PRIZEPICKS_GAME_TYPES.get(str(game_type_id))

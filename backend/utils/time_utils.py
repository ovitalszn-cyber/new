from __future__ import annotations

from datetime import datetime, timezone
from typing import Union
from zoneinfo import ZoneInfo

EASTERN_TZ = ZoneInfo("America/New_York")


def format_eastern_datetime(
    value: Union[str, datetime, None],
    include_date: bool = True,
) -> str:
    """
    Convert a datetime (or string) into 12-hour Eastern Time text.

    Args:
        value: datetime object or parseable string.
        include_date: include MM/DD/YYYY in the formatted string.
    """
    if not value:
        return ""

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return ""

        # ISO8601 (with or without timezone info)
        if "T" in text:
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return text
        else:
            # Lunosoft style "MM/DD/YYYY HH:MM"
            try:
                dt = datetime.strptime(text, "%m/%d/%Y %H:%M")
                dt = dt.replace(tzinfo=EASTERN_TZ)  # assume already Eastern
            except ValueError:
                return text
    else:
        return str(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    eastern_dt = dt.astimezone(EASTERN_TZ)
    fmt = "%m/%d/%Y %I:%M %p %Z" if include_date else "%I:%M %p %Z"
    formatted = eastern_dt.strftime(fmt)
    return formatted.lstrip("0")

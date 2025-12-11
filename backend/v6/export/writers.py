"""Streaming export writers for CSV and JSONL outputs."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional


class JSONLinesWriter:
    """Serialize export rows as newline-delimited JSON (NDJSON)."""

    def __init__(self, ensure_ascii: bool = False):
        self.ensure_ascii = ensure_ascii

    async def stream(self, records: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[bytes]:
        async for record in records:
            line = json.dumps(
                record,
                ensure_ascii=self.ensure_ascii,
                default=self._json_default,
            )
            yield (line + "\n").encode("utf-8")

    @staticmethod
    def _json_default(value: Any) -> Any:
        """Fallback serializer for non-JSON-native objects."""
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)


class CSVWriter:
    """Serialize export rows as CSV with dynamic headers."""

    def __init__(self, fieldnames: Optional[List[str]] = None):
        self._fieldnames = fieldnames

    async def stream(self, records: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[bytes]:
        buffer = io.StringIO()
        writer: Optional[csv.DictWriter] = None
        header_written = False

        async for record in records:
            if writer is None:
                fieldnames = self._fieldnames or sorted(record.keys())
                writer = csv.DictWriter(buffer, fieldnames=fieldnames)
                writer.writeheader()
                header_written = True
                yield buffer.getvalue().encode("utf-8")
                buffer.seek(0)
                buffer.truncate(0)

            writer.writerow(self._coerce_values(writer.fieldnames, record))
            yield buffer.getvalue().encode("utf-8")
            buffer.seek(0)
            buffer.truncate(0)

        # If no records were streamed but explicit headers were provided, emit header row
        if not header_written and self._fieldnames:
            writer = csv.DictWriter(buffer, fieldnames=self._fieldnames)
            writer.writeheader()
            yield buffer.getvalue().encode("utf-8")

    @staticmethod
    def _coerce_values(fieldnames: Iterable[str], record: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all requested fieldnames are present and string-friendly."""
        coerced: Dict[str, Any] = {}
        for field in fieldnames:
            value = record.get(field)
            if hasattr(value, "isoformat"):
                coerced[field] = value.isoformat()
            elif isinstance(value, (dict, list)):
                coerced[field] = json.dumps(value)
            else:
                coerced[field] = value
        return coerced

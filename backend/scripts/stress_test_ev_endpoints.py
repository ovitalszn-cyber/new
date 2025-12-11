#!/usr/bin/env python3
"""Simple EV endpoint stress tester.

This script repeatedly calls KashRock EV-related endpoints to surface errors
before launch. It focuses on the high-value `/v6/ev` APIs (including
variations) plus the cached EV props endpoint.

Example usage:
    python scripts/stress_test_ev_endpoints.py \
        --base-url http://localhost:8000 \
        --api-key YOUR_KEY \
        --iterations 5 \
        --concurrency 8
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from typing import Any, Dict, List, Optional

import httpx


# Default EV-focused endpoints to call each iteration
ENDPOINTS: List[Dict[str, Any]] = [
    {
        "name": "ev_nfl_default",
        "method": "GET",
        "path": "/v6/ev",
        "params": {"sport": "americanfootball_nfl"},
    },
    {
        "name": "ev_nfl_books_filtered",
        "method": "GET",
        "path": "/v6/ev",
        "params": {
            "sport": "americanfootball_nfl",
            "books": "draftkings,fanduel,prizepicks",
        },
    },
    {
        "name": "ev_nfl_raw",
        "method": "GET",
        "path": "/v6/ev",
        "params": {"sport": "americanfootball_nfl", "raw": "true"},
    },
    {
        "name": "ev_nba_default",
        "method": "GET",
        "path": "/v6/ev",
        "params": {"sport": "basketball_nba"},
    },
    {
        "name": "ev_props_nfl",
        "method": "GET",
        "path": "/v6/ev-props",
        "params": {"sport": "americanfootball_nfl"},
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stress test KashRock EV endpoints.")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="FastAPI server base URL.",
    )
    parser.add_argument(
        "--api-key",
        default="kr_test_key",
        help="API key for the Authorization header (Bearer).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of times to cycle through the endpoint list.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="Maximum number of in-flight requests.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP client timeout in seconds.",
    )
    return parser.parse_args()


async def call_endpoint(
    client: httpx.AsyncClient,
    endpoint: Dict[str, Any],
    semaphore: asyncio.Semaphore,
    iteration: int,
) -> Dict[str, Any]:
    async with semaphore:
        start = time.perf_counter()
        error: Optional[str] = None
        status_code: Optional[int] = None
        try:
            response = await client.request(
                endpoint["method"],
                endpoint["path"],
                params=endpoint.get("params"),
                json=endpoint.get("json"),
            )
            status_code = response.status_code
            response.raise_for_status()
            validate_response(endpoint, response.json())
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
        duration = (time.perf_counter() - start) * 1000.0
        return {
            "name": endpoint["name"],
            "path": endpoint["path"],
            "iteration": iteration,
            "status": status_code,
            "duration_ms": duration,
            "error": error,
        }


def validate_response(endpoint: Dict[str, Any], payload: Dict[str, Any]) -> None:
    """Lightweight validation tailored to EV endpoints."""
    if endpoint["path"].endswith("/ev"):
        if "ev_props" not in payload:
            raise ValueError("Response missing 'ev_props'")
        if not isinstance(payload["ev_props"], list):
            raise ValueError("'ev_props' must be a list")
    elif endpoint["path"].endswith("/ev-props"):
        if "ev_props" not in payload:
            raise ValueError("Response missing 'ev_props'")


def summarize_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for result in results:
        item = summary.setdefault(
            result["name"],
            {"calls": 0, "failures": 0, "durations": [], "path": result["path"], "errors": []},
        )
        item["calls"] += 1
        item["durations"].append(result["duration_ms"])
        if result["error"]:
            item["failures"] += 1
            item["errors"].append(result["error"])

    formatted: List[Dict[str, Any]] = []
    for name, data in summary.items():
        durations = data["durations"]
        formatted.append(
            {
                "name": name,
                "path": data["path"],
                "calls": data["calls"],
                "failures": data["failures"],
                "success_rate": f"{(1 - data['failures'] / data['calls']):.0%}",
                "avg_ms": f"{statistics.fmean(durations):.1f}",
                "p95_ms": f"{statistics.quantiles(durations, n=20)[18]:.1f}" if len(durations) > 1 else f"{durations[0]:.1f}",
                "errors": data["errors"][:3],  # surface first few errors
            }
        )
    return formatted


async def run_stress_test(args: argparse.Namespace) -> None:
    headers = {}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"

    timeout = httpx.Timeout(args.timeout)
    limits = httpx.Limits(max_keepalive_connections=args.concurrency, max_connections=args.concurrency * 2)

    async with httpx.AsyncClient(
        base_url=args.base_url,
        headers=headers,
        timeout=timeout,
        limits=limits,
    ) as client:
        semaphore = asyncio.Semaphore(args.concurrency)
        tasks: List[asyncio.Task] = []

        for iteration in range(1, args.iterations + 1):
            for endpoint in ENDPOINTS:
                tasks.append(
                    asyncio.create_task(call_endpoint(client, endpoint, semaphore, iteration))
                )

        results = await asyncio.gather(*tasks)

    summary = summarize_results(results)
    print("\n=== EV Endpoint Stress Test Summary ===")
    for item in summary:
        print(
            f"{item['name']:<22} {item['success_rate']:>7} success "
            f"(avg {item['avg_ms']} ms, p95 {item['p95_ms']} ms) "
            f"failures={item['failures']}/{item['calls']}"
        )
        if item["errors"]:
            for idx, err in enumerate(item["errors"], start=1):
                print(f"    Error {idx}: {err}")


def main() -> None:
    args = parse_args()
    asyncio.run(run_stress_test(args))


if __name__ == "__main__":
    main()

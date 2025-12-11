import argparse
import asyncio
from datetime import date

from .backfill_nba_boxscores import backfill_nba_boxscores, _parse_date


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill MLB player boxscores into the historical DB",
    )
    parser.add_argument("--from", dest="start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="Max concurrent boxscore requests",
    )
    args = parser.parse_args()

    start: date = _parse_date(args.start)
    end: date = _parse_date(args.end)

    asyncio.run(
        backfill_nba_boxscores(
            start_date=start,
            end_date=end,
            concurrency=args.concurrency,
            sport="mlb",
        )
    )


if __name__ == "__main__":
    main()

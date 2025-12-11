"""
Scraper Error Handling Utilities
Wraps book scrapers with standardized error handling.
"""

from typing import Any, Dict, List, Optional, Callable, Awaitable
import asyncio
import structlog
from datetime import datetime

logger = structlog.get_logger()


async def safe_scraper_call(
    scraper_func: Callable[[], Awaitable[Any]],
    book_name: str,
    sport: Optional[str] = None,
    timeout_seconds: int = 30,
    max_retries: int = 1
) -> Dict[str, Any]:
    """
    Execute scraper function with error handling and standardized response.

    Args:
        scraper_func: Async function that returns scraper data
        book_name: Name of the bookmaker
        sport: Sport being scraped (for logging)
        timeout_seconds: Timeout in seconds
        max_retries: Number of retry attempts

    Returns:
        Standardized response dict with 'data', 'errors', 'success', 'timestamp'
    """
    response = {
        "book_name": book_name,
        "sport": sport,
        "success": False,
        "data": None,
        "errors": [],
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": 0
    }

    for attempt in range(max_retries + 1):
        try:
            start_time = datetime.utcnow()

            # Execute scraper with timeout
            if timeout_seconds > 0:
                result = await asyncio.wait_for(scraper_func(), timeout=timeout_seconds)
            else:
                result = await scraper_func()

            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds() * 1000)

            response.update({
                "success": True,
                "data": result,
                "duration_ms": duration
            })

            logger.info(
                "scraper_success",
                book=book_name,
                sport=sport,
                attempt=attempt + 1,
                duration_ms=duration
            )

            return response

        except asyncio.TimeoutError:
            error_msg = f"Timeout after {timeout_seconds}s"
            response["errors"].append({
                "type": "timeout",
                "message": error_msg,
                "attempt": attempt + 1
            })

            logger.warning(
                "scraper_timeout",
                book=book_name,
                sport=sport,
                attempt=attempt + 1,
                timeout_seconds=timeout_seconds
            )

        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__

            response["errors"].append({
                "type": error_type,
                "message": error_msg,
                "attempt": attempt + 1
            })

            logger.warning(
                "scraper_error",
                book=book_name,
                sport=sport,
                attempt=attempt + 1,
                error_type=error_type,
                error_message=error_msg
            )

        # Wait before retry (exponential backoff)
        if attempt < max_retries:
            wait_time = 2 ** attempt  # 1s, 2s, 4s...
            await asyncio.sleep(wait_time)

    # All attempts failed
    response["duration_ms"] = int((datetime.utcnow() - datetime.fromisoformat(response["timestamp"])).total_seconds() * 1000)

    logger.error(
        "scraper_failed_all_attempts",
        book=book_name,
        sport=sport,
        attempts=max_retries + 1,
        errors=response["errors"]
    )

    return response


async def scrape_multiple_books(
    scrapers: Dict[str, Callable[[], Awaitable[Any]]],
    sport: Optional[str] = None,
    timeout_seconds: int = 30,
    max_concurrent: int = 5
) -> Dict[str, Dict[str, Any]]:
    """
    Scrape multiple books concurrently with error handling.

    Args:
        scrapers: Dict of book_name -> scraper_function
        sport: Sport being scraped
        timeout_seconds: Timeout per scraper
        max_concurrent: Max concurrent scrapers

    Returns:
        Dict of book_name -> standardized response
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results = {}

    async def scrape_book(book_name: str, scraper_func: Callable[[], Awaitable[Any]]):
        async with semaphore:
            result = await safe_scraper_call(
                scraper_func,
                book_name=book_name,
                sport=sport,
                timeout_seconds=timeout_seconds
            )
            results[book_name] = result

    # Launch all scrapers concurrently
    tasks = [
        scrape_book(book_name, scraper_func)
        for book_name, scraper_func in scrapers.items()
    ]

    await asyncio.gather(*tasks, return_exceptions=True)

    # Log summary
    successful = sum(1 for r in results.values() if r["success"])
    failed = len(results) - successful

    logger.info(
        "multi_book_scrape_complete",
        sport=sport,
        total_books=len(results),
        successful=successful,
        failed=failed
    )

    return results


def create_empty_book_response(book_name: str, sport: Optional[str] = None) -> Dict[str, Any]:
    """
    Create standardized empty response for failed scraper.

    Args:
        book_name: Name of the bookmaker
        sport: Sport being scraped

    Returns:
        Empty standardized response
    """
    return {
        "book_name": book_name,
        "sport": sport,
        "success": False,
        "data": [],
        "errors": [{"type": "no_data", "message": "No data available"}],
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": 0
    }


def aggregate_scraper_results(results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate multiple scraper results into summary.

    Args:
        results: Dict of book_name -> scraper response

    Returns:
        Summary with totals and error breakdown
    """
    total = len(results)
    successful = sum(1 for r in results.values() if r["success"])
    failed = total - successful

    errors_by_type = {}
    for result in results.values():
        for error in result.get("errors", []):
            error_type = error.get("type", "unknown")
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

    total_duration = sum(r.get("duration_ms", 0) for r in results.values())

    return {
        "total_books": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
        "total_duration_ms": total_duration,
        "avg_duration_ms": round(total_duration / total, 1) if total > 0 else 0,
        "errors_by_type": errors_by_type,
        "book_results": results
    }

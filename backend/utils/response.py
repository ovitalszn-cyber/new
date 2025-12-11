"""
API Response Utilities
Standardizes response structure across all endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import structlog

logger = structlog.get_logger()


def build_standard_response(
    data: Any,
    count: Optional[int] = None,
    sport: Optional[str] = None,
    source: Optional[str] = None,
    last_updated: Optional[str] = None,
    errors: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Build a standardized API response.

    Args:
        data: Main response data (list or dict)
        count: Number of items in data (if applicable)
        sport: Sport key (if applicable)
        source: Data source (e.g., "novig", "espn")
        last_updated: ISO timestamp string
        errors: List of error objects
        **kwargs: Additional fields to include

    Returns:
        Normalized response dict with consistent structure
    """
    response = {
        "data": data,
        "timestamp": last_updated or datetime.utcnow().isoformat(),
    }

    # Add optional fields if provided
    if count is not None:
        response["count"] = count
    if sport is not None:
        response["sport"] = sport
    if source is not None:
        response["source"] = source
    if errors is not None and errors:
        response["errors"] = errors

    # Add any additional fields
    response.update(kwargs)

    return response


def build_error_response(
    error_msg: str,
    status_code: int = 500,
    sport: Optional[str] = None,
    source: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a standardized error response.

    Args:
        error_msg: Human-readable error message
        status_code: HTTP status code
        sport: Sport key (if applicable)
        source: Data source (if applicable)
        details: Additional error details

    Returns:
        Error response dict
    """
    response = {
        "error": error_msg,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if sport:
        response["sport"] = sport
    if source:
        response["source"] = source
    if details:
        response["details"] = details

    return response


def validate_response_structure(response: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that response contains required fields.

    Args:
        response: Response dict to validate
        required_fields: List of required field names

    Returns:
        True if valid, False if missing required fields
    """
    missing = [field for field in required_fields if field not in response]
    if missing:
        logger.warning("Response missing required fields", missing=missing)
        return False
    return True

"""
Input validation and sanitization utilities
"""

import re
from typing import Optional
from fastapi import HTTPException

# Maximum parameter length
MAX_PARAM_LENGTH = 200

# Valid sport key pattern (alphanumeric, underscores, hyphens only)
SPORT_KEY_PATTERN = re.compile(r'^[a-z0-9_\-]+$', re.IGNORECASE)

# SQL injection patterns to reject
SQL_INJECTION_PATTERNS = [
    r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)',
    r'(\'|"|;|--|\*|/\*|\*/)',
    r'(\bOR\b.*=.*)',
    r'(\bAND\b.*=.*)',
]

def validate_sport_key(sport: str) -> str:
    """
    Validate and sanitize sport key parameter.
    
    Args:
        sport: Sport key to validate
        
    Returns:
        Sanitized sport key
        
    Raises:
        HTTPException: If sport key is invalid
    """
    if not sport:
        raise HTTPException(status_code=400, detail="Sport parameter is required")
    
    # Check length
    if len(sport) > MAX_PARAM_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Sport parameter too long (max {MAX_PARAM_LENGTH} characters)"
        )
    
    # Check for SQL injection patterns
    sport_lower = sport.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, sport_lower, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Invalid sport parameter: contains potentially malicious content"
            )
    
    # Check format (alphanumeric, underscores, hyphens only)
    if not SPORT_KEY_PATTERN.match(sport):
        raise HTTPException(
            status_code=400,
            detail="Invalid sport parameter format. Use alphanumeric characters, underscores, and hyphens only"
        )
    
    return sport.strip()

def validate_bookmaker_key(bookmaker: str) -> str:
    """
    Validate and sanitize bookmaker key parameter.
    
    Args:
        bookmaker: Bookmaker key to validate
        
    Returns:
        Sanitized bookmaker key
        
    Raises:
        HTTPException: If bookmaker key is invalid
    """
    if not bookmaker:
        raise HTTPException(status_code=400, detail="Bookmaker parameter is required")
    
    if len(bookmaker) > MAX_PARAM_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Bookmaker parameter too long (max {MAX_PARAM_LENGTH} characters)"
        )
    
    # Check for SQL injection patterns
    bookmaker_lower = bookmaker.lower()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, bookmaker_lower, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Invalid bookmaker parameter: contains potentially malicious content"
            )
    
    if not SPORT_KEY_PATTERN.match(bookmaker):
        raise HTTPException(
            status_code=400,
            detail="Invalid bookmaker parameter format"
        )
    
    return bookmaker.strip()

def validate_limit(limit: int, max_limit: int = 1000, min_limit: int = 1) -> int:
    """
    Validate limit parameter.
    
    Args:
        limit: Limit value to validate
        max_limit: Maximum allowed limit
        min_limit: Minimum allowed limit
        
    Returns:
        Validated limit
        
    Raises:
        HTTPException: If limit is invalid
    """
    if limit < min_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Limit must be at least {min_limit}"
        )
    
    if limit > max_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Limit cannot exceed {max_limit}"
        )
    
    return limit

def sanitize_string(value: str, max_length: int = MAX_PARAM_LENGTH) -> Optional[str]:
    """
    Sanitize a string parameter.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string or None if invalid
    """
    if not value:
        return None
    
    if len(value) > max_length:
        return None
    
    # Remove any control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    return sanitized.strip() if sanitized else None







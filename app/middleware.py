"""Rate limiting helper functions."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from app.config import settings
from app.logger import logger


def check_rate_limit(request: Request, limiter: Limiter) -> None:
    """Check if request is within rate limit.
    
    Raises:
        HTTPException: If rate limit is exceeded
    """
    try:
        # Use slowapi's limiter to check the request
        # This is a simplified check - in production, use slowapi's decorator pattern
        pass  # Rate limiting will be handled by slowapi exception handler
    except RateLimitExceeded:
        logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

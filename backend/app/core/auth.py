"""
API Key Authentication

Provides API key verification for protected endpoints.
Uses constant-time comparison to prevent timing attacks.
"""

import hmac
import logging
from typing import Optional

from fastapi import HTTPException, Header, Request

from app.config import get_settings

logger = logging.getLogger(__name__)


async def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """
    Verify API key for protected endpoints.

    Args:
        request: FastAPI request object
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: 401 if API key is missing or invalid
    """
    settings = get_settings()

    # If no API keys configured, reject (fail-secure in production)
    if not settings.api_keys_list:
        if settings.is_production:
            logger.error("API key required but none configured")
            raise HTTPException(
                status_code=500,
                detail="Server configuration error"
            )
        # In development without API keys, allow access with warning
        logger.warning("No API keys configured - allowing unauthenticated access")
        return ""

    # Check if API key provided
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required"
        )

    # Constant-time comparison to prevent timing attacks
    for valid_key in settings.api_keys_list:
        if hmac.compare_digest(x_api_key, valid_key):
            return x_api_key

    # Log failed attempt (without exposing the key)
    logger.warning(
        f"Invalid API key attempt from {request.client.host if request.client else 'unknown'}"
    )
    raise HTTPException(
        status_code=401,
        detail="Invalid API key"
    )


async def get_optional_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Optional[str]:
    """
    Get API key if provided, but don't require it.

    Use this for endpoints that work with or without authentication,
    but may provide enhanced features with a valid key.

    Args:
        request: FastAPI request object
        x_api_key: API key from X-API-Key header

    Returns:
        The validated API key if provided and valid, None otherwise
    """
    settings = get_settings()

    # If no API key provided, return None
    if not x_api_key:
        return None

    # If no keys configured, return None
    if not settings.api_keys_list:
        return None

    # Validate the provided key
    for valid_key in settings.api_keys_list:
        if hmac.compare_digest(x_api_key, valid_key):
            return x_api_key

    # Invalid key provided - don't raise, just return None
    return None

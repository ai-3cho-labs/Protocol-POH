"""
$COPPER Rate Limiter Configuration

Shared rate limiter instance for the application.
Requires Redis in production for proper multi-worker rate limiting.
"""

import logging
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_wallet_key(request: Request) -> str:
    """
    Rate limit key combining IP and wallet address.

    This provides stricter per-wallet rate limiting to prevent
    abuse targeting specific wallet endpoints.
    """
    ip = get_remote_address(request)
    # Extract wallet from path if present
    wallet = request.path_params.get("wallet", "")
    if wallet:
        # Truncate wallet for key to save space
        return f"{ip}:{wallet[:8]}"
    return ip


def _get_storage_uri() -> str | None:
    """
    Get storage URI for rate limiter.

    In development with embedded Celery, uses in-memory storage to avoid
    SSL configuration issues with Upstash Redis.
    In production, Redis is required for proper rate limiting across workers.
    """
    # In development with embedded Celery, use memory storage
    # This avoids SSL cert issues with Upstash and is fine for single-process dev
    if settings.embedded_celery:
        logger.info("Rate limiter: using in-memory storage (embedded Celery mode)")
        return "memory://"

    if settings.redis_url:
        logger.info("Rate limiter: using Redis storage")
        return settings.redis_url

    if settings.is_production:
        raise ValueError(
            "Redis URL is required for rate limiting in production. "
            "Set REDIS_URL environment variable."
        )

    logger.warning(
        "Rate limiter: using in-memory storage (development only). "
        "This will not work correctly with multiple workers."
    )
    return "memory://"


def _create_limiter() -> Limiter:
    """
    Create and configure the rate limiter instance.

    SECURITY: In production, Redis is REQUIRED for proper rate limiting.
    Without Redis, rate limits don't work across workers and attackers
    can bypass limits by hitting different workers.
    """
    try:
        storage_uri = _get_storage_uri()
    except ValueError as e:
        # SECURITY: Fail hard in production - do not allow startup without Redis
        if settings.is_production:
            logger.critical(f"FATAL: {e}")
            raise RuntimeError(
                "Cannot start in production without Redis for rate limiting. "
                "Set REDIS_URL environment variable."
            )
        logger.warning(str(e))
        storage_uri = "memory://"

    return Limiter(
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=["200/minute"],
        strategy="fixed-window",
    )


# Create shared limiter instance
limiter = _create_limiter()


def validate_rate_limiter_config() -> bool:
    """
    Validate rate limiter configuration at startup.

    Returns:
        True if properly configured, False otherwise.
    """
    if settings.is_production and not settings.redis_url:
        logger.error("Rate limiter validation failed: Redis required in production")
        return False

    return True

"""
$COPPER Webhook Handler

Handles incoming webhooks from Helius for transaction monitoring.
Note: Sell detection and tier drops have been removed - distribution is now balance-based.
"""

import hmac
import logging
import re
import time
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel

from app.utils.rate_limiter import limiter
from app.services.helius import get_helius_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/webhook", tags=["webhook"])

# Solana wallet address validation: 32-44 base58 characters
WALLET_REGEX = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

# SECURITY: Helius webhook IP allowlist (update if Helius changes their IPs)
# See: https://docs.helius.dev/webhooks/ip-addresses
HELIUS_IP_ALLOWLIST = {
    # Helius production IPs - verify these are current
    "52.1.58.225",
    "18.213.41.172",
    "52.206.218.133",
    "3.211.135.60",
    "34.227.23.72",
    "52.44.26.199",
}

# Maximum age for webhook timestamps to prevent replay attacks
# Production: 5 minutes (strict)
# Development: 30 minutes (more lenient for testing)
WEBHOOK_MAX_AGE_SECONDS_PRODUCTION = 300
WEBHOOK_MAX_AGE_SECONDS_DEVELOPMENT = 1800


class WebhookResponse(BaseModel):
    """Webhook response."""

    success: bool
    message: str
    processed: int = 0


def verify_webhook_auth(auth_header: Optional[str], secret: str) -> bool:
    """
    Verify Helius webhook authorization.

    Helius sends the authHeader value in the Authorization header.

    Args:
        auth_header: Authorization header value.
        secret: Expected auth header value (HELIUS_WEBHOOK_SECRET).

    Returns:
        True if authorization is valid.
    """
    if not auth_header or not secret:
        return False

    return hmac.compare_digest(auth_header, secret)


def validate_webhook_timestamp(timestamp: Optional[int]) -> bool:
    """
    Validate webhook timestamp to prevent replay attacks.

    SECURITY: Timestamps are ALWAYS required to prevent replay attacks.
    Production uses strict 5-minute window, development uses 30-minute window.

    Args:
        timestamp: Unix timestamp from webhook payload.

    Returns:
        True if timestamp is within acceptable range.
    """
    if timestamp is None:
        # SECURITY: Always require timestamps - replay attacks are possible without them
        logger.warning("Webhook rejected: missing timestamp (replay protection)")
        return False

    current_time = int(time.time())
    age = abs(current_time - timestamp)

    # Use stricter window in production
    max_age = (
        WEBHOOK_MAX_AGE_SECONDS_PRODUCTION
        if settings.is_production
        else WEBHOOK_MAX_AGE_SECONDS_DEVELOPMENT
    )

    if age > max_age:
        logger.warning(f"Webhook timestamp too old: {age}s (max: {max_age}s)")
        return False

    return True


@router.post("/helius", response_model=WebhookResponse)
@limiter.limit("100/minute")
async def helius_webhook(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """
    Handle Helius webhook for transaction monitoring.

    Logs transactions for analytics purposes.
    Note: Sell detection has been removed - distribution is now balance-based.

    SECURITY: Webhook authorization verification is MANDATORY.
    Configure HELIUS_WEBHOOK_SECRET in environment (must match Helius authHeader).
    """
    # MANDATORY: Verify webhook authorization
    if not settings.helius_webhook_secret:
        logger.error("HELIUS_WEBHOOK_SECRET not configured - rejecting webhook")
        raise HTTPException(
            status_code=503,
            detail="Webhook endpoint not configured. Set HELIUS_WEBHOOK_SECRET.",
        )

    # SECURITY: Validate source IP in production (defense in depth)
    if settings.is_production:
        client_ip = request.client.host if request.client else None
        if client_ip and client_ip not in HELIUS_IP_ALLOWLIST:
            logger.warning(f"Webhook rejected: IP {client_ip} not in Helius allowlist")
            raise HTTPException(status_code=403, detail="Forbidden")

    if not verify_webhook_auth(authorization, settings.helius_webhook_secret):
        logger.warning(
            f"Invalid webhook authorization from {request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(status_code=401, detail="Invalid authorization")

    # Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Handle array of transactions (Helius sends batches)
    transactions = payload if isinstance(payload, list) else [payload]

    if len(transactions) > 100:
        logger.warning(f"Webhook batch too large: {len(transactions)} transactions")
        raise HTTPException(
            status_code=400,
            detail="Batch too large. Maximum 100 transactions per request.",
        )

    # Validate webhook timestamp from first transaction
    if transactions:
        first_tx = transactions[0]
        tx_timestamp = first_tx.get("timestamp") or first_tx.get("blockTime")
        if not validate_webhook_timestamp(tx_timestamp):
            raise HTTPException(
                status_code=400,
                detail="Webhook timestamp missing or too old. Possible replay attack.",
            )

    # Log transactions for analytics (no sell processing)
    helius = get_helius_service()
    processed = 0

    for tx in transactions:
        try:
            parsed = helius.parse_webhook_transaction(tx)
            if parsed:
                # Just log for analytics - no sell detection/tier processing
                logger.debug(
                    f"Transaction logged: signature={parsed.signature[:16]}..., "
                    f"type={'sell' if parsed.is_sell else 'buy'}"
                )
                processed += 1
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            continue

    return WebhookResponse(
        success=True,
        message=f"Logged {processed} transactions",
        processed=processed,
    )


@router.get("/helius/status")
async def webhook_status():
    """
    Get webhook configuration status.

    Note: Does not expose sensitive details, only configuration state.
    """
    # Check if webhook secret is configured
    secret_configured = bool(settings.helius_webhook_secret)

    if not secret_configured:
        return {
            "configured": False,
            "error": "HELIUS_WEBHOOK_SECRET not set. Webhook endpoint is disabled.",
        }

    helius = get_helius_service()

    try:
        webhooks = await helius.get_webhooks()
        return {
            "configured": True,
            "signature_verification": "enabled",
            "registered_webhooks": len(webhooks),
            # Only show webhook count, not URLs or IDs (security)
        }
    except Exception as e:
        logger.error(f"Error fetching webhook status: {e}")
        return {
            "configured": True,
            "signature_verification": "enabled",
            "registered_webhooks": "unknown",
            "note": "Could not fetch webhook list from Helius",
        }

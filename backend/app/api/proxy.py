"""
RPC Proxy Endpoint

Proxies Solana RPC requests to Helius, keeping the API key server-side.
This prevents exposing the API key in the frontend code.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Request, HTTPException

from app.config import get_settings
from app.utils.rate_limiter import limiter
from app.utils.http_client import get_http_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/proxy", tags=["proxy"])

# Allowed RPC methods to prevent abuse
ALLOWED_RPC_METHODS = {
    # Basic queries
    "getHealth",
    "getVersion",
    "getSlot",
    "getBlockHeight",
    "getLatestBlockhash",
    # Account queries
    "getAccountInfo",
    "getBalance",
    "getTokenAccountBalance",
    "getTokenAccountsByOwner",
    "getProgramAccounts",
    # Transaction queries
    "getTransaction",
    "getSignaturesForAddress",
    "getSignatureStatuses",
    # Block queries
    "getBlock",
    "getBlockTime",
    # Other common queries
    "getMinimumBalanceForRentExemption",
    "getFeeForMessage",
    "getRecentPrioritizationFees",
}

# Methods that should not be proxied (write operations, etc.)
BLOCKED_RPC_METHODS = {
    "sendTransaction",
    "simulateTransaction",
    "requestAirdrop",
}


@router.post("/rpc")
@limiter.limit("60/minute")
async def rpc_proxy(request: Request) -> Dict[str, Any]:
    """
    Proxy RPC requests to Helius, keeping API key server-side.

    This endpoint accepts standard JSON-RPC 2.0 requests and forwards them
    to the configured Solana RPC (Helius). The API key is added server-side.

    Rate limited to prevent abuse.
    """
    settings = get_settings()

    if not settings.helius_api_key:
        raise HTTPException(status_code=503, detail="RPC not configured")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Validate JSON-RPC structure
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=400, detail="Request body must be a JSON object"
        )

    method = body.get("method")
    if not method:
        raise HTTPException(status_code=400, detail="Missing 'method' field")

    # Check if method is blocked
    if method in BLOCKED_RPC_METHODS:
        raise HTTPException(
            status_code=403, detail=f"Method '{method}' is not allowed through proxy"
        )

    # SECURITY: Strict allowlist - reject any method not explicitly allowed
    # This prevents exposure of new/unknown dangerous RPC methods
    if method not in ALLOWED_RPC_METHODS:
        logger.warning(f"RPC proxy: rejected unknown method '{method}'")
        raise HTTPException(
            status_code=403, detail=f"Method '{method}' is not allowed through proxy"
        )

    # Ensure required JSON-RPC fields
    if "jsonrpc" not in body:
        body["jsonrpc"] = "2.0"
    if "id" not in body:
        body["id"] = 1

    try:
        client = await get_http_client()
        response = await client.post(settings.helius_rpc_url, json=body, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"RPC proxy error: {e}")
        raise HTTPException(status_code=502, detail="RPC request failed")


@router.get("/health")
@limiter.limit("60/minute")
async def proxy_health(request: Request) -> Dict[str, str]:
    """Health check for the RPC proxy."""
    settings = get_settings()

    if not settings.helius_api_key:
        return {"status": "unconfigured"}

    return {"status": "ok"}

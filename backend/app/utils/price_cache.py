"""
$GOLD Price Cache

Provides cached and resilient price fetching for GOLD token.
Used for calculating distribution thresholds and pool value.
Falls back to cached values when API is unavailable.
"""

import logging
import time
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

from app.utils.http_client import get_http_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

JUPITER_PRICE_API = "https://price.jup.ag/v4/price"
BIRDEYE_PRICE_API = "https://public-api.birdeye.so/public/price"
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens"

# Cache configuration
CACHE_TTL_SECONDS = 60  # Cache prices for 1 minute
STALE_TTL_SECONDS = 300  # Use stale cache up to 5 minutes if API fails


@dataclass
class CachedPrice:
    """Cached price with timestamp."""

    price: Decimal
    timestamp: float
    source: str


# In-memory cache (simple implementation; could use Redis for multi-worker)
_price_cache: dict[str, CachedPrice] = {}


async def get_gold_price_usd(use_fallback: bool = True) -> Decimal:
    """
    Get GOLD price in USD with caching and fallback.

    Tries Jupiter first, falls back to Birdeye, then to cached value.
    On devnet, uses configured fallback price since test tokens have no market price.

    Args:
        use_fallback: Whether to use cached value if all APIs fail.

    Returns:
        Price per token in USD, or Decimal(0) if unavailable.
    """
    token_mint = settings.gold_token_mint
    if not token_mint:
        logger.warning("GOLD token mint not configured, cannot fetch price")
        return Decimal(0)

    cache_key = f"price:{token_mint}"
    now = time.time()

    # Check cache first
    cached = _price_cache.get(cache_key)
    if cached and (now - cached.timestamp) < CACHE_TTL_SECONDS:
        logger.debug(f"Using cached price from {cached.source}: {cached.price}")
        return cached.price

    # On devnet, use configured fallback price (test tokens have no market price)
    if settings.is_devnet:
        devnet_price = Decimal(str(settings.devnet_gold_price_usd))
        _price_cache[cache_key] = CachedPrice(
            price=devnet_price, timestamp=now, source="devnet_fallback"
        )
        logger.debug(f"Using devnet fallback price: ${devnet_price}")
        return devnet_price

    # Try DexScreener API first (most reliable, free, no auth)
    price = await _fetch_dexscreener_price(token_mint)
    if price and price > 0:
        _price_cache[cache_key] = CachedPrice(
            price=price, timestamp=now, source="dexscreener"
        )
        return price

    # Try Jupiter API
    price = await _fetch_jupiter_price(token_mint)
    if price and price > 0:
        _price_cache[cache_key] = CachedPrice(
            price=price, timestamp=now, source="jupiter"
        )
        return price

    # Try Birdeye API as fallback
    price = await _fetch_birdeye_price(token_mint)
    if price and price > 0:
        _price_cache[cache_key] = CachedPrice(
            price=price, timestamp=now, source="birdeye"
        )
        return price

    # Use stale cache if available and within stale TTL
    if use_fallback and cached:
        if (now - cached.timestamp) < STALE_TTL_SECONDS:
            logger.warning(
                f"Using stale cached price from {cached.source} "
                f"(age: {int(now - cached.timestamp)}s): {cached.price}"
            )
            return cached.price

    logger.error("All price feeds failed and no valid cache available")
    return Decimal(0)


async def _fetch_jupiter_price(token_mint: str) -> Optional[Decimal]:
    """Fetch price from Jupiter API."""
    try:
        client = get_http_client()
        response = await client.get(
            JUPITER_PRICE_API, params={"ids": token_mint}, timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        price_data = data.get("data", {}).get(token_mint, {})
        price = price_data.get("price", 0)

        if price and float(price) > 0:
            logger.debug(f"Jupiter price for {token_mint[:8]}...: ${price}")
            return Decimal(str(price))

        return None

    except Exception as e:
        logger.warning(f"Jupiter price fetch failed: {e}")
        return None


async def _fetch_birdeye_price(token_mint: str) -> Optional[Decimal]:
    """Fetch price from Birdeye API (public endpoint)."""
    try:
        client = get_http_client()
        response = await client.get(
            BIRDEYE_PRICE_API,
            params={"address": token_mint},
            headers={"accept": "application/json"},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            price = data.get("data", {}).get("value", 0)
            if price and float(price) > 0:
                logger.debug(f"Birdeye price for {token_mint[:8]}...: ${price}")
                return Decimal(str(price))

        return None

    except Exception as e:
        logger.warning(f"Birdeye price fetch failed: {e}")
        return None


async def _fetch_dexscreener_price(token_mint: str) -> Optional[Decimal]:
    """Fetch price from DexScreener API (free, no auth)."""
    try:
        client = get_http_client()
        response = await client.get(
            f"{DEXSCREENER_API}/{token_mint}",
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        # DexScreener returns pairs array, get price from first pair
        pairs = data.get("pairs", [])
        if pairs:
            # Use the pair with highest liquidity
            best_pair = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))
            price = best_pair.get("priceUsd")
            if price and float(price) > 0:
                logger.debug(f"DexScreener price for {token_mint[:8]}...: ${price}")
                return Decimal(str(price))

        return None

    except Exception as e:
        logger.warning(f"DexScreener price fetch failed: {e}")
        return None


def get_cached_price(token_mint: Optional[str] = None) -> Optional[CachedPrice]:
    """
    Get the current cached price without fetching.

    Args:
        token_mint: Token mint address. Defaults to GOLD_TOKEN_MINT.

    Returns:
        CachedPrice if available, None otherwise.
    """
    mint = token_mint or settings.gold_token_mint
    if not mint:
        return None

    return _price_cache.get(f"price:{mint}")


def clear_price_cache():
    """Clear all cached prices."""
    _price_cache.clear()
    logger.info("Price cache cleared")


async def warm_price_cache() -> bool:
    """
    Pre-populate the price cache.

    Call this at startup to ensure prices are available.

    Returns:
        True if cache was warmed successfully.
    """
    price = await get_gold_price_usd(use_fallback=False)
    if price > 0:
        logger.info(f"GOLD price cache warmed: ${price}")
        return True
    else:
        logger.warning("Failed to warm GOLD price cache")
        return False

"""
Cache Pre-computation Tasks

Background tasks for pre-computing and caching expensive calculations.
Reduces API response times by serving pre-computed data from Redis.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.database import get_worker_session_maker
from app.services.snapshot import SnapshotService
from app.services.distribution import DistributionService
from app.utils.async_utils import run_async
from app.utils.cache import get_cache_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


@celery_app.task(name="app.tasks.cache_task.refresh_leaderboard_cache")
def refresh_leaderboard_cache() -> dict:
    """
    Pre-compute and cache the leaderboard.

    Runs every minute to ensure leaderboard data is always fresh in cache.
    API reads from cache instead of computing on each request.
    """
    return run_async(_refresh_leaderboard_cache())


async def _refresh_leaderboard_cache() -> dict:
    """Async implementation of leaderboard cache refresh."""
    try:
        session_maker = get_worker_session_maker()
        cache = get_cache_service()

        async with session_maker() as db:
            # Get latest snapshot
            snapshot_service = SnapshotService(db)
            latest_snapshot = await snapshot_service.get_latest_snapshot()

            if not latest_snapshot:
                logger.warning("No snapshots found for leaderboard cache")
                return {"status": "skipped", "reason": "no_snapshots"}

            from app.models import Balance, ExcludedWallet

            # Get excluded wallets
            excluded_result = await db.execute(select(ExcludedWallet.wallet))
            excluded = {w for (w,) in excluded_result.all()}

            # Get top balances from latest snapshot
            result = await db.execute(
                select(Balance.wallet, Balance.balance)
                .where(Balance.snapshot_id == latest_snapshot.id)
                .order_by(Balance.balance.desc())
                .limit(100)
            )
            balances = [(w, b) for w, b in result.all() if w not in excluded and b > 0]

            # Convert to serializable format
            leaderboard_data = [
                {
                    "rank": i + 1,
                    "wallet": w,
                    "balance": b,
                }
                for i, (w, b) in enumerate(balances)
            ]

            # Cache the leaderboard
            await cache.set_leaderboard(leaderboard_data)

            logger.info(f"Leaderboard cache refreshed: {len(leaderboard_data)} entries")

            return {
                "status": "success",
                "entries": len(leaderboard_data),
                "cached_at": utc_now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Failed to refresh leaderboard cache: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.cache_task.refresh_pool_cache")
def refresh_pool_cache() -> dict:
    """
    Pre-compute and cache pool status.

    Runs every 30 seconds to keep pool data fresh.
    """
    return run_async(_refresh_pool_cache())


async def _refresh_pool_cache() -> dict:
    """Async implementation of pool cache refresh."""
    try:
        session_maker = get_worker_session_maker()
        cache = get_cache_service()

        async with session_maker() as db:
            distribution_service = DistributionService(db)

            # Get pool status and GOLD price
            from app.utils.price_cache import get_gold_price_usd

            status = await distribution_service.get_pool_status()
            gold_price = await get_gold_price_usd()

            # Get existing cache to preserve gold_price if new fetch fails
            existing_cache = await cache.get_pool_status()
            existing_gold_price = existing_cache.get("gold_price_usd", 0) if existing_cache else 0

            # Only use new price if it's valid (> 0), otherwise keep existing
            final_gold_price = float(gold_price) if gold_price > 0 else existing_gold_price

            # If we still have no valid price, skip caching to avoid corrupting cache
            if final_gold_price <= 0:
                logger.warning("Skipping pool cache update: no valid gold price available")
                return {"status": "skipped", "reason": "no_valid_price"}

            # Convert to serializable format
            pool_data = {
                "balance": status.balance_formatted,
                "balance_raw": status.balance,
                "value_usd": float(status.value_usd),
                "gold_price_usd": final_gold_price,
                "last_distribution": status.last_distribution.isoformat()
                if status.last_distribution
                else None,
                "hours_since_last": status.hours_since_last,
                "ready_to_distribute": status.should_distribute,
                "cached_at": utc_now().isoformat(),
            }

            # Cache the pool status
            await cache.set_pool_status(pool_data)

            logger.debug(f"Pool cache refreshed: balance={status.balance_formatted}, gold_price={final_gold_price}")

            return {"status": "success", "balance": status.balance_formatted, "gold_price": final_gold_price}

    except Exception as e:
        logger.error(f"Failed to refresh pool cache: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.cache_task.warm_cache")
def warm_cache() -> dict:
    """
    Warm up all caches on startup or after cache clear.

    Call this manually or on worker startup to pre-populate caches.
    """
    return run_async(_warm_cache())


async def _warm_cache() -> dict:
    """Async implementation of cache warming."""
    results = {}

    # Refresh leaderboard
    leaderboard_result = await _refresh_leaderboard_cache()
    results["leaderboard"] = leaderboard_result.get("status")

    # Refresh pool
    pool_result = await _refresh_pool_cache()
    results["pool"] = pool_result.get("status")

    logger.info(f"Cache warmed: {results}")
    return {"status": "success", "results": results}

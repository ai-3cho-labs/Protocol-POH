"""
$COPPER Distribution Tasks

Background tasks for checking triggers and executing distributions.
"""

import logging

from app.tasks.celery_app import celery_app
from app.database import get_worker_session_maker
from app.services.distribution import DistributionService, acquire_distribution_lock
from app.utils.async_utils import run_async

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.distribution_task.check_distribution_triggers")
def check_distribution_triggers() -> dict:
    """
    Execute hourly distribution.

    Distributes all GOLD in the pool to eligible holders every hour.
    No threshold or time triggers - just distributes if pool > 0.
    """
    return run_async(_check_distribution_triggers())


async def _check_distribution_triggers() -> dict:
    """
    Async implementation of check_distribution_triggers (hourly distribution).

    Distributes ALL GOLD in pool every hour if pool > 0.
    NO threshold or time triggers - just hourly distribution.
    Uses distribution lock to prevent double payouts.
    """
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        try:
            # Get pool status
            status = await service.get_pool_status()

            logger.info(
                f"Hourly distribution: pool={status.balance_formatted}, "
                f"value=${status.value_usd:.2f}"
            )

            # Skip if pool is empty
            if status.balance <= 0:
                logger.info("Hourly distribution: skipped (pool empty)")
                return {
                    "status": "skipped",
                    "reason": "pool_empty",
                    "pool_balance": status.balance,
                }

            # Acquire distribution lock to prevent double payouts
            if not await acquire_distribution_lock(db, "celery-hourly"):
                logger.info("Hourly distribution: skipped (another worker has lock)")
                return {
                    "status": "skipped",
                    "reason": "locked",
                    "pool_balance": status.balance,
                }

            # Calculate distribution plan (NO threshold check - always distribute if pool > 0)
            plan = await service.calculate_distribution()

            if not plan:
                logger.info("Hourly distribution: skipped (no eligible recipients)")
                await db.commit()  # Release lock
                return {
                    "status": "skipped",
                    "reason": "no_eligible_recipients",
                    "pool_balance": status.balance,
                }

            # Execute distribution
            distribution = await service.execute_distribution(plan)

            if distribution:
                logger.info(
                    f"Hourly distribution: success - "
                    f"{distribution.pool_amount} GOLD to {distribution.recipient_count} recipients"
                )
                return {
                    "status": "success",
                    "distribution_id": str(distribution.id),
                    "pool_amount": distribution.pool_amount,
                    "recipient_count": distribution.recipient_count,
                    "trigger_type": "hourly",
                }
            else:
                return {"status": "failed", "reason": "distribution_error"}

        except Exception as e:
            logger.error(f"Error in hourly distribution: {e}")
            return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.distribution_task.force_distribution")
def force_distribution() -> dict:
    """
    Force a distribution (bypass trigger checks).

    Use for testing or manual triggers.
    """
    return run_async(_force_distribution())


async def _force_distribution() -> dict:
    """Async implementation of force_distribution."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        try:
            # Calculate distribution plan
            plan = await service.calculate_distribution()

            if not plan:
                return {"status": "failed", "reason": "no_eligible_recipients"}

            # Execute
            distribution = await service.execute_distribution(plan)

            if distribution:
                return {
                    "status": "success",
                    "distribution_id": str(distribution.id),
                    "pool_amount": distribution.pool_amount,
                    "recipient_count": distribution.recipient_count,
                    "trigger_type": "manual",
                }
            else:
                return {"status": "failed", "reason": "execution_error"}

        except Exception as e:
            logger.error(f"Error in forced distribution: {e}")
            return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.distribution_task.get_distribution_preview")
def get_distribution_preview() -> dict:
    """
    Get a preview of what the next distribution would look like.

    Does not execute, just calculates shares.
    """
    return run_async(_get_distribution_preview())


async def _get_distribution_preview() -> dict:
    """Async implementation of get_distribution_preview."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        try:
            plan = await service.calculate_distribution()

            if not plan:
                return {"status": "no_distribution", "reason": "no_eligible_recipients"}

            # Return top recipients preview
            top_recipients = [
                {
                    "wallet": r.wallet[:8] + "...",
                    "share_pct": float(r.share_percentage),
                    "amount": r.amount,
                }
                for r in plan.recipients[:10]
            ]

            return {
                "status": "preview",
                "pool_amount": plan.pool_amount,
                "pool_value_usd": float(plan.pool_value_usd),
                "total_hashpower": float(plan.total_hashpower),
                "recipient_count": plan.recipient_count,
                "trigger_type": plan.trigger_type,
                "top_recipients": top_recipients,
            }

        except Exception as e:
            logger.error(f"Error in distribution preview: {e}")
            return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.distribution_task.get_pool_status")
def get_pool_status() -> dict:
    """Get current pool status."""
    return run_async(_get_pool_status())


async def _get_pool_status() -> dict:
    """Async implementation of get_pool_status."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)
        status = await service.get_pool_status()

        return {
            "balance": status.balance_formatted,
            "balance_raw": status.balance,
            "value_usd": float(status.value_usd),
            "last_distribution": status.last_distribution.isoformat()
            if status.last_distribution
            else None,
            "hours_since_last": status.hours_since_last,
            "threshold_met": status.threshold_met,
            "time_trigger_met": status.time_trigger_met,
            "should_distribute": status.should_distribute,
        }


# Allow running as script for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "force":
            result = force_distribution()
        elif sys.argv[1] == "preview":
            result = get_distribution_preview()
        elif sys.argv[1] == "status":
            result = get_pool_status()
        else:
            result = check_distribution_triggers()
    else:
        result = check_distribution_triggers()

    print(f"Result: {result}")

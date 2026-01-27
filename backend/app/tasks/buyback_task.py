"""
$COPPER Buyback Tasks

Background tasks for processing creator rewards and executing buybacks.
"""

import logging
from decimal import Decimal
from typing import Optional

from app.tasks.celery_app import celery_app
from app.database import get_worker_session_maker
from app.services.buyback import BuybackService, process_pending_rewards
from app.utils.async_utils import run_async
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Idempotency key TTL (1 hour) - prevents reprocessing within this window
IDEMPOTENCY_TTL_SECONDS = 3600


async def _check_idempotency(task_id: str) -> bool:
    """
    Check if this task has already been processed (idempotency).

    Uses Redis to track processed task IDs to prevent double-processing
    on Celery retries.

    Returns:
        True if task should proceed, False if already processed.
    """
    if not settings.redis_url:
        # Without Redis, we can't guarantee idempotency - proceed with caution
        logger.warning("Redis not configured - idempotency check skipped")
        return True

    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.redis_url)
        key = f"buyback:processed:{task_id}"

        # Try to set the key with NX (only if not exists)
        was_set = await client.set(key, "1", nx=True, ex=IDEMPOTENCY_TTL_SECONDS)
        await client.aclose()

        if not was_set:
            logger.info(f"Task {task_id} already processed (idempotency check)")
            return False
        return True

    except Exception as e:
        logger.warning(f"Idempotency check failed: {e} - proceeding with task")
        return True


@celery_app.task(bind=True, name="app.tasks.buyback_task.process_creator_rewards")
def process_creator_rewards(self) -> dict:
    """
    Process pending creator rewards.

    Executes 80/20 split:
    - 80% → Jupiter swap SOL → COPPER → Airdrop pool
    - 20% → Team wallet

    Uses idempotency check to prevent double-processing on retries.
    """
    return run_async(_process_creator_rewards(self.request.id))


async def _process_creator_rewards(task_id: Optional[str] = None) -> dict:
    """Async implementation of process_creator_rewards."""
    # Idempotency check to prevent double-processing on retries
    if task_id and not await _check_idempotency(task_id):
        return {"status": "skipped", "reason": "already_processed", "task_id": task_id}

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = BuybackService(db)

        try:
            # Check for pending rewards
            total_pending = await service.get_total_unprocessed_sol()

            if total_pending == 0:
                logger.info("No pending rewards to process")
                return {"status": "skipped", "reason": "no_pending_rewards"}

            # Process rewards
            result = await process_pending_rewards(db)

            if result and result.success:
                return {
                    "status": "success",
                    "sol_spent": float(result.sol_spent),
                    "copper_received": result.copper_received,
                    "tx_signature": result.tx_signature,
                }
            elif result:
                return {"status": "failed", "error": result.error}
            else:
                return {"status": "skipped", "reason": "no_result"}

        except Exception as e:
            logger.error(f"Error processing rewards: {e}")
            return {"status": "error", "error": str(e)}


@celery_app.task(name="app.tasks.buyback_task.record_incoming_reward")
def record_incoming_reward(
    amount_sol: float, source: str, tx_signature: str = None
) -> dict:
    """
    Record an incoming creator reward.

    Called when Pump.fun fees are detected.
    """
    return run_async(_record_incoming_reward(amount_sol, source, tx_signature))


async def _record_incoming_reward(
    amount_sol: float, source: str, tx_signature: str
) -> dict:
    """Async implementation of record_incoming_reward."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = BuybackService(db)

        reward = await service.record_creator_reward(
            Decimal(str(amount_sol)), source, tx_signature
        )

        return {
            "status": "success",
            "reward_id": str(reward.id),
            "amount_sol": amount_sol,
            "source": source,
        }


@celery_app.task(name="app.tasks.buyback_task.get_buyback_stats")
def get_buyback_stats() -> dict:
    """Get buyback statistics."""
    return run_async(_get_buyback_stats())


async def _get_buyback_stats() -> dict:
    """Async implementation of get_buyback_stats."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = BuybackService(db)

        total_sol, total_copper = await service.get_total_buybacks()
        pending_sol = await service.get_total_unprocessed_sol()

        return {
            "total_sol_spent": float(total_sol),
            "total_copper_bought": total_copper,
            "pending_sol": float(pending_sol),
        }


# Allow running as script for testing
if __name__ == "__main__":
    result = process_creator_rewards()
    print(f"Result: {result}")

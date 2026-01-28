"""
$COPPER Snapshot Tasks

Background tasks for balance snapshot collection.
"""

import logging

from app.tasks.celery_app import celery_app
from app.database import get_worker_session_maker
from app.services.snapshot import SnapshotService
from app.utils.async_utils import run_async
from app.websocket import emit_snapshot_taken

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.snapshot_task.take_snapshot")
def take_snapshot() -> dict:
    """
    Take a balance snapshot (always executes).

    Called every 15 minutes for consistent analytics.
    """
    return run_async(_take_snapshot())


async def _take_snapshot() -> dict:
    """Async implementation of take_snapshot."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = SnapshotService(db)

        # Take snapshot (no RNG check)
        snapshot = await service.take_snapshot()

        if snapshot:
            # Emit WebSocket event
            await emit_snapshot_taken(snapshot.created_at)

            logger.info(
                f"Snapshot taken: {snapshot.total_holders} holders, "
                f"supply={snapshot.total_supply}"
            )

            return {
                "status": "success",
                "snapshot_id": str(snapshot.id),
                "holders": snapshot.total_holders,
                "supply": snapshot.total_supply,
            }
        else:
            return {"status": "failed", "reason": "snapshot_error"}


@celery_app.task(name="app.tasks.snapshot_task.maybe_take_snapshot")
def maybe_take_snapshot() -> dict:
    """
    Legacy: Maybe take a balance snapshot (40% probability).

    Deprecated: Use take_snapshot instead. Kept for backwards compatibility.
    """
    return run_async(_maybe_take_snapshot())


async def _maybe_take_snapshot() -> dict:
    """Async implementation of maybe_take_snapshot (legacy)."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = SnapshotService(db)

        # RNG check (legacy behavior)
        if not service.should_take_snapshot():
            logger.info("Snapshot RNG: skipping this hour")
            return {"status": "skipped", "reason": "rng"}

        # Take snapshot
        snapshot = await service.take_snapshot()

        if snapshot:
            # Emit WebSocket event
            await emit_snapshot_taken(snapshot.created_at)

            return {
                "status": "success",
                "snapshot_id": str(snapshot.id),
                "holders": snapshot.total_holders,
                "supply": snapshot.total_supply,
            }
        else:
            return {"status": "failed", "reason": "snapshot_error"}


@celery_app.task(name="app.tasks.snapshot_task.force_snapshot")
def force_snapshot() -> dict:
    """
    Force take a snapshot (bypass RNG).

    Use for testing or manual triggers.
    """
    return run_async(_force_snapshot())


async def _force_snapshot() -> dict:
    """Async implementation of force_snapshot."""
    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = SnapshotService(db)
        snapshot = await service.take_snapshot()

        if snapshot:
            # Emit WebSocket event
            await emit_snapshot_taken(snapshot.created_at)

            return {
                "status": "success",
                "snapshot_id": str(snapshot.id),
                "holders": snapshot.total_holders,
                "supply": snapshot.total_supply,
            }
        else:
            return {"status": "failed", "reason": "snapshot_error"}


# Allow running as script for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "force":
        result = force_snapshot()
    else:
        result = maybe_take_snapshot()

    print(f"Result: {result}")

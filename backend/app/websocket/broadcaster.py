"""
$COPPER WebSocket Broadcaster

Convenience functions for emitting WebSocket events.
All functions are wrapped in try/except to never block service operations.
"""

import logging
from datetime import datetime

from app.websocket.socket_server import sio, GLOBAL_ROOM, WS_NAMESPACES
from app.websocket.events import (
    EventType,
    DistributionExecutedPayload,
    PoolUpdatedPayload,
    LeaderboardUpdatedPayload,
    SnapshotTakenPayload,
    TopRecipient,
)

logger = logging.getLogger(__name__)


async def broadcast_global(event: str, data: dict) -> None:
    """
    Broadcast an event to all connected clients on all namespaces.

    Args:
        event: Event name.
        data: Event payload.
    """
    try:
        # Emit to all supported namespaces
        for ns in WS_NAMESPACES:
            await sio.emit(event, data, room=GLOBAL_ROOM, namespace=ns)
        logger.debug(f"Broadcast to global: {event}")
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed (global): {event} - {e}")


# ============================================================================
# Global Room Event Emitters
# ============================================================================


async def emit_distribution_executed(
    distribution_id: str,
    pool_amount: int,
    pool_value_usd: float,
    recipient_count: int,
    trigger_type: str,
    top_recipients: list[tuple[str, int, int]],  # (wallet, amount, rank)
    executed_at: datetime,
) -> None:
    """
    Emit distribution:executed event to all clients.

    Args:
        distribution_id: ID of the distribution.
        pool_amount: Total pool amount distributed (raw tokens).
        pool_value_usd: Pool value in USD.
        recipient_count: Total number of recipients.
        trigger_type: 'hourly' or 'manual'.
        top_recipients: List of (wallet, amount, rank) tuples for top 5.
        executed_at: When the distribution was executed.
    """
    payload = DistributionExecutedPayload(
        distribution_id=str(distribution_id),
        pool_amount=pool_amount,
        pool_value_usd=float(pool_value_usd),
        recipient_count=recipient_count,
        trigger_type=trigger_type,
        top_recipients=[
            TopRecipient(wallet=w, amount=a, rank=r) for w, a, r in top_recipients
        ],
        executed_at=executed_at.isoformat(),
    )
    await broadcast_global(EventType.DISTRIBUTION_EXECUTED.value, payload.to_dict())


async def emit_pool_updated(
    balance: int,
    value_usd: float,
    ready_to_distribute: bool,
) -> None:
    """
    Emit pool:updated event to all clients.

    Args:
        balance: Current pool balance (raw tokens).
        value_usd: Current pool value in USD.
        ready_to_distribute: Whether the pool has balance to distribute.
    """
    payload = PoolUpdatedPayload(
        balance=balance,
        value_usd=float(value_usd),
        ready_to_distribute=ready_to_distribute,
    )
    await broadcast_global(EventType.POOL_UPDATED.value, payload.to_dict())


async def emit_leaderboard_updated() -> None:
    """
    Emit leaderboard:updated signal to all clients.

    This is a signal-only event - clients should refetch leaderboard data.
    """
    payload = LeaderboardUpdatedPayload()
    await broadcast_global(EventType.LEADERBOARD_UPDATED.value, payload.to_dict())


async def emit_snapshot_taken(snapshot_at: datetime) -> None:
    """
    Emit snapshot:taken event to all clients.

    Args:
        snapshot_at: When the snapshot was taken.
    """
    payload = SnapshotTakenPayload(
        snapshot_at=snapshot_at.isoformat(),
    )
    await broadcast_global(EventType.SNAPSHOT_TAKEN.value, payload.to_dict())

"""
$COPPER WebSocket Broadcaster

Convenience functions for emitting WebSocket events.
All functions are wrapped in try/except to never block service operations.
"""

import logging
from datetime import datetime
from typing import Optional

from app.websocket.socket_server import sio, GLOBAL_ROOM, wallet_room, WS_NAMESPACE
from app.websocket.events import (
    EventType,
    DistributionExecutedPayload,
    PoolUpdatedPayload,
    LeaderboardUpdatedPayload,
    SnapshotTakenPayload,
    TierChangedPayload,
    SellDetectedPayload,
    TopRecipient,
)

logger = logging.getLogger(__name__)


async def broadcast_global(event: str, data: dict) -> None:
    """
    Broadcast an event to all connected clients.

    Args:
        event: Event name.
        data: Event payload.
    """
    try:
        await sio.emit(event, data, room=GLOBAL_ROOM, namespace=WS_NAMESPACE)
        logger.debug(f"Broadcast to global: {event}")
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed (global): {event} - {e}")


async def broadcast_to_wallet(wallet: str, event: str, data: dict) -> None:
    """
    Broadcast an event to clients subscribed to a specific wallet.

    Args:
        wallet: Wallet address.
        event: Event name.
        data: Event payload.
    """
    try:
        room = wallet_room(wallet)
        await sio.emit(event, data, room=room, namespace=WS_NAMESPACE)
        logger.debug(f"Broadcast to wallet {wallet[:8]}...: {event}")
    except Exception as e:
        logger.warning(f"WebSocket broadcast failed (wallet): {event} - {e}")


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
        trigger_type: 'threshold' or 'time'.
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
    progress_to_threshold: float,
    threshold_met: bool,
    hours_until_time_trigger: Optional[float] = None,
) -> None:
    """
    Emit pool:updated event to all clients.

    Args:
        balance: Current pool balance (raw tokens).
        value_usd: Current pool value in USD.
        progress_to_threshold: Progress percentage (0-100).
        threshold_met: Whether the threshold has been met.
        hours_until_time_trigger: Hours until time-based trigger.
    """
    payload = PoolUpdatedPayload(
        balance=balance,
        value_usd=float(value_usd),
        progress_to_threshold=progress_to_threshold,
        threshold_met=threshold_met,
        hours_until_time_trigger=hours_until_time_trigger,
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


# ============================================================================
# Wallet Room Event Emitters
# ============================================================================


async def emit_tier_changed(
    wallet: str,
    old_tier: int,
    new_tier: int,
    new_tier_name: str,
    new_multiplier: float,
    is_upgrade: bool,
) -> None:
    """
    Emit tier:changed event to a specific wallet's room.

    Args:
        wallet: Wallet address.
        old_tier: Previous tier number.
        new_tier: New tier number.
        new_tier_name: Name of the new tier.
        new_multiplier: New tier multiplier.
        is_upgrade: True if upgrade, False if downgrade.
    """
    payload = TierChangedPayload(
        wallet=wallet,
        old_tier=old_tier,
        new_tier=new_tier,
        new_tier_name=new_tier_name,
        new_multiplier=new_multiplier,
        is_upgrade=is_upgrade,
    )
    await broadcast_to_wallet(wallet, EventType.TIER_CHANGED.value, payload.to_dict())


async def emit_sell_detected(
    wallet: str,
    old_tier: int,
    new_tier: int,
    tx_signature: Optional[str] = None,
    amount_sold: Optional[int] = None,
) -> None:
    """
    Emit sell:detected event to a specific wallet's room.

    Args:
        wallet: Wallet address that sold.
        old_tier: Tier before the sell.
        new_tier: Tier after the sell.
        tx_signature: Transaction signature if available.
        amount_sold: Amount sold in raw tokens if available.
    """
    payload = SellDetectedPayload(
        wallet=wallet,
        tx_signature=tx_signature,
        amount_sold=amount_sold,
        old_tier=old_tier,
        new_tier=new_tier,
    )
    await broadcast_to_wallet(wallet, EventType.SELL_DETECTED.value, payload.to_dict())

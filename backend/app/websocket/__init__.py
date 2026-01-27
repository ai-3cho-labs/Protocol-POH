"""
$COPPER WebSocket Package

Real-time updates via Socket.IO with Redis adapter.
"""

# Server and app
from app.websocket.socket_server import (
    sio,
    socket_app,
    setup_redis_adapter,
    connection_tracker,
    GLOBAL_ROOM,
    wallet_room,
    WS_NAMESPACE,
)

# Event types and payloads
from app.websocket.events import (
    EventType,
    TopRecipient,
    DistributionExecutedPayload,
    PoolUpdatedPayload,
    LeaderboardUpdatedPayload,
    SnapshotTakenPayload,
    TierChangedPayload,
    SellDetectedPayload,
)

# Broadcaster functions
from app.websocket.broadcaster import (
    broadcast_global,
    broadcast_to_wallet,
    emit_distribution_executed,
    emit_pool_updated,
    emit_leaderboard_updated,
    emit_snapshot_taken,
    emit_tier_changed,
    emit_sell_detected,
)

# Handlers are registered via decorators in handlers.py
# Import to ensure handlers are registered
from app.websocket import handlers as _handlers  # noqa: F401

__all__ = [
    # Server
    "sio",
    "socket_app",
    "setup_redis_adapter",
    "connection_tracker",
    "GLOBAL_ROOM",
    "wallet_room",
    "WS_NAMESPACE",
    # Event types
    "EventType",
    "TopRecipient",
    "DistributionExecutedPayload",
    "PoolUpdatedPayload",
    "LeaderboardUpdatedPayload",
    "SnapshotTakenPayload",
    "TierChangedPayload",
    "SellDetectedPayload",
    # Broadcasters
    "broadcast_global",
    "broadcast_to_wallet",
    "emit_distribution_executed",
    "emit_pool_updated",
    "emit_leaderboard_updated",
    "emit_snapshot_taken",
    "emit_tier_changed",
    "emit_sell_detected",
]

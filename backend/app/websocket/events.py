"""
$COPPER WebSocket Events

Event types and payload dataclasses for real-time updates.
All payloads include server_timestamp for client-side synchronization.

IMPORTANT: Payload size should not exceed 4KB for optimal performance.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

# Maximum payload size in bytes (4KB as per spec)
MAX_PAYLOAD_SIZE = 4096

# Maximum number of top recipients to include
MAX_TOP_RECIPIENTS = 5


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def iso_timestamp() -> str:
    """Get current UTC time as ISO string."""
    return utc_now().isoformat()


def validate_payload_size(payload: dict, event_name: str) -> dict:
    """
    Validate and potentially truncate payload to fit within size limit.

    Args:
        payload: The payload dict to validate.
        event_name: Name of the event (for logging).

    Returns:
        The payload, potentially with a warning flag if too large.
    """
    try:
        size = len(json.dumps(payload))
        if size > MAX_PAYLOAD_SIZE:
            logger.warning(
                f"WebSocket payload exceeds {MAX_PAYLOAD_SIZE} bytes: "
                f"{event_name} ({size} bytes)"
            )
            # Add truncation flag so client knows data may be incomplete
            payload["_truncated"] = True
    except Exception:
        pass  # Don't fail on serialization issues
    return payload


class EventType(str, Enum):
    """WebSocket event types."""

    # Global room events
    DISTRIBUTION_EXECUTED = "distribution:executed"
    POOL_UPDATED = "pool:updated"
    LEADERBOARD_UPDATED = "leaderboard:updated"
    SNAPSHOT_TAKEN = "snapshot:taken"


@dataclass
class TopRecipient:
    """Top recipient in a distribution."""

    wallet: str  # Full address, frontend truncates
    amount: int  # Raw token amount
    rank: int


@dataclass
class DistributionExecutedPayload:
    """Payload for distribution:executed event."""

    distribution_id: str
    pool_amount: int  # Raw token amount
    pool_value_usd: float
    recipient_count: int
    trigger_type: str  # 'hourly' | 'manual'
    top_recipients: list[TopRecipient]
    executed_at: str  # ISO timestamp
    server_timestamp: str = field(default_factory=iso_timestamp)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        # Limit top recipients to avoid payload bloat
        limited_recipients = self.top_recipients[:MAX_TOP_RECIPIENTS]
        payload = {
            "distribution_id": self.distribution_id,
            "pool_amount": self.pool_amount,
            "pool_value_usd": self.pool_value_usd,
            "recipient_count": self.recipient_count,
            "trigger_type": self.trigger_type,
            "top_recipients": [
                {"wallet": r.wallet, "amount": r.amount, "rank": r.rank}
                for r in limited_recipients
            ],
            "executed_at": self.executed_at,
            "server_timestamp": self.server_timestamp,
        }
        return validate_payload_size(payload, "distribution:executed")


@dataclass
class PoolUpdatedPayload:
    """Payload for pool:updated event."""

    balance: int  # Raw token amount
    value_usd: float
    ready_to_distribute: bool  # True if pool has balance
    server_timestamp: str = field(default_factory=iso_timestamp)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return validate_payload_size(asdict(self), "pool:updated")


@dataclass
class LeaderboardUpdatedPayload:
    """Payload for leaderboard:updated event (signal only)."""

    server_timestamp: str = field(default_factory=iso_timestamp)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        payload = {"server_timestamp": self.server_timestamp}
        return validate_payload_size(payload, "leaderboard:updated")


@dataclass
class SnapshotTakenPayload:
    """Payload for snapshot:taken event."""

    snapshot_at: str  # ISO timestamp of snapshot
    server_timestamp: str = field(default_factory=iso_timestamp)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return validate_payload_size(asdict(self), "snapshot:taken")

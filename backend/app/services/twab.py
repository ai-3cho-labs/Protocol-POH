"""
$COPPER TWAB Service

Time-Weighted Average Balance calculation for fair reward distribution.
TWAB captures holding behavior over time, not just point-in-time balance.

OPTIMIZED: Uses batch queries to avoid N+1 query problems.
"""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass
from collections import defaultdict

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Snapshot, Balance, HoldStreak
from app.config import TIER_CONFIG

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is timezone-aware UTC.

    Handles both naive and aware datetimes from databases that may not
    preserve timezone information consistently.
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it was stored as UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class HashPowerInfo:
    """Complete hash power breakdown for a wallet."""
    wallet: str
    twab: int  # Time-weighted average balance (raw tokens)
    multiplier: float
    hash_power: Decimal  # TWAB × multiplier
    tier: int
    tier_name: str


class TWABService:
    """Service for TWAB and Hash Power calculations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_twab(
        self,
        wallet: str,
        start: datetime,
        end: datetime
    ) -> int:
        """
        Calculate Time-Weighted Average Balance for a single wallet.

        For single wallet queries, use this method.
        For batch calculations, use calculate_all_hash_powers.
        """
        # Get all balances for wallet in time range
        result = await self.db.execute(
            select(Snapshot.timestamp, Balance.balance)
            .join(Balance, Balance.snapshot_id == Snapshot.id)
            .where(and_(
                Balance.wallet == wallet,
                Snapshot.timestamp >= start,
                Snapshot.timestamp <= end
            ))
            .order_by(Snapshot.timestamp.asc())
        )
        balances = [(row[0], row[1]) for row in result.fetchall()]

        return self._compute_twab(balances, start, end)

    def _compute_twab(
        self,
        balances: list[tuple[datetime, int]],
        start: datetime,
        end: datetime
    ) -> int:
        """
        Compute TWAB from balance snapshots.

        TWAB = Σ(balance_i × duration_i) / total_duration

        Uses FORWARD-FILL interpolation: each balance is valid from its
        snapshot time until the next snapshot (or end of period). This is
        fairer than trapezoidal interpolation which penalizes new holders
        by up to 50%.

        For the period BEFORE the first snapshot, we assume zero balance
        (holder hadn't bought yet). This ensures new holders get credit
        for exactly the time they've held, not more.
        """
        if not balances:
            return 0

        # Ensure start/end are timezone-aware for comparison
        start = ensure_utc(start)
        end = ensure_utc(end)

        total_duration = (end - start).total_seconds()
        if total_duration <= 0:
            return 0

        # Handle single balance point - applies from snapshot time to end
        if len(balances) == 1:
            timestamp, balance = balances[0]
            timestamp = ensure_utc(timestamp)
            # Only count time from snapshot to end (when they actually held)
            seg_start = max(timestamp, start)
            seg_end = end
            duration = (seg_end - seg_start).total_seconds()
            if duration <= 0:
                return 0
            # Weight by fraction of period they held
            return int(Decimal(balance) * Decimal(duration) / Decimal(total_duration))

        weighted_sum = Decimal(0)

        # Forward-fill: each balance covers from its timestamp to the next
        for i in range(len(balances)):
            timestamp, balance = balances[i]
            timestamp = ensure_utc(timestamp)

            # Segment starts at this snapshot's timestamp
            seg_start = timestamp

            # Segment ends at next snapshot's timestamp, or end of period
            if i < len(balances) - 1:
                seg_end = ensure_utc(balances[i + 1][0])
            else:
                seg_end = end

            # Clamp to period boundaries
            seg_start = max(seg_start, start)
            seg_end = min(seg_end, end)

            duration = (seg_end - seg_start).total_seconds()
            if duration > 0:
                weighted_sum += Decimal(balance) * Decimal(duration)

        twab = weighted_sum / Decimal(total_duration)
        return int(twab)

    async def calculate_hash_power(
        self,
        wallet: str,
        start: datetime,
        end: datetime
    ) -> HashPowerInfo:
        """
        Calculate Hash Power for a single wallet.

        Hash Power = TWAB × Streak Multiplier
        """
        twab = await self.calculate_twab(wallet, start, end)

        # Get streak info
        result = await self.db.execute(
            select(HoldStreak).where(HoldStreak.wallet == wallet)
        )
        streak = result.scalar_one_or_none()

        if streak:
            tier = streak.current_tier
            multiplier = TIER_CONFIG[tier]["multiplier"]
            tier_name = TIER_CONFIG[tier]["name"]
        else:
            tier = 1
            multiplier = 1.0
            tier_name = "Ore"

        hash_power = Decimal(twab) * Decimal(str(multiplier))

        return HashPowerInfo(
            wallet=wallet,
            twab=twab,
            multiplier=multiplier,
            hash_power=hash_power,
            tier=tier,
            tier_name=tier_name
        )

    async def calculate_all_hash_powers(
        self,
        start: datetime,
        end: datetime,
        min_balance: int = 0,
        limit: Optional[int] = None
    ) -> list[HashPowerInfo]:
        """
        Calculate hash power for all eligible wallets using ATOMIC batch query.

        OPTIMIZED: Uses single JOIN query to prevent sell-timing gaming.
        Previously used 2 separate queries, creating a race window where
        a sell between queries could result in inconsistent tier data.

        Args:
            start: Start of period.
            end: End of period.
            min_balance: Minimum TWAB to include (filters dust).
            limit: Optional limit on results (for leaderboard).

        Returns:
            List of HashPowerInfo sorted by hash power descending.
        """
        # ATOMIC QUERY: Get ALL balances WITH tiers in single query
        # This prevents sell-timing gaming where a sell between separate
        # balance/tier queries could manipulate the distribution denominator.
        # Using LEFT OUTER JOIN so wallets without streaks still get included.
        result = await self.db.execute(
            select(
                Balance.wallet,
                Snapshot.timestamp,
                Balance.balance,
                HoldStreak.current_tier
            )
            .join(Snapshot, Balance.snapshot_id == Snapshot.id)
            .outerjoin(HoldStreak, Balance.wallet == HoldStreak.wallet)
            .where(and_(
                Snapshot.timestamp >= start,
                Snapshot.timestamp <= end
            ))
            .order_by(Balance.wallet, Snapshot.timestamp.asc())
        )
        all_data = result.fetchall()

        if not all_data:
            return []

        # Group balances by wallet, also capture tier (same for all rows per wallet)
        wallet_balances: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
        wallet_tiers: dict[str, int] = {}

        for wallet, timestamp, balance, tier in all_data:
            wallet_balances[wallet].append((timestamp, balance))
            # Tier is the same for all rows of a wallet, just capture first occurrence
            if wallet not in wallet_tiers:
                wallet_tiers[wallet] = tier if tier is not None else 1

        logger.info(f"Batch TWAB: {len(wallet_balances)} wallets, {len(all_data)} balance records")

        # Calculate hash powers (CPU-bound, no DB)
        hash_powers = []
        for wallet, balances in wallet_balances.items():
            # Compute TWAB
            twab = self._compute_twab(balances, start, end)

            # Filter by minimum balance
            if twab < min_balance:
                continue

            # Get tier/multiplier (already snapshotted atomically with balances)
            tier = wallet_tiers.get(wallet, 1)
            multiplier = TIER_CONFIG[tier]["multiplier"]
            tier_name = TIER_CONFIG[tier]["name"]

            # Calculate hash power
            hash_power = Decimal(twab) * Decimal(str(multiplier))

            hash_powers.append(HashPowerInfo(
                wallet=wallet,
                twab=twab,
                multiplier=multiplier,
                hash_power=hash_power,
                tier=tier,
                tier_name=tier_name
            ))

        # Sort by hash power descending
        hash_powers.sort(key=lambda x: x.hash_power, reverse=True)

        # Apply limit if specified
        if limit:
            hash_powers = hash_powers[:limit]

        return hash_powers

    async def get_total_hash_power(
        self,
        start: datetime,
        end: datetime,
        min_balance: int = 0
    ) -> Decimal:
        """
        Calculate total hash power across all eligible wallets.
        """
        hash_powers = await self.calculate_all_hash_powers(start, end, min_balance)
        return sum(hp.hash_power for hp in hash_powers)

    async def get_leaderboard(
        self,
        limit: int = 10,
        hours: int = 24
    ) -> list[HashPowerInfo]:
        """
        Get top wallets by hash power.

        Uses optimized batch query.
        """
        end = utc_now()
        start = end - timedelta(hours=hours)

        return await self.calculate_all_hash_powers(start, end, limit=limit)

    async def get_wallet_rank(
        self,
        wallet: str,
        hours: int = 24
    ) -> Optional[int]:
        """
        Get a wallet's rank on the leaderboard.

        Note: For large datasets, consider caching leaderboard.
        """
        end = utc_now()
        start = end - timedelta(hours=hours)

        # Get all hash powers (consider caching this)
        hash_powers = await self.calculate_all_hash_powers(start, end)

        for i, hp in enumerate(hash_powers):
            if hp.wallet == wallet:
                return i + 1

        return None

    async def estimate_reward_share(
        self,
        wallet: str,
        pool_amount: int,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> tuple[int, Decimal]:
        """
        Estimate a wallet's share of a distribution pool.

        Returns:
            Tuple of (estimated_amount, share_percentage).
        """
        if end is None:
            end = utc_now()
        if start is None:
            start = end - timedelta(hours=24)

        # Get wallet's hash power
        hp_info = await self.calculate_hash_power(wallet, start, end)

        # Get total hash power
        total_hp = await self.get_total_hash_power(start, end)

        if total_hp == 0:
            return 0, Decimal(0)

        share = hp_info.hash_power / total_hp
        estimated_amount = int(Decimal(pool_amount) * share)

        return estimated_amount, share * 100

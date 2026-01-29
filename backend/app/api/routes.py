"""
$COPPER API Routes

REST API endpoints for the mining dashboard.
"""

import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.database import get_db
from app.services.snapshot import SnapshotService
from app.services.distribution import DistributionService
from app.config import TOKEN_MULTIPLIER, GOLD_MULTIPLIER, get_settings

settings = get_settings()
from app.utils.rate_limiter import limiter

router = APIRouter(prefix="/api", tags=["api"])


# ===========================================
# Validation
# ===========================================

# Solana wallet address: 32-44 base58 characters
WALLET_REGEX = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


def validate_wallet_address(wallet: str) -> str:
    """Validate Solana wallet address format."""
    if not wallet or not WALLET_REGEX.match(wallet):
        raise HTTPException(
            status_code=400,
            detail="Invalid wallet address format. Must be 32-44 base58 characters.",
        )
    return wallet


# Type alias for validated wallet parameter
ValidatedWallet = Annotated[
    str,
    Path(
        min_length=32,
        max_length=44,
        pattern=r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
        description="Solana wallet address (base58)",
    ),
]


# ===========================================
# Response Models
# ===========================================


class GlobalStatsResponse(BaseModel):
    """Global system statistics."""

    total_holders: int
    total_volume_24h: float
    total_buybacks_sol: float
    total_distributed: float
    last_snapshot_at: Optional[datetime]
    last_distribution_at: Optional[datetime]


class UserStatsResponse(BaseModel):
    """User mining statistics."""

    wallet: str
    balance: float  # Token balance
    balance_raw: int
    rank: Optional[int]
    pending_reward_estimate: float
    pool_share_percent: float
    is_new_holder: bool = False


class DistributionHistoryItem(BaseModel):
    """Distribution history item."""

    distribution_id: str
    executed_at: datetime
    balance: float  # User's balance at distribution time
    share_percent: float
    amount_received: float
    tx_signature: Optional[str]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""

    rank: int
    wallet: str
    wallet_short: str
    total_earned: float


class PoolStatusResponse(BaseModel):
    """Reward pool status."""

    balance: float
    balance_raw: int
    value_usd: float
    gold_price_usd: float  # Current GOLD token price
    last_distribution: Optional[datetime]
    hours_since_last: Optional[float]
    ready_to_distribute: bool  # True if pool has balance


class DistributionItem(BaseModel):
    """Distribution record."""

    id: str
    pool_amount: float
    pool_value_usd: Optional[float]
    total_supply: float
    recipient_count: int
    trigger_type: str
    executed_at: datetime


# ===========================================
# Helper Functions
# ===========================================


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def format_wallet(wallet: str) -> str:
    """Shorten wallet address for display."""
    if len(wallet) < 12:
        return wallet
    return f"{wallet[:4]}...{wallet[-4:]}"


# ===========================================
# Endpoints
# ===========================================


@router.get("/stats", response_model=GlobalStatsResponse)
@limiter.limit("60/minute")
async def get_global_stats(request: Request, db: AsyncSession = Depends(get_db)):
    """Get global system statistics."""
    from app.models import SystemStats

    result = await db.execute(select(SystemStats).where(SystemStats.id == 1))
    stats = result.scalar_one_or_none()

    if not stats:
        return GlobalStatsResponse(
            total_holders=0,
            total_volume_24h=0,
            total_buybacks_sol=0,
            total_distributed=0,
            last_snapshot_at=None,
            last_distribution_at=None,
        )

    return GlobalStatsResponse(
        total_holders=stats.total_holders or 0,
        total_volume_24h=float(stats.total_volume_24h or 0),
        total_buybacks_sol=float(stats.total_buybacks or 0),
        total_distributed=float(
            Decimal(stats.total_distributed or 0) / GOLD_MULTIPLIER
        ),
        last_snapshot_at=stats.last_snapshot_at,
        last_distribution_at=stats.last_distribution_at,
    )


@router.get("/user/{wallet}", response_model=UserStatsResponse)
@limiter.limit("30/minute")
async def get_user_stats(
    request: Request, wallet: ValidatedWallet, db: AsyncSession = Depends(get_db)
):
    """Get mining statistics for a specific wallet."""
    from app.utils.cache import get_cache_service

    cache = get_cache_service()

    # Additional validation
    validate_wallet_address(wallet)

    # Test mode: return mock user data
    if settings.test_mode:
        pool_balance = settings.test_pool_balance
        pending = pool_balance * (settings.test_user_share_percent / 100)
        return UserStatsResponse(
            wallet=wallet,
            balance=settings.test_user_balance,
            balance_raw=int(settings.test_user_balance * TOKEN_MULTIPLIER),
            rank=42,
            pending_reward_estimate=pending,
            pool_share_percent=settings.test_user_share_percent,
            is_new_holder=False,
        )

    distribution_service = DistributionService(db)

    # Get current balance from latest snapshot
    snapshot_service = SnapshotService(db)
    latest_snapshot = await snapshot_service.get_latest_snapshot()

    balance_raw = 0
    if latest_snapshot:
        from app.models import Balance

        result = await db.execute(
            select(Balance.balance).where(
                and_(
                    Balance.snapshot_id == latest_snapshot.id, Balance.wallet == wallet
                )
            )
        )
        balance_raw = result.scalar_one_or_none() or 0

    # Get rank from cached leaderboard (fast) with fallback to computation
    rank = None
    cached_leaderboard = await cache.get_leaderboard()
    if cached_leaderboard:
        for entry in cached_leaderboard:
            if entry["wallet"] == wallet:
                rank = entry["rank"]
                break

    # Determine if this is a new holder
    is_new_holder = balance_raw == 0

    # Estimate pending reward - use cached pool status and leaderboard for speed
    cached_pool = await cache.get_pool_status()
    if cached_pool:
        pool_balance = cached_pool.get("balance_raw", 0)
    else:
        pool_status = await distribution_service.get_pool_status()
        pool_balance = pool_status.balance

    pending_estimate = 0.0
    pool_share_percent = 0.0

    if pool_balance > 0 and balance_raw > 0:
        # Calculate total supply from leaderboard cache
        total_supply = 0
        if cached_leaderboard:
            total_supply = sum(int(e.get("balance", 0)) for e in cached_leaderboard)

        if total_supply > 0:
            share_ratio = balance_raw / total_supply
            pool_share_percent = share_ratio * 100
            pending_estimate = float(
                Decimal(pool_balance) * Decimal(str(share_ratio)) / GOLD_MULTIPLIER
            )

    return UserStatsResponse(
        wallet=wallet,
        balance=float(Decimal(balance_raw) / TOKEN_MULTIPLIER),
        balance_raw=balance_raw,
        rank=rank,
        pending_reward_estimate=pending_estimate,
        pool_share_percent=pool_share_percent,
        is_new_holder=is_new_holder,
    )


@router.get("/user/{wallet}/history", response_model=list[DistributionHistoryItem])
@limiter.limit("30/minute")
async def get_user_history(
    request: Request,
    wallet: ValidatedWallet,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get distribution history for a wallet."""
    validate_wallet_address(wallet)

    distribution_service = DistributionService(db)
    recipients = await distribution_service.get_wallet_distributions(wallet, limit)

    return [
        DistributionHistoryItem(
            distribution_id=str(r.distribution_id),
            executed_at=r.distribution.executed_at if r.distribution else utc_now(),
            balance=float(Decimal(r.balance) / TOKEN_MULTIPLIER),
            share_percent=float(
                Decimal(r.balance) / Decimal(r.distribution.total_supply) * 100
                if r.distribution and r.distribution.total_supply > 0
                else 0
            ),
            amount_received=float(Decimal(r.amount_received) / GOLD_MULTIPLIER),
            tx_signature=r.tx_signature,
        )
        for r in recipients
    ]


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
@limiter.limit("60/minute")
async def get_leaderboard(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get top earners by total GOLD received (cached)."""
    from app.utils.cache import get_cache_service

    cache = get_cache_service()

    # Try cache first
    cached = await cache.get_leaderboard()
    if cached and "total_earned" in cached[0]:
        # Return from cache (slice to requested limit)
        return [
            LeaderboardEntry(
                rank=entry["rank"],
                wallet=entry["wallet"],
                wallet_short=format_wallet(entry["wallet"]),
                total_earned=float(Decimal(entry["total_earned"]) / GOLD_MULTIPLIER),
            )
            for entry in cached[:limit]
        ]

    from app.models import DistributionRecipient, ExcludedWallet

    # Get excluded wallets
    excluded_result = await db.execute(select(ExcludedWallet.wallet))
    excluded = {w for (w,) in excluded_result.all()}

    # Get top earners by total amount received across all distributions
    total_earned = func.sum(DistributionRecipient.amount_received).label(
        "total_earned"
    )
    result = await db.execute(
        select(DistributionRecipient.wallet, total_earned)
        .group_by(DistributionRecipient.wallet)
        .order_by(total_earned.desc())
        .limit(100)
    )
    earners = [(w, e) for w, e in result.all() if w not in excluded and e > 0]

    # Cache for next time
    leaderboard_data = [
        {
            "rank": i + 1,
            "wallet": w,
            "total_earned": e,
        }
        for i, (w, e) in enumerate(earners)
    ]
    await cache.set_leaderboard(leaderboard_data)

    return [
        LeaderboardEntry(
            rank=i + 1,
            wallet=w,
            wallet_short=format_wallet(w),
            total_earned=float(Decimal(e) / GOLD_MULTIPLIER),
        )
        for i, (w, e) in enumerate(earners[:limit])
    ]


@router.get("/pool", response_model=PoolStatusResponse)
@limiter.limit("120/minute")
async def get_pool_status(request: Request, db: AsyncSession = Depends(get_db)):
    """Get reward pool status (cached)."""
    from app.utils.cache import get_cache_service
    from app.utils.price_cache import get_gold_price_usd

    cache = get_cache_service()

    # Try cache first, but only if it has valid gold_price_usd
    cached = await cache.get_pool_status()
    cached_gold_price = cached.get("gold_price_usd", 0) if cached else 0
    if cached and cached_gold_price > 0:
        return PoolStatusResponse(
            balance=cached["balance"],
            balance_raw=cached["balance_raw"],
            value_usd=cached["value_usd"],
            gold_price_usd=cached_gold_price,
            last_distribution=datetime.fromisoformat(cached["last_distribution"])
            if cached.get("last_distribution")
            else None,
            hours_since_last=cached["hours_since_last"],
            ready_to_distribute=cached["ready_to_distribute"],
        )

    # Cache miss - compute and cache
    distribution_service = DistributionService(db)
    status = await distribution_service.get_pool_status()
    gold_price = await get_gold_price_usd()

    # Ensure we have a valid gold price (fallback to a reasonable default if API fails)
    final_gold_price = float(gold_price) if gold_price > 0 else 0.0

    # Cache for next time
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
    }
    await cache.set_pool_status(pool_data)

    return PoolStatusResponse(
        balance=status.balance_formatted,
        balance_raw=status.balance,
        value_usd=float(status.value_usd),
        gold_price_usd=final_gold_price,
        last_distribution=status.last_distribution,
        hours_since_last=status.hours_since_last,
        ready_to_distribute=status.should_distribute,
    )


@router.get("/distributions", response_model=list[DistributionItem])
@limiter.limit("30/minute")
async def get_distributions(
    request: Request,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get recent mining reward payouts."""
    distribution_service = DistributionService(db)

    distributions = await distribution_service.get_recent_distributions(limit)

    return [
        DistributionItem(
            id=str(d.id),
            pool_amount=float(Decimal(d.pool_amount) / GOLD_MULTIPLIER),
            pool_value_usd=float(d.pool_value_usd) if d.pool_value_usd else None,
            total_supply=float(Decimal(d.total_supply) / TOKEN_MULTIPLIER),
            recipient_count=d.recipient_count,
            trigger_type=d.trigger_type,
            executed_at=d.executed_at,
        )
        for d in distributions
    ]

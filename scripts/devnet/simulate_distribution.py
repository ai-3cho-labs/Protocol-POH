#!/usr/bin/env python3
"""
Standalone Distribution Simulation

Simulates a distribution calculation using local SQLite test data.
This script is self-contained and doesn't depend on the app's database module.

Usage:
    python scripts/devnet/simulate_distribution.py [pool_amount]

Example:
    python scripts/devnet/simulate_distribution.py 500000
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select, func, Column, String, Integer, BigInteger, DateTime, Numeric, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Configuration
DB_PATH = Path(__file__).parent.parent.parent / "backend" / "test_devnet.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"
TOKEN_DECIMALS = 9
TOKEN_MULTIPLIER = 10 ** TOKEN_DECIMALS

# Tier configuration (from SPEC.md)
TIER_CONFIG = {
    1: {"name": "Ore", "multiplier": 1.0},
    2: {"name": "Raw Copper", "multiplier": 1.25},
    3: {"name": "Refined", "multiplier": 1.5},
    4: {"name": "Industrial", "multiplier": 2.5},
    5: {"name": "Master Miner", "multiplier": 3.5},
    6: {"name": "Diamond Hands", "multiplier": 5.0},
}

Base = declarative_base()


# SQLite-compatible models
class Snapshot(Base):
    __tablename__ = "snapshots"
    id = Column(Text, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    snapshot_at = Column(DateTime, nullable=False)
    total_holders = Column(Integer, nullable=False)
    total_supply = Column(BigInteger, nullable=False)
    created_at = Column(DateTime)


class Balance(Base):
    __tablename__ = "balances"
    id = Column(Text, primary_key=True)
    snapshot_id = Column(Text)
    wallet = Column(String(44), nullable=False)
    wallet_address = Column(String(44), nullable=False)
    balance = Column(BigInteger, nullable=False)


class HoldStreak(Base):
    __tablename__ = "hold_streaks"
    wallet = Column(String(44), primary_key=True)
    streak_start = Column(DateTime, nullable=False)
    current_tier = Column(Integer, nullable=False, default=1)
    last_sell_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime)


class Distribution(Base):
    __tablename__ = "distributions"
    id = Column(Text, primary_key=True)
    pool_amount = Column(BigInteger, nullable=False)
    pool_value_usd = Column(Numeric(18, 2), nullable=True)
    total_hashpower = Column(Numeric(24, 2), nullable=False)
    recipient_count = Column(Integer, nullable=False)
    trigger_type = Column(String(20), nullable=False)
    executed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime)


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


async def simulate_distribution(pool_amount_tokens: float):
    """
    Simulate a distribution calculation.

    Args:
        pool_amount_tokens: Pool amount in whole tokens (e.g., 500000)
    """
    print(f"\n{'='*60}")
    print(f"  DISTRIBUTION SIMULATION")
    print(f"{'='*60}\n")

    # Check database exists
    if not DB_PATH.exists():
        print(f"  ERROR: Database not found at {DB_PATH}")
        print(f"  Run setup_local_db.py first:")
        print(f"    python scripts/devnet/setup_local_db.py")
        return

    pool_amount = int(pool_amount_tokens * TOKEN_MULTIPLIER)

    # Connect to database
    engine = create_async_engine(DB_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get distribution time window
        result = await session.execute(
            select(Distribution)
            .order_by(Distribution.executed_at.desc())
            .limit(1)
        )
        last_dist = result.scalar_one_or_none()

        end = utc_now()
        if last_dist:
            start = last_dist.executed_at
            if hasattr(start, 'replace') and start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
        else:
            start = end - timedelta(hours=24)

        print(f"  Pool Amount:     {pool_amount_tokens:,.0f} tokens")
        print(f"  Pool (raw):      {pool_amount:,}")
        print(f"  Period Start:    {start}")
        print(f"  Period End:      {end}")

        # Get snapshots in time window
        result = await session.execute(
            select(Snapshot)
            .where(Snapshot.snapshot_at >= start)
            .where(Snapshot.snapshot_at <= end)
            .order_by(Snapshot.snapshot_at)
        )
        snapshots = result.scalars().all()

        if len(snapshots) < 2:
            print(f"\n  ERROR: Need at least 2 snapshots for TWAB calculation")
            print(f"  Found: {len(snapshots)} snapshots")
            print(f"  Run setup_local_db.py to create test data")
            return

        print(f"  Snapshots:       {len(snapshots)}")

        # Get snapshot IDs
        snapshot_ids = [s.id for s in snapshots]

        # Calculate TWAB for each wallet (simple average of balances)
        result = await session.execute(
            select(
                Balance.wallet,
                func.avg(Balance.balance).label("avg_balance")
            )
            .where(Balance.snapshot_id.in_(snapshot_ids))
            .group_by(Balance.wallet)
        )
        avg_balances = {row.wallet: float(row.avg_balance) for row in result.fetchall()}

        if not avg_balances:
            print(f"\n  ERROR: No holder balances found in snapshots")
            return

        # Get hold streaks for multipliers
        result = await session.execute(select(HoldStreak))
        streaks = {s.wallet: s for s in result.scalars().all()}

        # Calculate hash powers
        hash_powers = []
        for wallet, twab in avg_balances.items():
            streak = streaks.get(wallet)
            tier = streak.current_tier if streak else 1
            multiplier = TIER_CONFIG.get(tier, TIER_CONFIG[1])["multiplier"]
            hash_power = Decimal(str(twab)) * Decimal(str(multiplier))

            if hash_power > 0:
                hash_powers.append({
                    "wallet": wallet,
                    "twab": int(twab),
                    "tier": tier,
                    "tier_name": TIER_CONFIG.get(tier, TIER_CONFIG[1])["name"],
                    "multiplier": multiplier,
                    "hash_power": hash_power,
                })

        if not hash_powers:
            print(f"\n  ERROR: No wallets with hash power > 0")
            return

        # Sort by hash power (descending)
        hash_powers.sort(key=lambda x: x["hash_power"], reverse=True)
        total_hp = sum(hp["hash_power"] for hp in hash_powers)

        # Calculate distribution shares
        recipients = []
        total_distributed = 0

        for hp in hash_powers:
            share_pct = hp["hash_power"] / total_hp
            amount = int(Decimal(pool_amount) * share_pct)
            total_distributed += amount

            if amount > 0:
                recipients.append({
                    **hp,
                    "share_pct": float(share_pct * 100),
                    "amount": amount,
                    "amount_tokens": amount / TOKEN_MULTIPLIER,
                })

        # Handle remainder (dust) - distribute to largest holders
        remainder = pool_amount - total_distributed
        if remainder > 0 and recipients:
            recipients[0]["amount"] += remainder
            recipients[0]["amount_tokens"] = recipients[0]["amount"] / TOKEN_MULTIPLIER
            total_distributed += remainder

        # Print results
        print(f"\n  {'='*56}")
        print(f"  DISTRIBUTION CALCULATION RESULTS")
        print(f"  {'='*56}\n")

        print(f"  Total Hash Power: {total_hp:,.2f}")
        print(f"  Recipients:       {len(recipients)}")
        print(f"  Total Distributed: {total_distributed / TOKEN_MULTIPLIER:,.2f} tokens")

        print(f"\n  {'#':<3} {'Wallet':<20} {'TWAB':>12} {'Tier':<14} {'Mult':>5} {'Share':>8} {'Amount':>14}")
        print(f"  {'-'*3} {'-'*20} {'-'*12} {'-'*14} {'-'*5} {'-'*8} {'-'*14}")

        for i, r in enumerate(recipients, 1):
            twab_fmt = f"{r['twab'] / TOKEN_MULTIPLIER:,.0f}"
            print(
                f"  {i:<3} "
                f"{r['wallet'][:20]:<20} "
                f"{twab_fmt:>12} "
                f"{r['tier_name']:<14} "
                f"{r['multiplier']:>4}x "
                f"{r['share_pct']:>7.2f}% "
                f"{r['amount_tokens']:>13,.2f}"
            )

        # Summary
        print(f"\n  {'='*56}")
        print(f"  SUMMARY")
        print(f"  {'='*56}\n")

        print(f"  Pool Amount:       {pool_amount_tokens:>15,.2f} tokens")
        print(f"  Total Distributed: {total_distributed / TOKEN_MULTIPLIER:>15,.2f} tokens")
        print(f"  Remainder (dust):  {remainder / TOKEN_MULTIPLIER:>15,.6f} tokens")
        print(f"  Recipients:        {len(recipients):>15}")

        # Verification
        verification_total = sum(r["amount"] for r in recipients)
        print(f"\n  Verification:")
        print(f"    Sum of amounts:  {verification_total / TOKEN_MULTIPLIER:>15,.2f} tokens")
        print(f"    Matches pool:    {'YES' if verification_total == pool_amount else 'NO'}")

    await engine.dispose()

    print(f"\n  {'='*56}")
    print(f"  SIMULATION COMPLETE")
    print(f"  {'='*56}\n")


async def main():
    # Default pool amount
    pool_amount = 500_000

    if len(sys.argv) > 1:
        try:
            pool_amount = float(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [pool_amount]")
            print(f"  pool_amount: Amount in whole tokens (default: 500000)")
            return

    await simulate_distribution(pool_amount)


if __name__ == "__main__":
    asyncio.run(main())

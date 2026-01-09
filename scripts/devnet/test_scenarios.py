#!/usr/bin/env python3
"""
Distribution Test Scenarios

Tests various edge cases and scenarios for the distribution system.

Usage:
    python scripts/devnet/test_scenarios.py
"""

import asyncio
import uuid
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy import select, func, Column, String, Integer, BigInteger, DateTime, Numeric, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Configuration
DB_PATH = Path(__file__).parent.parent.parent / "backend" / "test_scenarios.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"
TOKEN_DECIMALS = 9
TOKEN_MULTIPLIER = 10 ** TOKEN_DECIMALS

# Tier configuration
TIER_CONFIG = {
    1: {"name": "Ore", "multiplier": 1.0},
    2: {"name": "Raw Copper", "multiplier": 1.25},
    3: {"name": "Refined", "multiplier": 1.5},
    4: {"name": "Industrial", "multiplier": 2.5},
    5: {"name": "Master Miner", "multiplier": 3.5},
    6: {"name": "Diamond Hands", "multiplier": 5.0},
}

Base = declarative_base()


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


class DistributionLock(Base):
    __tablename__ = "distribution_lock"
    id = Column(Integer, primary_key=True, default=1)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_wallet(index: int) -> str:
    """Generate a fake wallet address."""
    import hashlib
    hash_input = f"TestWallet{index:06d}".encode()
    hash_bytes = hashlib.sha256(hash_input).digest()
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    result = ""
    num = int.from_bytes(hash_bytes[:32], "big")
    while len(result) < 44:
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result
    return result[:44]


async def setup_scenario(
    engine,
    holders: List[Dict[str, Any]],
    scenario_name: str
) -> None:
    """Set up database with specific holder configuration."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        now = utc_now()

        # Create snapshots
        snapshot_times = [
            now - timedelta(hours=12),
            now - timedelta(hours=6),
            now - timedelta(hours=1),
        ]

        total_supply = sum(h["balance"] for h in holders) * TOKEN_MULTIPLIER
        snapshots = []

        for snap_time in snapshot_times:
            snapshot = Snapshot(
                id=str(uuid.uuid4()),
                timestamp=snap_time,
                snapshot_at=snap_time,
                total_holders=len(holders),
                total_supply=total_supply,
                created_at=snap_time,
            )
            session.add(snapshot)
            snapshots.append(snapshot)

        await session.flush()

        # Create balances and streaks
        for i, holder in enumerate(holders):
            wallet = generate_wallet(i)
            holder["wallet"] = wallet

            for snapshot in snapshots:
                balance = Balance(
                    id=str(uuid.uuid4()),
                    snapshot_id=snapshot.id,
                    wallet=wallet,
                    wallet_address=wallet,
                    balance=holder["balance"] * TOKEN_MULTIPLIER,
                )
                session.add(balance)

            streak = HoldStreak(
                wallet=wallet,
                streak_start=now - timedelta(days=holder.get("days_held", 1)),
                current_tier=holder["tier"],
                last_sell_at=None,
                updated_at=now,
            )
            session.add(streak)

        # Distribution lock
        lock = DistributionLock(id=1)
        session.add(lock)

        await session.commit()


async def run_distribution(engine, pool_amount_tokens: float) -> Dict[str, Any]:
    """Run distribution calculation and return results."""
    pool_amount = int(pool_amount_tokens * TOKEN_MULTIPLIER)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get snapshots
        result = await session.execute(
            select(Snapshot).order_by(Snapshot.snapshot_at)
        )
        snapshots = result.scalars().all()
        snapshot_ids = [s.id for s in snapshots]

        # Calculate TWAB
        result = await session.execute(
            select(
                Balance.wallet,
                func.avg(Balance.balance).label("avg_balance")
            )
            .where(Balance.snapshot_id.in_(snapshot_ids))
            .group_by(Balance.wallet)
        )
        avg_balances = {row.wallet: float(row.avg_balance) for row in result.fetchall()}

        # Get streaks
        result = await session.execute(select(HoldStreak))
        streaks = {s.wallet: s for s in result.scalars().all()}

        # Calculate hash powers
        recipients = []
        for wallet, twab in avg_balances.items():
            streak = streaks.get(wallet)
            tier = streak.current_tier if streak else 1
            multiplier = TIER_CONFIG.get(tier, TIER_CONFIG[1])["multiplier"]
            hash_power = Decimal(str(twab)) * Decimal(str(multiplier))

            if hash_power > 0:
                recipients.append({
                    "wallet": wallet,
                    "twab": int(twab),
                    "tier": tier,
                    "multiplier": multiplier,
                    "hash_power": hash_power,
                })

        if not recipients:
            return {"error": "No recipients", "recipients": []}

        # Sort and calculate shares
        recipients.sort(key=lambda x: x["hash_power"], reverse=True)
        total_hp = sum(r["hash_power"] for r in recipients)

        total_distributed = 0
        for r in recipients:
            share_pct = r["hash_power"] / total_hp
            amount = int(Decimal(pool_amount) * share_pct)
            r["share_pct"] = float(share_pct * 100)
            r["amount"] = amount
            r["amount_tokens"] = amount / TOKEN_MULTIPLIER
            total_distributed += amount

        # Handle remainder
        remainder = pool_amount - total_distributed
        if remainder > 0 and recipients:
            recipients[0]["amount"] += remainder
            recipients[0]["amount_tokens"] = recipients[0]["amount"] / TOKEN_MULTIPLIER
            total_distributed += remainder

        return {
            "pool_amount": pool_amount_tokens,
            "total_hp": float(total_hp),
            "recipient_count": len(recipients),
            "total_distributed": total_distributed / TOKEN_MULTIPLIER,
            "remainder": remainder / TOKEN_MULTIPLIER,
            "recipients": recipients,
            "verified": abs(total_distributed - pool_amount) < 1,
        }


def print_scenario_result(name: str, result: Dict[str, Any], show_all: bool = False):
    """Print scenario results."""
    print(f"\n{'='*70}")
    print(f"  SCENARIO: {name}")
    print(f"{'='*70}")

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return

    print(f"\n  Pool: {result['pool_amount']:,.0f} tokens")
    print(f"  Recipients: {result['recipient_count']}")
    print(f"  Total Distributed: {result['total_distributed']:,.2f} tokens")
    print(f"  Remainder (dust): {result['remainder']:.6f} tokens")
    print(f"  Verified: {'PASS' if result['verified'] else 'FAIL'}")

    # Show recipients
    recipients = result["recipients"]
    show_count = len(recipients) if show_all or len(recipients) <= 10 else 5

    print(f"\n  {'#':<3} {'Wallet':<15} {'Balance':>12} {'Tier':<12} {'Mult':>5} {'Share':>8} {'Amount':>12}")
    print(f"  {'-'*3} {'-'*15} {'-'*12} {'-'*12} {'-'*5} {'-'*8} {'-'*12}")

    for i, r in enumerate(recipients[:show_count], 1):
        tier_name = TIER_CONFIG[r["tier"]]["name"]
        print(
            f"  {i:<3} "
            f"{r['wallet'][:15]:<15} "
            f"{r['twab']/TOKEN_MULTIPLIER:>11,.0f} "
            f"{tier_name:<12} "
            f"{r['multiplier']:>4}x "
            f"{r['share_pct']:>7.2f}% "
            f"{r['amount_tokens']:>11,.2f}"
        )

    if len(recipients) > show_count:
        print(f"  ... and {len(recipients) - show_count} more recipients")

        # Show last recipient
        last = recipients[-1]
        tier_name = TIER_CONFIG[last["tier"]]["name"]
        print(f"\n  Last recipient:")
        print(
            f"  {len(recipients):<3} "
            f"{last['wallet'][:15]:<15} "
            f"{last['twab']/TOKEN_MULTIPLIER:>11,.0f} "
            f"{tier_name:<12} "
            f"{last['multiplier']:>4}x "
            f"{last['share_pct']:>7.4f}% "
            f"{last['amount_tokens']:>11,.6f}"
        )


async def run_all_scenarios():
    """Run all test scenarios."""
    print("\n" + "="*70)
    print("  DISTRIBUTION TEST SCENARIOS")
    print("="*70)

    # Create engine
    if DB_PATH.exists():
        DB_PATH.unlink()
    engine = create_async_engine(DB_URL, echo=False)

    scenarios = []

    # =========================================================================
    # SCENARIO 1: Single holder (edge case)
    # =========================================================================
    holders = [{"balance": 1_000_000, "tier": 3, "days_held": 5}]
    await setup_scenario(engine, holders, "Single Holder")
    result = await run_distribution(engine, 100_000)
    scenarios.append(("Single Holder (100% to one wallet)", result))

    # =========================================================================
    # SCENARIO 2: Two holders, same balance, different tiers
    # =========================================================================
    holders = [
        {"balance": 1_000_000, "tier": 1, "days_held": 0},  # Ore 1.0x
        {"balance": 1_000_000, "tier": 6, "days_held": 30},  # Diamond 5.0x
    ]
    await setup_scenario(engine, holders, "Same Balance Different Tiers")
    result = await run_distribution(engine, 100_000)
    scenarios.append(("Same Balance, Different Tiers (1x vs 5x)", result))

    # =========================================================================
    # SCENARIO 3: Extreme whale (99% of supply)
    # =========================================================================
    holders = [
        {"balance": 99_000_000, "tier": 1, "days_held": 0},  # Whale
    ] + [
        {"balance": 10_000, "tier": 6, "days_held": 30} for _ in range(100)  # Small Diamond holders
    ]
    await setup_scenario(engine, holders, "Extreme Whale")
    result = await run_distribution(engine, 500_000)
    scenarios.append(("Extreme Whale (99M Ore vs 100x 10K Diamond)", result))

    # =========================================================================
    # SCENARIO 4: All Diamond Hands
    # =========================================================================
    holders = [
        {"balance": 1_000_000, "tier": 6, "days_held": 30},
        {"balance": 500_000, "tier": 6, "days_held": 35},
        {"balance": 250_000, "tier": 6, "days_held": 40},
        {"balance": 100_000, "tier": 6, "days_held": 45},
    ]
    await setup_scenario(engine, holders, "All Diamond Hands")
    result = await run_distribution(engine, 100_000)
    scenarios.append(("All Diamond Hands (same multiplier)", result))

    # =========================================================================
    # SCENARIO 5: Equal balances, all tiers
    # =========================================================================
    holders = [
        {"balance": 100_000, "tier": t, "days_held": t * 5}
        for t in range(1, 7)
    ]
    await setup_scenario(engine, holders, "Equal Balance All Tiers")
    result = await run_distribution(engine, 100_000)
    scenarios.append(("Equal Balance, All Tiers (100K each)", result))

    # =========================================================================
    # SCENARIO 6: Dust distribution (very small pool)
    # =========================================================================
    holders = [
        {"balance": 10_000_000, "tier": 3, "days_held": 5},
        {"balance": 5_000_000, "tier": 2, "days_held": 1},
        {"balance": 1_000_000, "tier": 1, "days_held": 0},
    ]
    await setup_scenario(engine, holders, "Dust Distribution")
    result = await run_distribution(engine, 0.001)  # 0.001 tokens = 1M raw units
    scenarios.append(("Dust Distribution (0.001 tokens)", result))

    # =========================================================================
    # SCENARIO 7: Large pool distribution
    # =========================================================================
    holders = [
        {"balance": 50_000_000, "tier": 5, "days_held": 10},
        {"balance": 25_000_000, "tier": 4, "days_held": 5},
        {"balance": 10_000_000, "tier": 3, "days_held": 2},
        {"balance": 5_000_000, "tier": 2, "days_held": 1},
        {"balance": 1_000_000, "tier": 1, "days_held": 0},
    ]
    await setup_scenario(engine, holders, "Large Pool")
    result = await run_distribution(engine, 10_000_000)  # 10M tokens
    scenarios.append(("Large Pool (10M tokens)", result))

    # =========================================================================
    # SCENARIO 8: Tier multiplier dominance test
    # =========================================================================
    holders = [
        {"balance": 100_000, "tier": 6, "days_held": 30},   # 100K * 5.0 = 500K HP
        {"balance": 400_000, "tier": 1, "days_held": 0},    # 400K * 1.0 = 400K HP
    ]
    await setup_scenario(engine, holders, "Tier Dominance")
    result = await run_distribution(engine, 100_000)
    scenarios.append(("Tier Dominance (100K Diamond vs 400K Ore)", result))

    # =========================================================================
    # SCENARIO 9: Many small holders vs few whales
    # =========================================================================
    holders = [
        {"balance": 10_000_000, "tier": 1, "days_held": 0},  # Whale 1
        {"balance": 10_000_000, "tier": 1, "days_held": 0},  # Whale 2
    ] + [
        {"balance": 10_000, "tier": 4, "days_held": 5} for _ in range(500)  # 500 small Industrial holders
    ]
    await setup_scenario(engine, holders, "Whales vs Small Holders")
    result = await run_distribution(engine, 500_000)
    scenarios.append(("2 Whales (10M Ore) vs 500 Small (10K Industrial)", result))

    # =========================================================================
    # SCENARIO 10: Minimum viable distribution
    # =========================================================================
    holders = [
        {"balance": 1, "tier": 6, "days_held": 30},  # 1 raw token
        {"balance": 1, "tier": 1, "days_held": 0},   # 1 raw token
    ]
    await setup_scenario(engine, holders, "Minimum Viable")
    result = await run_distribution(engine, 0.000000001)  # 1 raw unit
    scenarios.append(("Minimum Viable (1 raw unit each)", result))

    # =========================================================================
    # Print all results
    # =========================================================================
    for name, result in scenarios:
        print_scenario_result(name, result)

    await engine.dispose()

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"\n  Total scenarios: {len(scenarios)}")
    passed = sum(1 for _, r in scenarios if r.get("verified", False))
    print(f"  Passed: {passed}/{len(scenarios)}")

    if passed == len(scenarios):
        print("\n  ALL SCENARIOS PASSED!")
    else:
        print("\n  FAILURES:")
        for name, r in scenarios:
            if not r.get("verified", False):
                print(f"    - {name}")

    print()


if __name__ == "__main__":
    asyncio.run(run_all_scenarios())

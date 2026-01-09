#!/usr/bin/env python3
"""
Setup Local SQLite Database for Devnet Testing

Creates a local SQLite database with pre-populated test data
for distribution simulation testing.

Usage:
    python scripts/devnet/setup_local_db.py
"""

import asyncio
import os
import uuid
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

# Ensure we can import from backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, DateTime,
    Numeric, ForeignKey, Text, create_engine, event
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker

# Configuration
DB_PATH = Path(__file__).parent.parent.parent / "backend" / "test_devnet.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"
SYNC_DB_URL = f"sqlite:///{DB_PATH}"

# Token decimals (10^9 for raw amounts)
TOKEN_MULTIPLIER = 10**9

# Number of test holders (can be overridden via command line)
NUM_HOLDERS = 1000

import random
import hashlib

def generate_wallet_address(index: int) -> str:
    """Generate a deterministic fake Solana wallet address."""
    # Create a deterministic but realistic-looking address
    hash_input = f"DevnetTestHolder{index:06d}".encode()
    hash_bytes = hashlib.sha256(hash_input).digest()
    # Base58 alphabet (Solana uses this)
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    result = ""
    num = int.from_bytes(hash_bytes[:32], "big")
    while len(result) < 44:
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result
    return result[:44]

def generate_holder_configs(num_holders: int) -> list:
    """
    Generate realistic holder configurations with power-law distribution.

    Distribution mimics real token holdings:
    - Few whales (top 1%): 50% of supply
    - Medium holders (next 9%): 30% of supply
    - Small holders (remaining 90%): 20% of supply
    """
    random.seed(42)  # Deterministic for reproducibility

    configs = []

    # Tier distribution (realistic)
    # Most holders are new (tier 1-2), fewer are veterans
    tier_weights = {
        1: 0.40,  # 40% Ore (new)
        2: 0.25,  # 25% Raw Copper
        3: 0.15,  # 15% Refined
        4: 0.10,  # 10% Industrial
        5: 0.07,  # 7% Master Miner
        6: 0.03,  # 3% Diamond Hands
    }

    tier_days = {
        1: (0, 0.25),      # 0-6 hours
        2: (0.25, 0.5),    # 6-12 hours
        3: (0.5, 3),       # 12h - 3 days
        4: (3, 7),         # 3-7 days
        5: (7, 30),        # 7-30 days
        6: (30, 60),       # 30-60 days
    }

    for i in range(num_holders):
        # Determine tier based on weights
        rand = random.random()
        cumulative = 0
        tier = 1
        for t, weight in tier_weights.items():
            cumulative += weight
            if rand <= cumulative:
                tier = t
                break

        # Generate balance using power-law distribution
        # Top holders have much more than bottom holders
        percentile = (num_holders - i) / num_holders  # 1.0 for first, ~0 for last

        if percentile > 0.99:  # Top 1% - whales
            balance = random.randint(5_000_000, 50_000_000)
        elif percentile > 0.90:  # Next 9% - large holders
            balance = random.randint(500_000, 5_000_000)
        elif percentile > 0.50:  # Next 40% - medium holders
            balance = random.randint(50_000, 500_000)
        else:  # Bottom 50% - small holders
            balance = random.randint(1_000, 50_000)

        # Days held based on tier
        min_days, max_days = tier_days[tier]
        days_held = random.uniform(min_days, max_days)

        configs.append({
            "balance": balance,
            "tier": tier,
            "days_held": days_held,
        })

    # Sort by balance descending (whales first)
    configs.sort(key=lambda x: x["balance"], reverse=True)

    return configs

Base = declarative_base()


# SQLite-compatible models (using Text instead of UUID)
class Snapshot(Base):
    __tablename__ = "snapshots"
    id = Column(Text, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    snapshot_at = Column(DateTime, nullable=False)  # Alias for compatibility
    total_holders = Column(Integer, nullable=False)
    total_supply = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Balance(Base):
    __tablename__ = "balances"
    id = Column(Text, primary_key=True)
    snapshot_id = Column(Text, ForeignKey("snapshots.id"))
    wallet = Column(String(44), nullable=False)
    wallet_address = Column(String(44), nullable=False)  # Alias for compatibility
    balance = Column(BigInteger, nullable=False)


class HoldStreak(Base):
    __tablename__ = "hold_streaks"
    wallet = Column(String(44), primary_key=True)
    streak_start = Column(DateTime, nullable=False)
    current_tier = Column(Integer, nullable=False, default=1)
    last_sell_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Distribution(Base):
    __tablename__ = "distributions"
    id = Column(Text, primary_key=True)
    pool_amount = Column(BigInteger, nullable=False)
    pool_value_usd = Column(Numeric(18, 2), nullable=True)
    total_hashpower = Column(Numeric(24, 2), nullable=False)
    recipient_count = Column(Integer, nullable=False)
    trigger_type = Column(String(20), nullable=False)
    executed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DistributionRecipient(Base):
    __tablename__ = "distribution_recipients"
    id = Column(Text, primary_key=True)
    distribution_id = Column(Text, ForeignKey("distributions.id"))
    wallet = Column(String(44), nullable=False)
    twab = Column(BigInteger, nullable=False)
    multiplier = Column(Numeric(4, 2), nullable=False)
    hash_power = Column(Numeric(24, 2), nullable=False)
    amount_received = Column(BigInteger, nullable=False)
    tx_signature = Column(String(88), nullable=True)


class DistributionLock(Base):
    __tablename__ = "distribution_lock"
    id = Column(Integer, primary_key=True, default=1)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


async def setup_database(num_holders: int = NUM_HOLDERS):
    """Create database and populate with test data."""
    print(f"\n=== Setting Up Local Test Database ===\n")
    print(f"  Database: {DB_PATH}")
    print(f"  Holders:  {num_holders}")

    # Generate test data
    holder_configs = generate_holder_configs(num_holders)
    test_holders = [generate_wallet_address(i) for i in range(num_holders)]

    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"  Removed existing database")

    # Create async engine
    engine = create_async_engine(DB_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"  Created tables")

    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        now = utc_now()

        # Create snapshots (need at least 2 for TWAB calculation)
        # Snapshots over the last 24 hours
        snapshot_times = [
            now - timedelta(hours=20),
            now - timedelta(hours=16),
            now - timedelta(hours=12),
            now - timedelta(hours=8),
            now - timedelta(hours=4),
            now - timedelta(hours=1),
        ]

        total_supply = sum(cfg["balance"] for cfg in holder_configs) * TOKEN_MULTIPLIER
        snapshots = []

        print(f"\n  Creating {len(snapshot_times)} snapshots...")
        for snap_time in snapshot_times:
            snapshot = Snapshot(
                id=str(uuid.uuid4()),
                timestamp=snap_time,
                snapshot_at=snap_time,
                total_holders=len(test_holders),
                total_supply=total_supply,
                created_at=snap_time,
            )
            session.add(snapshot)
            snapshots.append(snapshot)

        await session.flush()

        # Create balances for each snapshot (batch insert for performance)
        print(f"  Creating balances for {len(test_holders)} holders...")
        balance_count = 0
        for snapshot in snapshots:
            for wallet, config in zip(test_holders, holder_configs):
                balance = Balance(
                    id=str(uuid.uuid4()),
                    snapshot_id=snapshot.id,
                    wallet=wallet,
                    wallet_address=wallet,
                    balance=config["balance"] * TOKEN_MULTIPLIER,
                )
                session.add(balance)
                balance_count += 1

            # Flush every snapshot to avoid memory issues
            await session.flush()
            print(f"    Snapshot {snapshots.index(snapshot) + 1}/{len(snapshots)}: {len(test_holders)} balances")

        # Create hold streaks
        print(f"  Creating {len(test_holders)} hold streaks...")
        for wallet, config in zip(test_holders, holder_configs):
            streak = HoldStreak(
                wallet=wallet,
                streak_start=now - timedelta(days=config["days_held"]),
                current_tier=config["tier"],
                last_sell_at=None,
                updated_at=now,
            )
            session.add(streak)

        # Create distribution lock row
        lock = DistributionLock(id=1)
        session.add(lock)

        await session.commit()
        print(f"\n  Database populated successfully!")
        print(f"  Total balance records: {balance_count}")

    await engine.dispose()

    # Print summary
    print(f"\n=== Test Data Summary ===\n")
    print(f"  Snapshots: {len(snapshot_times)}")
    print(f"  Time range: {snapshot_times[0]} to {snapshot_times[-1]}")
    print(f"  Total holders: {num_holders}")

    # Tier distribution stats
    tier_names = {1: "Ore", 2: "Raw Copper", 3: "Refined", 4: "Industrial", 5: "Master Miner", 6: "Diamond Hands"}
    tier_multipliers = {1: 1.0, 2: 1.25, 3: 1.5, 4: 2.5, 5: 3.5, 6: 5.0}

    tier_counts = {}
    for cfg in holder_configs:
        tier_counts[cfg["tier"]] = tier_counts.get(cfg["tier"], 0) + 1

    print(f"\n  Tier Distribution:")
    print(f"  {'Tier':<15} {'Count':>8} {'Percent':>10} {'Multiplier':>12}")
    print(f"  {'-'*15} {'-'*8} {'-'*10} {'-'*12}")
    for tier in sorted(tier_counts.keys()):
        count = tier_counts[tier]
        pct = count / num_holders * 100
        print(f"  {tier_names[tier]:<15} {count:>8} {pct:>9.1f}% {tier_multipliers[tier]:>11}x")

    # Balance distribution stats
    balances = [cfg["balance"] for cfg in holder_configs]
    print(f"\n  Balance Distribution:")
    print(f"    Min:     {min(balances):>15,} tokens")
    print(f"    Max:     {max(balances):>15,} tokens")
    print(f"    Median:  {sorted(balances)[len(balances)//2]:>15,} tokens")
    print(f"    Total:   {sum(balances):>15,} tokens")

    # Top 10 holders
    print(f"\n  Top 10 Holders:")
    print(f"  {'#':<4} {'Wallet':<20} {'Balance':>15} {'Tier':<15}")
    print(f"  {'-'*4} {'-'*20} {'-'*15} {'-'*15}")
    for i, (wallet, config) in enumerate(zip(test_holders[:10], holder_configs[:10]), 1):
        print(f"  {i:<4} {wallet[:20]:<20} {config['balance']:>14,} {tier_names[config['tier']]:<15}")


def update_env_file():
    """Update .env file with SQLite database URL."""
    env_path = Path(__file__).parent.parent.parent / "backend" / ".env"

    print(f"\n=== Updating .env File ===\n")

    # Read existing .env or create new
    env_content = ""
    if env_path.exists():
        with open(env_path, "r") as f:
            env_content = f.read()

    # Check if DATABASE_URL already exists
    lines = env_content.split("\n")
    new_lines = []
    found_db_url = False

    for line in lines:
        if line.startswith("DATABASE_URL="):
            # Comment out old DATABASE_URL and add new one
            new_lines.append(f"# {line}  # Commented for local testing")
            new_lines.append(f"DATABASE_URL={DB_URL}")
            found_db_url = True
            print(f"  Updated DATABASE_URL to: {DB_URL}")
        else:
            new_lines.append(line)

    if not found_db_url:
        new_lines.append(f"\n# Local test database")
        new_lines.append(f"DATABASE_URL={DB_URL}")
        print(f"  Added DATABASE_URL: {DB_URL}")

    # Ensure COPPER_TOKEN_MINT is set (needed for formatting)
    if "COPPER_TOKEN_MINT=" not in env_content:
        new_lines.append(f"\n# Test token mint (placeholder)")
        new_lines.append(f"COPPER_TOKEN_MINT=DevnetTestToken11111111111111111111111111")
        print(f"  Added placeholder COPPER_TOKEN_MINT")

    # Write updated .env
    with open(env_path, "w") as f:
        f.write("\n".join(new_lines))

    print(f"  Saved: {env_path}")


async def main():
    # Parse command line arguments
    num_holders = NUM_HOLDERS
    if len(sys.argv) > 1:
        try:
            num_holders = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [num_holders]")
            print(f"  num_holders: Number of test holders (default: {NUM_HOLDERS})")
            return

    await setup_database(num_holders)
    update_env_file()

    print(f"\n=== Setup Complete ===\n")
    print(f"  You can now run the distribution simulation:")
    print(f"  python scripts/devnet/simulate_distribution.py 500000")
    print()


if __name__ == "__main__":
    asyncio.run(main())

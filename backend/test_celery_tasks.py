#!/usr/bin/env python3
"""
Celery Tasks Test Script

Tests Celery tasks directly without running worker/beat.

Usage:
    python test_celery_tasks.py snapshot      # Test snapshot task
    python test_celery_tasks.py distribution  # Test distribution task
    python test_celery_tasks.py buyback       # Test buyback task
    python test_celery_tasks.py tiers         # Test tier update task
    python test_celery_tasks.py all           # Test all tasks
"""

import asyncio
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_celery")

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def print_rpc_stats():
    """Print RPC call statistics."""
    from app.utils.http_client import rpc_counter
    stats = rpc_counter.get_stats()

    print("\n--- RPC Call Statistics ---")
    print(f"  Total RPC Calls: {stats['total']}")
    if stats['by_endpoint']:
        for endpoint, count in sorted(stats['by_endpoint'].items(), key=lambda x: -x[1]):
            print(f"    {endpoint}: {count}")
    print()


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def test_snapshot():
    """Test the snapshot task."""
    print_header("SNAPSHOT TASK TEST")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.snapshot import SnapshotService
    from app.config import get_settings

    settings = get_settings()
    print(f"CPU Token Mint: {settings.cpu_token_mint or 'NOT SET'}")
    print()

    if not settings.cpu_token_mint:
        print("CPU_TOKEN_MINT not configured - cannot take snapshot")
        return False

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = SnapshotService(db)

        print("Taking snapshot...")
        snapshot = await service.take_snapshot()

        if snapshot:
            print(f"\n  Snapshot ID: {snapshot.id}")
            print(f"  Timestamp: {snapshot.timestamp}")
            print(f"  Total Holders: {snapshot.total_holders}")
            print(f"  Total Supply: {snapshot.total_supply:,}")
            print_rpc_stats()
            return True
        else:
            print("  Snapshot failed or no holders found")
            print_rpc_stats()
            return False


async def test_distribution():
    """Test the distribution check task."""
    print_header("DISTRIBUTION TASK TEST")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.distribution import DistributionService

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        print("Checking distribution triggers...")
        should, trigger = await service.should_distribute()

        print(f"\n  Should Distribute: {should}")
        print(f"  Trigger Type: {trigger or 'N/A'}")

        status = await service.get_pool_status()
        print(f"\n  Pool Balance: {status.balance:,} raw")
        print(f"  Pool Value: ${status.value_usd:.2f}")
        print(f"  Hours Since Last: {status.hours_since_last:.1f}h" if status.hours_since_last else "  Hours Since Last: N/A")

        print_rpc_stats()
        return True


async def test_buyback():
    """Test the buyback/rewards task."""
    print_header("BUYBACK TASK TEST")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.buyback import BuybackService
    from app.config import get_settings

    settings = get_settings()
    session_maker = get_worker_session_maker()

    async with session_maker() as db:
        service = BuybackService(db)

        print("Checking unprocessed rewards...")
        rewards = await service.get_unprocessed_rewards()

        print(f"\n  Unprocessed Rewards: {len(rewards)}")

        if rewards:
            total_sol = sum(r.amount_sol for r in rewards)
            print(f"  Total SOL: {total_sol}")

            # Show split calculation
            split = service.calculate_split(total_sol)
            print(f"\n  Split (100% to Pool):")
            print(f"    Pool: {split.pool_sol} SOL")
        else:
            print("  No pending rewards to process")

        print_rpc_stats()
        return True


async def test_tiers():
    """Test the tier update task."""
    print_header("TIER UPDATE TASK TEST")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from sqlalchemy import select, func
    from app.models import HoldStreak
    from app.config import TIER_CONFIG

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        # Get tier distribution
        result = await db.execute(
            select(HoldStreak.current_tier, func.count(HoldStreak.wallet))
            .group_by(HoldStreak.current_tier)
            .order_by(HoldStreak.current_tier)
        )
        tier_counts = {row[0]: row[1] for row in result.fetchall()}

        print("Current Tier Distribution:")
        for tier, config in TIER_CONFIG.items():
            count = tier_counts.get(tier, 0)
            print(f"  Tier {tier} ({config['name']}): {count} wallets")

        total = sum(tier_counts.values())
        print(f"\n  Total Streaks: {total}")

        print_rpc_stats()
        return True


async def test_all():
    """Test all tasks."""
    print_header("TESTING ALL CELERY TASKS")

    results = {}

    # Test each task
    results['snapshot'] = await test_snapshot()
    results['distribution'] = await test_distribution()
    results['buyback'] = await test_buyback()
    results['tiers'] = await test_tiers()

    # Summary
    print_header("TEST SUMMARY")
    for task, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {task}: {status}")

    return all(results.values())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "snapshot":
            asyncio.run(test_snapshot())
        elif command == "distribution":
            asyncio.run(test_distribution())
        elif command == "buyback":
            asyncio.run(test_buyback())
        elif command == "tiers":
            asyncio.run(test_tiers())
        elif command == "all":
            asyncio.run(test_all())
        else:
            print(f"Unknown command: {command}")
            print("Commands: snapshot, distribution, buyback, tiers, all")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Mainnet Distribution Test

Tests distribution on mainnet with safety checks.

Usage:
    python test_distribution_mainnet.py preview   # Show plan only (safe)
    python test_distribution_mainnet.py execute   # Actually execute (REAL!)
"""

import asyncio
import sys
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_distribution")

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


async def preview_distribution():
    """Preview distribution without executing."""
    print_header("MAINNET DISTRIBUTION PREVIEW")

    # Reset RPC counter for this run
    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.distribution import DistributionService
    from app.config import get_settings, GOLD_MULTIPLIER

    settings = get_settings()

    print(f"Environment: {settings.environment}")
    print(f"Network: {settings.solana_network}")
    print()

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        # Get pool status
        print("--- Pool Status ---")
        status = await service.get_pool_status()

        print(f"  Balance: {status.balance_formatted:,.2f} GOLD ({status.balance:,} raw)")
        print(f"  Value: ${status.value_usd:.2f} USD")
        print(f"  Hours Since Last: {status.hours_since_last:.1f}h" if status.hours_since_last else "  Hours Since Last: N/A")
        print()

        if status.balance <= 0:
            print("❌ Pool is empty - nothing to distribute")
            return None

        # Calculate distribution plan
        print("--- Calculating Distribution Plan ---")
        plan = await service.calculate_distribution()

        if not plan:
            print("❌ Could not create distribution plan")
            return None

        print(f"  Pool Amount: {plan.pool_amount:,} raw ({plan.pool_amount / GOLD_MULTIPLIER:,.6f} GOLD)")
        print(f"  Total Recipients: {plan.recipient_count}")
        print(f"  Total Hash Power: {plan.total_hashpower:,.0f}")
        print()

        # Show all recipients
        print("--- All Recipients ---")
        print(f"{'#':<4} {'Wallet':<20} {'Share %':<10} {'Amount':<15} {'GOLD':<12}")
        print("-" * 65)

        for i, r in enumerate(plan.recipients):
            wallet_short = f"{r.wallet[:8]}...{r.wallet[-4:]}"
            gold_amount = r.amount / GOLD_MULTIPLIER
            print(f"{i+1:<4} {wallet_short:<20} {r.share_percentage:>8.4f}% {r.amount:>14,} {gold_amount:>11.6f}")

        print("-" * 65)
        total = sum(r.amount for r in plan.recipients)
        print(f"{'TOTAL':<4} {'':<20} {'100.0000%':<10} {total:>14,} {total/GOLD_MULTIPLIER:>11.6f}")

        # Show RPC stats
        print_rpc_stats()

        return plan


async def execute_distribution():
    """Actually execute distribution on mainnet."""
    print_header("⚠️  MAINNET DISTRIBUTION EXECUTION ⚠️")

    from app.config import get_settings
    settings = get_settings()

    print(f"Environment: {settings.environment}")
    print(f"Network: {settings.solana_network}")
    print()

    if settings.environment != "production":
        print("❌ Not in production environment!")
        return False

    if settings.solana_network != "mainnet-beta":
        print("❌ Not on mainnet-beta!")
        return False

    # First show preview
    plan = await preview_distribution()

    if not plan:
        return False

    print()
    print("=" * 60)
    print("  ⚠️  WARNING: This will execute REAL token transfers!")
    print(f"  Recipients: {plan.recipient_count}")
    print(f"  Total GOLD: {plan.pool_amount / 1_000_000:,.6f}")
    print("=" * 60)
    print()

    confirm = input("Type 'EXECUTE' to proceed: ")
    if confirm != "EXECUTE":
        print("Cancelled.")
        return False

    print()
    print("Executing distribution...")

    # Reset RPC counter for execution phase
    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.distribution import DistributionService

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        distribution = await service.execute_distribution(plan)

        if distribution:
            print()
            print_header("✅ DISTRIBUTION COMPLETE")
            print(f"  Distribution ID: {distribution.id}")
            print(f"  Recipients: {distribution.recipient_count}")
            print(f"  Pool Amount: {distribution.pool_amount:,}")
            print(f"  Executed At: {distribution.executed_at}")

            # Show RPC stats for execution
            print_rpc_stats()
            return True
        else:
            print()
            print("❌ Distribution failed!")
            print_rpc_stats()
            return False


async def check_failed_transfers():
    """Check for any failed transfers that need reconciliation."""
    print_header("FAILED TRANSFERS CHECK")

    from app.database import get_worker_session_maker
    from app.services.distribution import DistributionService
    from app.config import GOLD_MULTIPLIER

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        failed = await service.get_failed_transfers()

        if not failed:
            print("✅ No failed transfers found")
            return True

        print(f"⚠️  Found {len(failed)} failed transfers:")
        print()

        for r in failed:
            print(f"  Distribution {r.distribution_id}:")
            print(f"    Wallet: {r.wallet}")
            print(f"    Amount: {r.amount_received:,} (expected based on hash power)")
            print()

        return False


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_distribution_mainnet.py preview   # Show plan (safe)")
        print("  python test_distribution_mainnet.py execute   # Execute (REAL!)")
        print("  python test_distribution_mainnet.py failed    # Check failed transfers")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "preview":
            asyncio.run(preview_distribution())
        elif command == "execute":
            asyncio.run(execute_distribution())
        elif command == "failed":
            asyncio.run(check_failed_transfers())
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

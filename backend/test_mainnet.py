#!/usr/bin/env python3
"""
Mainnet Validation Test Script

Tests distribution, Jupiter swap, and TWAB calculations locally
before deploying to production.

Usage:
    cd backend
    python test_mainnet.py [test_name]

Tests:
    python test_mainnet.py distribution  # Test distribution calculation
    python test_mainnet.py jupiter       # Test Jupiter quote (no execution)
    python test_mainnet.py pool          # Check pool status
    python test_mainnet.py all           # Run all tests
"""

import asyncio
import sys
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_mainnet")

# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def print_header(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(label: str, value, indent: int = 0):
    """Print a labeled result."""
    prefix = "  " * indent
    print(f"{prefix}{label}: {value}")


async def test_pool_status():
    """Test pool status and balance fetching."""
    print_header("POOL STATUS TEST")

    from app.database import get_worker_session_maker
    from app.services.distribution import DistributionService
    from app.config import get_settings, GOLD_MULTIPLIER

    settings = get_settings()

    print_result("Environment", settings.environment)
    print_result("Solana Network", settings.solana_network)
    print_result("GOLD Token Mint", settings.gold_token_mint[:16] + "..." if settings.gold_token_mint else "NOT SET")
    print_result("CPU Token Mint", settings.cpu_token_mint[:16] + "..." if settings.cpu_token_mint else "NOT SET")

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = DistributionService(db)

        # Get pool status
        status = await service.get_pool_status()

        print("\n--- Pool Status ---")
        print_result("Balance (raw)", status.balance)
        print_result("Balance (formatted)", f"{status.balance_formatted:,.2f} GOLD")
        print_result("Value USD", f"${status.value_usd:.2f}")
        print_result("Last Distribution", status.last_distribution)
        print_result("Hours Since Last", f"{status.hours_since_last:.1f}h" if status.hours_since_last else "N/A")
        print_result("Threshold Met", status.threshold_met)
        print_result("Time Trigger Met", status.time_trigger_met)
        print_result("Should Distribute", status.should_distribute)

        # Get GOLD price
        gold_price = await service.get_gold_price_usd()
        print_result("GOLD Price USD", f"${gold_price:.6f}")

        return status.balance > 0


async def test_distribution_calculation():
    """Test distribution calculation without executing."""
    print_header("DISTRIBUTION CALCULATION TEST")

    from app.database import get_worker_session_maker
    from app.services.distribution import DistributionService
    from app.services.twab import TWABService
    from app.config import get_settings

    settings = get_settings()
    session_maker = get_worker_session_maker()

    async with session_maker() as db:
        service = DistributionService(db)
        twab_service = TWABService(db)

        # Get time range (last 24h or since last distribution)
        last_dist = await service.get_last_distribution()
        end = datetime.now(timezone.utc)

        if last_dist:
            start = last_dist.executed_at
            print_result("Period Start", f"{start} (last distribution)")
        else:
            start = end - timedelta(hours=24)
            print_result("Period Start", f"{start} (24h ago)")

        print_result("Period End", end)

        # Calculate hash powers (no min_balance filter)
        print("\n--- Hash Power Calculation ---")
        hash_powers = await twab_service.calculate_all_hash_powers(
            start, end, min_balance=0
        )

        print_result("Total Wallets with Hash Power", len(hash_powers))

        if not hash_powers:
            print("\n❌ No wallets found with hash power!")
            print("   This could mean:")
            print("   - No snapshots in the time period")
            print("   - All wallets are excluded")
            return False

        # Show top 10 by hash power
        print("\n--- Top 10 by Hash Power ---")
        for i, hp in enumerate(hash_powers[:10]):
            print(f"  {i+1}. {hp.wallet[:8]}...{hp.wallet[-4:]}")
            print(f"     TWAB: {hp.twab:,} | Tier: {hp.tier} ({hp.tier_name}) | HP: {hp.hash_power:,.0f}")

        # Calculate distribution plan
        print("\n--- Distribution Plan ---")
        plan = await service.calculate_distribution()

        if not plan:
            print("\n❌ Could not create distribution plan!")
            return False

        print_result("Pool Amount", f"{plan.pool_amount:,} raw tokens")
        print_result("Pool Value USD", f"${plan.pool_value_usd:.2f}")
        print_result("Total Hash Power", f"{plan.total_hashpower:,.0f}")
        print_result("Recipient Count", plan.recipient_count)
        print_result("Trigger Type", plan.trigger_type)

        # Show distribution to top 10
        print("\n--- Top 10 Recipients ---")
        for i, r in enumerate(plan.recipients[:10]):
            print(f"  {i+1}. {r.wallet[:8]}...{r.wallet[-4:]}")
            print(f"     Share: {r.share_percentage:.2f}% | Amount: {r.amount:,}")

        # Show distribution to bottom 5 (check for 0 amounts)
        if len(plan.recipients) > 10:
            print("\n--- Bottom 5 Recipients ---")
            for r in plan.recipients[-5:]:
                print(f"  {r.wallet[:8]}...{r.wallet[-4:]}: {r.amount:,} ({r.share_percentage:.4f}%)")

        # Summary
        total_distributed = sum(r.amount for r in plan.recipients)
        print("\n--- Summary ---")
        print_result("Total to Distribute", f"{total_distributed:,}")
        print_result("Remainder", f"{plan.pool_amount - total_distributed:,}")

        return True


async def test_jupiter_quote():
    """Test Jupiter quote without executing swap."""
    print_header("JUPITER QUOTE TEST")

    from app.database import get_worker_session_maker
    from app.services.buyback import BuybackService
    from app.config import get_settings, LAMPORTS_PER_SOL

    settings = get_settings()

    if not settings.gold_token_mint:
        print("❌ GOLD_TOKEN_MINT not configured!")
        return False

    print_result("GOLD Token Mint", settings.gold_token_mint)
    print_result("Slippage BPS", settings.safe_slippage_bps)

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = BuybackService(db)

        # Test with different SOL amounts
        test_amounts = [0.01, 0.1, 1.0, 10.0]

        print("\n--- Quote Tests ---")
        for sol_amount in test_amounts:
            lamports = int(sol_amount * LAMPORTS_PER_SOL)

            quote = await service.get_jupiter_quote(lamports)

            if quote:
                out_amount = int(quote.data.get("outAmount", 0))
                price_impact = quote.data.get("priceImpactPct", "N/A")
                route_plan = quote.data.get("routePlan", [])

                print(f"\n  {sol_amount} SOL:")
                print(f"    Output: {out_amount:,} GOLD")
                print(f"    Price Impact: {price_impact}%")
                print(f"    Route Steps: {len(route_plan)}")

                if route_plan:
                    for step in route_plan[:2]:  # Show first 2 steps
                        swap_info = step.get("swapInfo", {})
                        label = swap_info.get("label", "Unknown")
                        print(f"    - {label}")
            else:
                print(f"\n  {sol_amount} SOL: ❌ Quote failed!")

        return True


async def test_excluded_wallets():
    """Check excluded wallets configuration."""
    print_header("EXCLUDED WALLETS CHECK")

    from app.database import get_worker_session_maker
    from app.models import ExcludedWallet
    from sqlalchemy import select

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        result = await db.execute(select(ExcludedWallet))
        excluded = list(result.scalars().all())

        print_result("Total Excluded Wallets", len(excluded))

        if excluded:
            print("\n--- Excluded Wallets ---")
            for w in excluded[:10]:
                print(f"  - {w.wallet[:16]}... ({w.reason or 'no reason'})")

            if len(excluded) > 10:
                print(f"  ... and {len(excluded) - 10} more")

        return True


async def test_snapshots():
    """Check recent snapshots."""
    print_header("SNAPSHOTS CHECK")

    from app.database import get_worker_session_maker
    from app.models import Snapshot, Balance
    from sqlalchemy import select, func
    from datetime import timedelta

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        # Get recent snapshots
        result = await db.execute(
            select(Snapshot)
            .order_by(Snapshot.created_at.desc())
            .limit(10)
        )
        snapshots = list(result.scalars().all())

        print_result("Recent Snapshots", len(snapshots))

        if snapshots:
            print("\n--- Last 10 Snapshots ---")
            for s in snapshots:
                print(f"  {s.created_at}: {s.total_holders} holders, {s.total_supply:,} supply")

            # Check snapshot frequency
            if len(snapshots) >= 2:
                time_diff = snapshots[0].created_at - snapshots[1].created_at
                print(f"\n  Time between last 2 snapshots: {time_diff}")
        else:
            print("\n❌ No snapshots found!")
            print("   Run: celery -A app.tasks.celery_app call app.tasks.snapshot_task.take_snapshot")
            return False

        # Count balances in last 24h
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await db.execute(
            select(func.count(func.distinct(Balance.wallet)))
            .join(Snapshot, Balance.snapshot_id == Snapshot.id)
            .where(Snapshot.created_at >= cutoff)
        )
        unique_wallets = result.scalar_one()
        print_result("\nUnique Wallets (24h)", unique_wallets)

        return True


async def run_all_tests():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("  MAINNET VALIDATION TESTS")
    print("=" * 60)

    results = {}

    # Run tests in order
    tests = [
        ("Pool Status", test_pool_status),
        ("Snapshots", test_snapshots),
        ("Excluded Wallets", test_excluded_wallets),
        ("Distribution Calculation", test_distribution_calculation),
        ("Jupiter Quote", test_jupiter_quote),
    ]

    for name, test_func in tests:
        try:
            results[name] = await test_func()
        except Exception as e:
            logger.error(f"Test '{name}' failed with error: {e}", exc_info=True)
            results[name] = False

    # Summary
    print_header("TEST SUMMARY")

    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("  🎉 All tests passed! Ready for deployment.")
    else:
        print("  ⚠️  Some tests failed. Review the output above.")

    return all_passed


def main():
    """Main entry point."""
    # Parse command line args
    test_name = sys.argv[1] if len(sys.argv) > 1 else "all"

    # Map test names to functions
    tests = {
        "pool": test_pool_status,
        "distribution": test_distribution_calculation,
        "jupiter": test_jupiter_quote,
        "excluded": test_excluded_wallets,
        "snapshots": test_snapshots,
        "all": run_all_tests,
    }

    if test_name not in tests:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(tests.keys())}")
        sys.exit(1)

    # Run the test
    try:
        result = asyncio.run(tests[test_name]())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

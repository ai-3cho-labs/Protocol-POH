#!/usr/bin/env python3
"""
Jupiter Swap Test Script

Tests Jupiter swap functionality with detailed debugging.

Usage:
    cd backend
    python test_jupiter.py quote           # Test quote only (safe)
    python test_jupiter.py quote 0.1       # Test quote for 0.1 SOL
    python test_jupiter.py balance         # Check wallet balances
    python test_jupiter.py swap 0.001      # Execute tiny swap (REAL!)
"""

import asyncio
import sys
import logging
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_jupiter")

# Suppress noisy loggers
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


async def check_balances():
    """Check SOL and GOLD balances of relevant wallets."""
    print_header("WALLET BALANCES")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.config import get_settings, LAMPORTS_PER_SOL, GOLD_MULTIPLIER
    from app.services.helius import get_helius_service
    from app.utils.solana_tx import keypair_from_base58

    settings = get_settings()
    helius = get_helius_service()

    wallets = {}

    # Creator wallet
    if settings.creator_wallet_private_key:
        kp = keypair_from_base58(settings.creator_wallet_private_key)
        wallets["Creator"] = str(kp.pubkey())

    # Airdrop pool
    if settings.airdrop_pool_private_key:
        kp = keypair_from_base58(settings.airdrop_pool_private_key)
        wallets["Airdrop Pool"] = str(kp.pubkey())

    print(f"\nGOLD Token: {settings.gold_token_mint}")
    print()

    for name, address in wallets.items():
        print(f"--- {name} ---")
        print(f"  Address: {address}")

        # Get SOL balance
        try:
            sol_balance = await helius.get_sol_balance(address)
            print(f"  SOL: {sol_balance / LAMPORTS_PER_SOL:.4f}")
        except Exception as e:
            print(f"  SOL: Error - {e}")

        # Get GOLD balance
        try:
            gold_balance = await helius.get_token_balance(address, settings.gold_token_mint)
            print(f"  GOLD: {gold_balance / GOLD_MULTIPLIER:,.2f}")
        except Exception as e:
            print(f"  GOLD: Error - {e}")

        print()

    print_rpc_stats()
    return True


async def test_quote(sol_amount: float = 0.1):
    """Test Jupiter quote for a specific SOL amount."""
    print_header(f"JUPITER QUOTE TEST ({sol_amount} SOL)")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.buyback import BuybackService
    from app.config import get_settings, LAMPORTS_PER_SOL, GOLD_MULTIPLIER

    settings = get_settings()

    print(f"Input: {sol_amount} SOL")
    print(f"Output Token: {settings.gold_token_mint}")
    print(f"Slippage: {settings.safe_slippage_bps} bps ({settings.safe_slippage_bps / 100}%)")
    print(f"API URL: {settings.jupiter_api_base_url}")
    print(f"API Key: {'✅ Configured' if settings.jupiter_api_key else '❌ Not set'}")
    print()

    if not settings.gold_token_mint:
        print("❌ GOLD_TOKEN_MINT not configured!")
        return False

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = BuybackService(db)

        lamports = int(sol_amount * LAMPORTS_PER_SOL)
        print(f"Requesting quote for {lamports:,} lamports...")

        quote = await service.get_jupiter_quote(lamports)

        if not quote:
            print("\n❌ Quote failed!")
            print("   Possible reasons:")
            print("   - Token not tradeable on Jupiter")
            print("   - Insufficient liquidity")
            print("   - Network issues")
            return False

        print("\n--- Quote Response ---")

        # Parse quote data
        in_amount = int(quote.data.get("inAmount", 0))
        out_amount = int(quote.data.get("outAmount", 0))
        price_impact = quote.data.get("priceImpactPct", "N/A")
        other_amount_threshold = quote.data.get("otherAmountThreshold", 0)
        route_plan = quote.data.get("routePlan", [])

        print(f"  Input Amount: {in_amount:,} lamports ({in_amount / LAMPORTS_PER_SOL:.6f} SOL)")
        print(f"  Output Amount: {out_amount:,} raw ({out_amount / GOLD_MULTIPLIER:,.6f} GOLD)")
        print(f"  Price Impact: {price_impact}%")
        print(f"  Min Output (with slippage): {int(other_amount_threshold):,}")

        # Calculate effective price
        if out_amount > 0:
            price_per_gold = (sol_amount / (out_amount / GOLD_MULTIPLIER))
            print(f"  Effective Price: {price_per_gold:.8f} SOL per GOLD")

        # Show route
        print(f"\n--- Route ({len(route_plan)} steps) ---")
        for i, step in enumerate(route_plan):
            swap_info = step.get("swapInfo", {})
            label = swap_info.get("label", "Unknown")
            amm_key = swap_info.get("ammKey", "")[:16]
            in_amt = swap_info.get("inAmount", 0)
            out_amt = swap_info.get("outAmount", 0)
            fee_amount = swap_info.get("feeAmount", 0)

            print(f"  Step {i+1}: {label}")
            print(f"    AMM: {amm_key}...")
            print(f"    In: {int(in_amt):,} → Out: {int(out_amt):,}")
            print(f"    Fee: {int(fee_amount):,}")

        # Quote freshness
        print(f"\n  Quote Age: {quote.age_seconds():.1f}s")
        print(f"  Quote Fresh: {quote.is_fresh()}")

        print_rpc_stats()
        return True


async def test_swap_execution(sol_amount: float = 0.001):
    """Actually execute a small swap (use with caution!)."""
    print_header(f"JUPITER SWAP EXECUTION ({sol_amount} SOL)")

    print("⚠️  WARNING: This will execute a REAL swap on mainnet!")
    print(f"    Amount: {sol_amount} SOL")
    print()

    confirm = input("Type 'yes' to proceed: ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return False

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.buyback import BuybackService
    from app.config import get_settings, GOLD_MULTIPLIER

    settings = get_settings()

    if not settings.airdrop_pool_private_key:
        print("❌ AIRDROP_POOL_PRIVATE_KEY not configured!")
        return False

    session_maker = get_worker_session_maker()
    async with session_maker() as db:
        service = BuybackService(db)

        print(f"\nExecuting swap: {sol_amount} SOL → GOLD...")

        result = await service.execute_swap(
            Decimal(str(sol_amount)),
            settings.airdrop_pool_private_key
        )

        print("\n--- Swap Result ---")
        print(f"  Success: {result.success}")
        print(f"  TX Signature: {result.tx_signature}")
        print(f"  SOL Spent: {result.sol_spent}")
        print(f"  GOLD Received: {result.copper_received:,} ({result.copper_received / GOLD_MULTIPLIER:,.6f})")
        print(f"  Price per Token: {result.price_per_token}")

        if result.error:
            print(f"  Error: {result.error}")

        if result.tx_signature:
            print(f"\n  View on Solscan: https://solscan.io/tx/{result.tx_signature}")

        print_rpc_stats()
        return result.success


async def test_full_buyback_flow():
    """Test the full buyback flow without executing (dry run)."""
    print_header("FULL BUYBACK FLOW (DRY RUN)")

    from app.utils.http_client import rpc_counter
    rpc_counter.reset()

    from app.database import get_worker_session_maker
    from app.services.buyback import BuybackService
    from app.config import get_settings

    settings = get_settings()
    session_maker = get_worker_session_maker()

    async with session_maker() as db:
        service = BuybackService(db)

        # Check unprocessed rewards
        rewards = await service.get_unprocessed_rewards()
        total_sol = sum(r.amount_sol for r in rewards)

        print(f"Unprocessed Rewards: {len(rewards)}")
        print(f"Total SOL: {total_sol}")

        if not rewards:
            print("\nNo pending rewards to process.")
            return True

        # Calculate split
        split = service.calculate_split(total_sol)

        print("\n--- Reward Split (100% to Pool) ---")
        print(f"  Total: {split.total_sol} SOL")
        print(f"  Pool: {split.pool_sol} SOL")

        # The pool portion gets further split
        swap_amount = split.pool_sol * Decimal("0.20")
        reserve_amount = split.pool_sol * Decimal("0.80")

        print("\n--- Buyback Split (20/80) ---")
        print(f"  Swap to GOLD (20%): {swap_amount} SOL")
        print(f"  Keep as SOL (80%): {reserve_amount} SOL")

        # Test quote for swap amount
        if swap_amount > 0:
            from app.config import LAMPORTS_PER_SOL
            lamports = int(swap_amount * LAMPORTS_PER_SOL)
            quote = await service.get_jupiter_quote(lamports)

            if quote:
                out_amount = int(quote.data.get("outAmount", 0))
                print(f"\n  Expected GOLD output: {out_amount:,}")
            else:
                print("\n  ❌ Could not get quote for swap amount")

        print_rpc_stats()
        return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "balance":
            asyncio.run(check_balances())

        elif command == "quote":
            amount = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
            asyncio.run(test_quote(amount))

        elif command == "swap":
            if len(sys.argv) < 3:
                print("Usage: python test_jupiter.py swap <amount>")
                print("Example: python test_jupiter.py swap 0.001")
                sys.exit(1)
            amount = float(sys.argv[2])
            asyncio.run(test_swap_execution(amount))

        elif command == "flow":
            asyncio.run(test_full_buyback_flow())

        else:
            print(f"Unknown command: {command}")
            print("Commands: balance, quote, swap, flow")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

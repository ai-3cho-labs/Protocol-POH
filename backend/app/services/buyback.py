"""
$GOLD Buyback Service

Processes creator rewards and executes Jupiter swaps.
80% → Airdrop Pool (SOL)
      └── 20% swapped to GOLD (buyback)
      └── 80% kept as SOL (reserves/fees)
10% → Algo Bot (trading operations)
10% → Team Operations (maintenance)
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CreatorReward, Buyback, SystemStats
from app.config import get_settings, LAMPORTS_PER_SOL, SOL_MINT
from app.utils.http_client import get_http_client
from app.utils.solana_tx import (
    sign_and_send_transaction,
    send_sol_transfer,
    confirm_transaction,
)
from app.websocket.broadcaster import emit_pool_updated

logger = logging.getLogger(__name__)
settings = get_settings()


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"
# Jupiter quotes expire after ~60s, use 50s to be safe
JUPITER_QUOTE_MAX_AGE_SECONDS = 50


@dataclass
class JupiterQuote:
    """Jupiter swap quote with timestamp for freshness tracking."""

    data: dict
    fetched_at: datetime

    def is_fresh(self) -> bool:
        """Check if the quote is still within the valid time window."""
        age = (utc_now() - self.fetched_at).total_seconds()
        return age < JUPITER_QUOTE_MAX_AGE_SECONDS

    def age_seconds(self) -> float:
        """Get the age of the quote in seconds."""
        return (utc_now() - self.fetched_at).total_seconds()


@dataclass
class BuybackResult:
    """Result of a buyback execution."""

    success: bool
    tx_signature: Optional[str]
    sol_spent: Decimal
    copper_received: int
    price_per_token: Optional[Decimal]
    error: Optional[str] = None


@dataclass
class RewardSplit:
    """80/10/10 split of creator rewards."""

    total_sol: Decimal
    buyback_sol: Decimal  # 80% → Reward pool
    algo_bot_sol: Decimal  # 10% → Algo bot
    team_sol: Decimal  # 10% → Maintenance


class BuybackService:
    """Service for processing buybacks from creator rewards (SOL → GOLD)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        # Buybacks swap SOL for GOLD tokens to fund the reward pool
        self.token_mint = settings.gold_token_mint

    @property
    def client(self):
        """Get shared HTTP client."""
        return get_http_client()

    async def get_unprocessed_rewards(self) -> list[CreatorReward]:
        """
        Get all unprocessed creator rewards.

        Returns:
            List of unprocessed CreatorReward records.
        """
        result = await self.db.execute(
            select(CreatorReward)
            .where(CreatorReward.processed == False)
            .order_by(CreatorReward.received_at.asc())
        )
        return list(result.scalars().all())

    async def get_total_unprocessed_sol(self) -> Decimal:
        """
        Get total SOL from unprocessed rewards.

        Returns:
            Total unprocessed SOL amount.
        """
        result = await self.db.execute(
            select(func.sum(CreatorReward.amount_sol)).where(
                CreatorReward.processed == False
            )
        )
        total = result.scalar_one_or_none()
        return Decimal(total) if total else Decimal(0)

    def calculate_split(self, total_sol: Decimal) -> RewardSplit:
        """
        Calculate 80/10/10 split of rewards.

        Args:
            total_sol: Total SOL to split.

        Returns:
            RewardSplit with buyback, algo bot, and team amounts.
        """
        buyback_sol = total_sol * Decimal("0.8")  # 80% → Reward pool
        algo_bot_sol = total_sol * Decimal("0.1")  # 10% → Algo bot
        team_sol = total_sol * Decimal("0.1")  # 10% → Maintenance

        return RewardSplit(
            total_sol=total_sol,
            buyback_sol=buyback_sol,
            algo_bot_sol=algo_bot_sol,
            team_sol=team_sol,
        )

    async def get_jupiter_quote(
        self, sol_amount_lamports: int
    ) -> Optional[JupiterQuote]:
        """
        Get swap quote from Jupiter with timestamp for freshness tracking.

        Args:
            sol_amount_lamports: Amount of SOL in lamports.

        Returns:
            JupiterQuote with data and timestamp, or None if error.
        """
        if not self.token_mint:
            logger.error("Token mint not configured")
            return None

        try:
            fetch_time = utc_now()
            response = await self.client.get(
                JUPITER_QUOTE_API,
                params={
                    "inputMint": SOL_MINT,
                    "outputMint": self.token_mint,
                    "amount": str(sol_amount_lamports),
                    "slippageBps": settings.safe_slippage_bps,  # Capped slippage (max 2% to prevent MEV)
                    "onlyDirectRoutes": False,
                    "asLegacyTransaction": False,
                },
            )
            response.raise_for_status()
            return JupiterQuote(data=response.json(), fetched_at=fetch_time)

        except Exception as e:
            logger.error(f"Error getting Jupiter quote: {e}")
            return None

    async def execute_swap(
        self, sol_amount: Decimal, wallet_private_key: str
    ) -> BuybackResult:
        """
        Execute a Jupiter swap (SOL → GOLD).

        Includes quote freshness validation - will re-fetch the quote if
        it has expired (older than JUPITER_QUOTE_MAX_AGE_SECONDS).

        Args:
            sol_amount: Amount of SOL to swap.
            wallet_private_key: Base58 private key of buyback wallet.

        Returns:
            BuybackResult with transaction details.
        """
        if not wallet_private_key:
            return BuybackResult(
                success=False,
                tx_signature=None,
                sol_spent=Decimal(0),
                copper_received=0,
                price_per_token=None,
                error="Wallet private key not configured",
            )

        lamports = int(sol_amount * LAMPORTS_PER_SOL)

        # Get initial quote
        quote = await self.get_jupiter_quote(lamports)
        if not quote:
            return BuybackResult(
                success=False,
                tx_signature=None,
                sol_spent=Decimal(0),
                copper_received=0,
                price_per_token=None,
                error="Failed to get Jupiter quote",
            )

        try:
            # Get the public key from private key for the swap
            from app.utils.solana_tx import keypair_from_base58

            keypair = keypair_from_base58(wallet_private_key)
            user_public_key = str(keypair.pubkey())

            # Check quote freshness before submitting swap
            # Re-fetch if stale to avoid expired quote errors
            if not quote.is_fresh():
                logger.info(
                    f"Quote is stale ({quote.age_seconds():.1f}s old), re-fetching before swap"
                )
                quote = await self.get_jupiter_quote(lamports)
                if not quote:
                    return BuybackResult(
                        success=False,
                        tx_signature=None,
                        sol_spent=Decimal(0),
                        copper_received=0,
                        price_per_token=None,
                        error="Failed to re-fetch Jupiter quote after expiration",
                    )

            # Get swap transaction from Jupiter
            swap_response = await self.client.post(
                JUPITER_SWAP_API,
                json={
                    "quoteResponse": quote.data,
                    "userPublicKey": user_public_key,
                    "wrapAndUnwrapSol": True,
                    "dynamicComputeUnitLimit": True,
                    "prioritizationFeeLamports": "auto",
                },
            )
            swap_response.raise_for_status()
            swap_data = swap_response.json()

            swap_tx = swap_data.get("swapTransaction")
            if not swap_tx:
                return BuybackResult(
                    success=False,
                    tx_signature=None,
                    sol_spent=Decimal(0),
                    copper_received=0,
                    price_per_token=None,
                    error="No swap transaction returned from Jupiter",
                )

            # Sign and send the transaction
            tx_result = await sign_and_send_transaction(
                serialized_tx=swap_tx,
                private_key=wallet_private_key,
                skip_preflight=False,
            )

            if not tx_result.success:
                return BuybackResult(
                    success=False,
                    tx_signature=None,
                    sol_spent=Decimal(0),
                    copper_received=0,
                    price_per_token=None,
                    error=tx_result.error or "Transaction failed",
                )

            # Wait for confirmation
            confirmed = await confirm_transaction(
                tx_result.signature, timeout_seconds=30
            )
            if not confirmed:
                logger.warning(
                    f"Transaction sent but not confirmed: {tx_result.signature}"
                )

            # Calculate results from quote
            out_amount = int(quote.data.get("outAmount", 0))
            price_per_token = None
            if out_amount > 0:
                price_per_token = sol_amount / Decimal(out_amount)

            logger.info(
                f"Swap executed: {tx_result.signature}, "
                f"{sol_amount} SOL → {out_amount} GOLD"
            )

            return BuybackResult(
                success=True,
                tx_signature=tx_result.signature,
                sol_spent=sol_amount,
                copper_received=out_amount,
                price_per_token=price_per_token,
            )

        except Exception as e:
            # SECURITY: Do not use exc_info=True to avoid exposing private key bytes in stack traces
            logger.error(f"Error executing swap: {type(e).__name__}: {e}")
            return BuybackResult(
                success=False,
                tx_signature=None,
                sol_spent=Decimal(0),
                copper_received=0,
                price_per_token=None,
                error=str(e),
            )

    async def record_buyback(
        self,
        tx_signature: str,
        sol_amount: Decimal,
        gold_amount: int,
        price_per_token: Optional[Decimal] = None,
    ) -> Buyback:
        """
        Record a buyback transaction in the database.

        Args:
            tx_signature: Solana transaction signature.
            sol_amount: SOL spent.
            gold_amount: GOLD received.
            price_per_token: Price per GOLD token in SOL.

        Returns:
            Created Buyback record.
        """
        buyback = Buyback(
            tx_signature=tx_signature,
            sol_amount=sol_amount,
            gold_amount=gold_amount,
            price_per_token=price_per_token,
            executed_at=utc_now(),
        )
        self.db.add(buyback)

        # Update system stats
        await self._update_system_stats(sol_amount)

        await self.db.commit()

        logger.info(
            f"Recorded buyback: {tx_signature}, "
            f"{sol_amount} SOL → {gold_amount} GOLD"
        )
        return buyback

    async def mark_rewards_processed(self, reward_ids: list) -> None:
        """
        Mark creator rewards as processed.

        Args:
            reward_ids: List of reward IDs to mark.
        """
        result = await self.db.execute(
            select(CreatorReward).where(CreatorReward.id.in_(reward_ids))
        )
        rewards = result.scalars().all()

        for reward in rewards:
            reward.processed = True

        await self.db.commit()
        logger.info(f"Marked {len(reward_ids)} rewards as processed")

    async def record_creator_reward(
        self, amount_sol: Decimal, source: str, tx_signature: Optional[str] = None
    ) -> Optional[CreatorReward]:
        """
        Record an incoming creator reward with idempotency check.

        If tx_signature is provided and already exists, returns the existing
        record to prevent duplicate processing from webhook retries.

        Args:
            amount_sol: Amount of SOL received.
            source: Source of reward ('pumpfun' or 'pumpswap').
            tx_signature: Transaction signature.

        Returns:
            Created or existing CreatorReward record, or None if duplicate.
        """
        # Idempotency check: if tx_signature exists, return existing record
        if tx_signature:
            result = await self.db.execute(
                select(CreatorReward).where(CreatorReward.tx_signature == tx_signature)
            )
            existing = result.scalar_one_or_none()
            if existing:
                logger.info(
                    f"Creator reward already exists for tx {tx_signature}, skipping duplicate"
                )
                return existing

        reward = CreatorReward(
            amount_sol=amount_sol,
            source=source,
            tx_signature=tx_signature,
            received_at=utc_now(),
        )
        self.db.add(reward)
        await self.db.commit()

        logger.info(
            f"Recorded creator reward: {amount_sol} SOL from {source} (tx: {tx_signature})"
        )
        return reward

    async def get_recent_buybacks(self, limit: int = 10) -> list[Buyback]:
        """
        Get recent buyback transactions.

        Args:
            limit: Maximum number to return.

        Returns:
            List of recent Buyback records.
        """
        result = await self.db.execute(
            select(Buyback).order_by(Buyback.executed_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_buybacks(self) -> tuple[Decimal, int]:
        """
        Get total buyback statistics.

        Returns:
            Tuple of (total_sol_spent, total_copper_bought).
        """
        result = await self.db.execute(
            select(func.sum(Buyback.sol_amount), func.sum(Buyback.gold_amount))
        )
        row = result.one()
        return (Decimal(row[0]) if row[0] else Decimal(0), int(row[1]) if row[1] else 0)

    async def _update_system_stats(self, sol_amount: Decimal):
        """Update system stats with buyback amount using atomic UPDATE."""
        from sqlalchemy import update

        # Use atomic UPDATE to prevent lost updates under concurrency
        await self.db.execute(
            update(SystemStats)
            .where(SystemStats.id == 1)
            .values(
                total_buybacks=func.coalesce(SystemStats.total_buybacks, 0)
                + sol_amount,
                updated_at=utc_now(),
            )
        )


async def transfer_to_team_wallet(
    amount_sol: Decimal, from_private_key: str, to_address: str
) -> Optional[str]:
    """
    Transfer SOL to team wallet (10% of creator rewards).

    Args:
        amount_sol: Amount of SOL to transfer.
        from_private_key: Private key of source wallet.
        to_address: Team wallet public address.

    Returns:
        Transaction signature if successful, None otherwise.
    """
    if not from_private_key or not to_address:
        logger.error("Team wallet transfer: missing private key or address")
        return None

    if amount_sol <= 0:
        logger.warning("Team wallet transfer: amount is zero or negative")
        return None

    lamports = int(amount_sol * LAMPORTS_PER_SOL)

    result = await send_sol_transfer(
        from_private_key=from_private_key,
        to_address=to_address,
        amount_lamports=lamports,
    )

    if result.success:
        logger.info(f"Team wallet transfer: {result.signature}, {amount_sol} SOL")
        return result.signature
    else:
        logger.error(f"Team wallet transfer failed: {result.error}")
        return None


async def process_pending_rewards(db: AsyncSession) -> Optional[BuybackResult]:
    """
    Process all pending creator rewards.

    Main entry point for the buyback task.
    - 80% goes to airdrop pool:
      - 20% of that swapped to GOLD (buyback)
      - 80% of that kept as SOL (reserves/fees)
    - 10% goes to algo bot wallet for trading operations
    - 10% goes to team wallet for maintenance

    Args:
        db: Database session.

    Returns:
        BuybackResult if buyback was executed, None if no rewards.
    """
    service = BuybackService(db)

    # Get unprocessed rewards
    rewards = await service.get_unprocessed_rewards()
    if not rewards:
        logger.info("No pending rewards to process")
        return None

    total_sol = sum(r.amount_sol for r in rewards)
    split = service.calculate_split(total_sol)

    logger.info(
        f"Processing {len(rewards)} rewards: "
        f"total={split.total_sol} SOL, "
        f"buyback={split.buyback_sol} SOL, "
        f"algo_bot={split.algo_bot_sol} SOL, "
        f"team={split.team_sol} SOL"
    )

    # Step 1: Transfer 80% SOL from CREATOR → AIRDROP_POOL for buyback
    pool_transfer_tx = None
    pool_transfer_confirmed = False
    if settings.airdrop_pool_private_key and settings.creator_wallet_private_key:
        from app.utils.solana_tx import keypair_from_base58

        pool_keypair = keypair_from_base58(settings.airdrop_pool_private_key)
        pool_address = str(pool_keypair.pubkey())

        pool_transfer_tx = await transfer_to_team_wallet(
            amount_sol=split.buyback_sol,
            from_private_key=settings.creator_wallet_private_key,
            to_address=pool_address,
        )
        if pool_transfer_tx:
            logger.info(f"Pool transfer sent: {pool_transfer_tx}, {split.buyback_sol} SOL")
            # Wait for confirmation before swapping
            pool_transfer_confirmed = await confirm_transaction(
                pool_transfer_tx, timeout_seconds=30
            )
            if pool_transfer_confirmed:
                logger.info(f"Pool transfer confirmed: {pool_transfer_tx}")
            else:
                logger.error(f"Pool transfer not confirmed: {pool_transfer_tx}")
        else:
            logger.error("Pool transfer failed to send")
    else:
        logger.error("Pool transfer skipped: missing configuration")

    # Step 2: Execute buyback swap from AIRDROP_POOL (SOL → GOLD)
    result = BuybackResult(
        success=False,
        tx_signature=None,
        sol_spent=Decimal(0),
        copper_received=0,
        price_per_token=None,
        error="Pool transfer failed or not confirmed",
    )

    if pool_transfer_confirmed:
        # Swap 20% of transferred SOL to GOLD, keep 80% as SOL reserves
        swap_amount = split.buyback_sol * Decimal("0.20")
        result = await service.execute_swap(
            swap_amount, settings.airdrop_pool_private_key
        )

    buyback_success = result.success and result.tx_signature

    if buyback_success:
        # Record buyback
        await service.record_buyback(
            result.tx_signature,
            result.sol_spent,
            result.copper_received,
            result.price_per_token,
        )
        logger.info(f"Buyback recorded: {result.tx_signature}")

        # Emit pool:updated WebSocket event
        try:
            from app.services.distribution import DistributionService

            dist_service = DistributionService(db)
            pool_status = await dist_service.get_pool_status()

            # Calculate progress to threshold
            threshold_usd = settings.distribution_threshold_usd
            progress = (
                min(100.0, float(pool_status.value_usd / threshold_usd * 100))
                if threshold_usd > 0
                else 0.0
            )

            # Calculate hours until time trigger
            hours_until = None
            if pool_status.hours_since_last is not None:
                hours_until = max(
                    0.0, settings.distribution_max_hours - pool_status.hours_since_last
                )

            await emit_pool_updated(
                balance=pool_status.balance,
                value_usd=float(pool_status.value_usd),
                progress_to_threshold=progress,
                threshold_met=pool_status.threshold_met,
                hours_until_time_trigger=hours_until,
            )
            logger.info("Emitted pool:updated WebSocket event")
        except Exception as e:
            # Never block buyback on WebSocket failures
            logger.warning(f"Failed to emit pool:updated event: {e}")
    else:
        logger.error(f"Buyback failed: {result.error}")

    # Transfer 10% to algo bot wallet
    algo_bot_tx = None
    if settings.algo_bot_wallet_public_key and settings.creator_wallet_private_key:
        algo_bot_tx = await transfer_to_team_wallet(
            amount_sol=split.algo_bot_sol,
            from_private_key=settings.creator_wallet_private_key,
            to_address=settings.algo_bot_wallet_public_key,
        )
        if algo_bot_tx:
            logger.info(f"Algo bot wallet transfer: {algo_bot_tx}")
        else:
            logger.warning("Algo bot wallet transfer failed or skipped")
    else:
        logger.warning("Algo bot wallet transfer skipped: missing configuration")

    # Transfer 10% to team wallet (maintenance)
    team_tx = None
    if settings.team_wallet_public_key and settings.creator_wallet_private_key:
        team_tx = await transfer_to_team_wallet(
            amount_sol=split.team_sol,
            from_private_key=settings.creator_wallet_private_key,
            to_address=settings.team_wallet_public_key,
        )
        if team_tx:
            logger.info(f"Team wallet transfer: {team_tx}")
        else:
            logger.warning("Team wallet transfer failed or skipped")
    else:
        logger.warning("Team wallet transfer skipped: missing configuration")

    # Mark rewards as processed if at least one operation succeeded
    if buyback_success or algo_bot_tx or team_tx:
        reward_ids = [r.id for r in rewards]
        await service.mark_rewards_processed(reward_ids)
        logger.info(f"Marked {len(reward_ids)} rewards as processed")

    return result

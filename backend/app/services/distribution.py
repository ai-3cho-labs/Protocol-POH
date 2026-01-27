"""
$GOLD Distribution Service

Handles GOLD token distribution to CPU holders based on Hash Power.
Triggers: Pool reaches $250 USD OR 24 hours since last distribution.
"""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

from sqlalchemy import select, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import OperationalError

from app.models import (
    Distribution,
    DistributionRecipient,
    DistributionLock,
    SystemStats,
)
from app.services.twab import TWABService
from app.services.helius import get_helius_service
from app.utils.http_client import get_http_client
from app.utils.solana_tx import send_spl_token_transfer, batch_confirm_transactions
from app.utils.price_cache import get_gold_price_usd as get_cached_gold_price
from app.config import get_settings, GOLD_MULTIPLIER, TOKEN_MULTIPLIER
from app.websocket import emit_distribution_executed

logger = logging.getLogger(__name__)
settings = get_settings()


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


@dataclass
class DistributionPlan:
    """Planned distribution before execution."""

    pool_amount: int  # Raw token amount
    pool_value_usd: Decimal
    total_hashpower: Decimal
    recipient_count: int
    trigger_type: str  # 'threshold' or 'time'
    recipients: list["RecipientShare"]


@dataclass
class RecipientShare:
    """Individual recipient's share in a distribution."""

    wallet: str
    twab: int
    multiplier: float
    hash_power: Decimal
    share_percentage: Decimal
    amount: int  # Raw token amount


@dataclass
class PoolStatus:
    """Current pool status."""

    balance: int  # Raw token amount
    balance_formatted: float  # Human readable
    value_usd: Decimal
    last_distribution: Optional[datetime]
    hours_since_last: Optional[float]
    threshold_met: bool
    time_trigger_met: bool
    should_distribute: bool


class DistributionService:
    """Service for managing token distributions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.twab_service = TWABService(db)
        self.helius = get_helius_service()

    @property
    def client(self):
        """Get shared HTTP client."""
        return get_http_client()

    async def get_pool_balance(self) -> int:
        """
        Get current airdrop pool balance.

        Returns:
            Raw token balance of airdrop pool wallet.
        """
        # Test mode: return mock balance
        if settings.test_mode:
            return int(settings.test_pool_balance * TOKEN_MULTIPLIER)

        # Fetch from Helius
        try:
            # Derive airdrop pool public key from private key
            pool_wallet = self._get_airdrop_pool_address()
            if not pool_wallet:
                logger.warning("Airdrop pool wallet not configured")
                return 0

            accounts = await self.helius.get_token_accounts(settings.gold_token_mint)

            for account in accounts:
                if account.wallet == pool_wallet:
                    return account.balance

            return 0

        except Exception as e:
            logger.error(f"Error fetching pool balance: {e}")
            return 0

    def _get_airdrop_pool_address(self) -> Optional[str]:
        """
        Get the airdrop pool wallet public address from private key.

        Returns:
            Public key string, or None if not configured.
        """
        if not settings.airdrop_pool_private_key:
            return None

        try:
            from app.utils.solana_tx import keypair_from_base58

            keypair = keypair_from_base58(settings.airdrop_pool_private_key)
            return str(keypair.pubkey())
        except Exception as e:
            logger.error(f"Error deriving airdrop pool address: {e}")
            return None

    async def get_gold_price_usd(self) -> Decimal:
        """
        Get current GOLD price in USD.

        Uses cached price with fallback to multiple price feeds.

        Returns:
            Price per token in USD.
        """
        if not settings.gold_token_mint:
            return Decimal(0)

        try:
            # Use cached price with fallback support
            price = await get_cached_gold_price(use_fallback=True)
            return price

        except Exception as e:
            logger.error(f"Error fetching GOLD price: {e}")
            return Decimal(0)

    async def get_pool_value_usd(self) -> Decimal:
        """
        Get current pool value in USD.

        Returns:
            Pool value in USD.
        """
        # Test mode: return mock USD value
        if settings.test_mode:
            return Decimal(str(settings.test_pool_value_usd))

        balance = await self.get_pool_balance()
        price = await self.get_gold_price_usd()

        # Convert raw balance to token amount (GOLD pool uses GOLD_MULTIPLIER)
        tokens = Decimal(balance) / GOLD_MULTIPLIER
        return tokens * price

    async def get_last_distribution(self) -> Optional[Distribution]:
        """
        Get the most recent distribution.

        Returns:
            Last Distribution record, or None.
        """
        result = await self.db.execute(
            select(Distribution).order_by(Distribution.executed_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_pool_status(self) -> PoolStatus:
        """
        Get complete pool status including trigger checks.

        Returns:
            PoolStatus with all relevant info.
        """
        balance = await self.get_pool_balance()
        value_usd = await self.get_pool_value_usd()
        last_dist = await self.get_last_distribution()

        # Calculate time since last distribution
        hours_since = None
        if settings.test_mode:
            # Test mode: use mock hours
            hours_since = settings.test_hours_since_distribution
        elif last_dist:
            delta = utc_now() - last_dist.executed_at
            hours_since = delta.total_seconds() / 3600

        # Check triggers
        threshold_met = value_usd >= settings.distribution_threshold_usd
        time_trigger_met = (
            hours_since is None or hours_since >= settings.distribution_max_hours
        )

        return PoolStatus(
            balance=balance,
            balance_formatted=float(Decimal(balance) / GOLD_MULTIPLIER),
            value_usd=value_usd,
            last_distribution=last_dist.executed_at if last_dist else None,
            hours_since_last=hours_since,
            threshold_met=threshold_met,
            time_trigger_met=time_trigger_met,
            should_distribute=threshold_met or time_trigger_met,
        )

    async def should_distribute(self) -> tuple[bool, str]:
        """
        Check if distribution should be triggered.

        Returns:
            Tuple of (should_distribute, trigger_type).
        """
        status = await self.get_pool_status()

        if status.threshold_met:
            return True, "threshold"
        if status.time_trigger_met:
            return True, "time"

        return False, ""

    async def calculate_distribution(
        self, pool_amount: Optional[int] = None
    ) -> Optional[DistributionPlan]:
        """
        Calculate distribution shares for all eligible wallets.

        Args:
            pool_amount: Override pool amount (for testing).

        Returns:
            DistributionPlan with all recipient shares.
        """
        # Get pool info
        if pool_amount is None:
            pool_amount = await self.get_pool_balance()

        if pool_amount <= 0:
            logger.warning("Pool is empty, cannot distribute")
            return None

        pool_value_usd = await self.get_pool_value_usd()

        # Determine trigger type
        should, trigger_type = await self.should_distribute()
        if not should:
            trigger_type = "manual"  # Allow manual distributions

        # Calculate period (since last distribution or 24h)
        last_dist = await self.get_last_distribution()
        end = utc_now()

        if last_dist:
            start = last_dist.executed_at
        else:
            start = end - timedelta(hours=24)

        # Get minimum balance threshold (convert USD to CPU tokens)
        price = await self.get_gold_price_usd()
        min_balance_tokens = 0
        if price > 0:
            min_balance_tokens = int(
                (Decimal(settings.min_balance_usd) / price) * TOKEN_MULTIPLIER
            )

        # Calculate hash powers for all wallets
        hash_powers = await self.twab_service.calculate_all_hash_powers(
            start, end, min_balance=min_balance_tokens
        )

        if not hash_powers:
            logger.warning("No eligible wallets for distribution")
            return None

        # Calculate total hash power
        total_hp = sum(hp.hash_power for hp in hash_powers)

        # SAFETY: Guard against division by zero
        # This can happen if all wallets have 0 hash power (no TWAB or all at tier 1 with 0 balance)
        if total_hp <= 0:
            logger.warning(
                "Total hash power is zero or negative, cannot calculate distribution shares"
            )
            return None

        # Calculate shares with precision remainder distribution
        # First pass: calculate truncated amounts
        recipients = []
        for hp in hash_powers:
            # SAFETY: total_hp is guaranteed > 0 here due to guard above
            share_pct = hp.hash_power / total_hp
            amount = int(Decimal(pool_amount) * share_pct)

            # Include all recipients, even with 0 amount initially
            # (they may receive remainder tokens)
            recipients.append(
                RecipientShare(
                    wallet=hp.wallet,
                    twab=hp.twab,
                    multiplier=hp.multiplier,
                    hash_power=hp.hash_power,
                    share_percentage=share_pct * 100,
                    amount=amount,
                )
            )

        # Second pass: distribute remainder to largest holder(s)
        # Truncation loses ~1 token per recipient on average
        total_distributed = sum(r.amount for r in recipients)
        remainder = pool_amount - total_distributed

        if remainder > 0 and recipients:
            # Sort by hash power descending to give remainder to top holders
            recipients.sort(key=lambda x: x.hash_power, reverse=True)

            # Distribute remainder 1 token at a time to top holders
            for i in range(remainder):
                idx = i % len(recipients)
                # Create new RecipientShare with updated amount (dataclass is immutable-ish)
                r = recipients[idx]
                recipients[idx] = RecipientShare(
                    wallet=r.wallet,
                    twab=r.twab,
                    multiplier=r.multiplier,
                    hash_power=r.hash_power,
                    share_percentage=r.share_percentage,
                    amount=r.amount + 1,
                )

            logger.debug(
                f"Distributed {remainder} remainder tokens to top {min(remainder, len(recipients))} holders"
            )

        # Filter out recipients with 0 amount
        recipients = [r for r in recipients if r.amount > 0]

        return DistributionPlan(
            pool_amount=pool_amount,
            pool_value_usd=pool_value_usd,
            total_hashpower=total_hp,
            recipient_count=len(recipients),
            trigger_type=trigger_type,
            recipients=recipients,
        )

    async def execute_distribution(
        self, plan: DistributionPlan
    ) -> Optional[Distribution]:
        """
        Execute a distribution plan (send tokens to recipients).

        Args:
            plan: DistributionPlan to execute.

        Returns:
            Distribution record if successful.
        """
        try:
            # Create distribution record
            distribution = Distribution(
                pool_amount=plan.pool_amount,
                pool_value_usd=plan.pool_value_usd,
                total_hashpower=plan.total_hashpower,
                recipient_count=plan.recipient_count,
                trigger_type=plan.trigger_type,
                executed_at=utc_now(),
            )
            self.db.add(distribution)
            await self.db.flush()

            # Execute GOLD token transfers and collect results
            transfer_results = {}
            if settings.airdrop_pool_private_key and settings.gold_token_mint:
                transfer_results = await self._execute_token_transfers(plan.recipients)
            else:
                logger.warning(
                    "Token transfers skipped: missing airdrop_pool_private_key or gold_token_mint"
                )

            # BULK INSERT: Create all recipient records at once
            # Only record amount_received for successful transfers (tx_signature present)
            # Failed transfers get amount_received=0 for reconciliation
            if plan.recipients:
                recipient_data = [
                    {
                        "distribution_id": distribution.id,
                        "wallet": r.wallet,
                        "twab": r.twab,
                        "multiplier": Decimal(str(r.multiplier)),
                        "hash_power": r.hash_power,
                        "amount_received": r.amount
                        if transfer_results.get(r.wallet)
                        else 0,
                        "tx_signature": transfer_results.get(r.wallet),
                    }
                    for r in plan.recipients
                ]
                await self.db.execute(insert(DistributionRecipient), recipient_data)

                # Log failed transfers for reconciliation
                failed_transfers = [
                    r.wallet
                    for r in plan.recipients
                    if not transfer_results.get(r.wallet)
                ]
                if failed_transfers:
                    logger.warning(
                        f"Distribution {distribution.id}: {len(failed_transfers)} transfers failed, "
                        f"need reconciliation: {failed_transfers[:5]}{'...' if len(failed_transfers) > 5 else ''}"
                    )

            # Update system stats
            await self._update_system_stats(distribution)

            await self.db.commit()

            # Count successful transfers
            successful_transfers = sum(1 for v in transfer_results.values() if v)
            logger.info(
                f"Distribution executed: id={distribution.id}, "
                f"recipients={plan.recipient_count}, "
                f"transfers_sent={successful_transfers}, "
                f"pool={plan.pool_amount}"
            )

            # Emit WebSocket event (after commit)
            top_5 = [
                (r.wallet, r.amount, i + 1)
                for i, r in enumerate(
                    sorted(plan.recipients, key=lambda x: x.amount, reverse=True)[:5]
                )
            ]
            await emit_distribution_executed(
                distribution_id=str(distribution.id),
                pool_amount=plan.pool_amount,
                pool_value_usd=float(plan.pool_value_usd),
                recipient_count=plan.recipient_count,
                trigger_type=plan.trigger_type,
                top_recipients=top_5,
                executed_at=distribution.executed_at,
            )

            return distribution

        except Exception as e:
            logger.error(f"Error executing distribution: {e}", exc_info=True)
            await self.db.rollback()
            return None

    async def _execute_token_transfers(
        self, recipients: list[RecipientShare]
    ) -> dict[str, Optional[str]]:
        """
        Execute token transfers to all recipients sequentially with rate limiting.

        Processes transfers one at a time with delays to avoid RPC rate limits (429s),
        then uses batch confirmation to verify all transactions efficiently.

        Args:
            recipients: List of recipients with wallet and amount.

        Returns:
            Dict mapping wallet addresses to transaction signatures (or None if failed).
        """
        import asyncio

        # Rate limiting: 150ms between transfers = ~6.6 transfers/second
        # Well under Helius 10 RPS limit, leaving headroom for other calls
        TRANSFER_DELAY_SECONDS = 0.15

        results: dict[str, Optional[str]] = {}
        token_mint = settings.gold_token_mint  # Distribute GOLD tokens
        private_key = settings.airdrop_pool_private_key

        if not token_mint or not private_key:
            logger.error(
                "Cannot execute transfers: missing gold_token_mint or private_key"
            )
            return results

        # Collect pending signatures for batch confirmation
        pending_signatures: list[tuple[str, str]] = []  # (wallet, signature)
        total = len(recipients)

        logger.info(f"Executing {total} token transfers sequentially")

        # Process transfers sequentially with delays
        for idx, recipient in enumerate(recipients):
            try:
                result = await send_spl_token_transfer(
                    from_private_key=private_key,
                    to_address=recipient.wallet,
                    token_mint=token_mint,
                    amount=recipient.amount,
                )

                if result.success and result.signature:
                    # Don't confirm inline - collect for batch confirmation
                    pending_signatures.append((recipient.wallet, result.signature))
                    results[recipient.wallet] = result.signature
                    logger.debug(
                        f"Transfer sent ({idx + 1}/{total}): {recipient.wallet[:16]}..."
                    )
                else:
                    logger.error(
                        f"Transfer failed to {recipient.wallet}: {result.error}"
                    )
                    results[recipient.wallet] = None

            except Exception as e:
                logger.error(f"Transfer error to {recipient.wallet}: {e}")
                results[recipient.wallet] = None

            # Delay between transfers (except after the last one)
            if idx < total - 1:
                await asyncio.sleep(TRANSFER_DELAY_SECONDS)

        # Batch confirm all sent transactions
        if pending_signatures:
            signatures_to_confirm = [sig for _, sig in pending_signatures]
            wallet_by_sig = {sig: wallet for wallet, sig in pending_signatures}

            logger.info(f"Batch confirming {len(signatures_to_confirm)} transactions")

            confirmation_results = await batch_confirm_transactions(
                signatures_to_confirm,
                timeout_seconds=30,
                poll_interval=2.0,
            )

            # Update results based on confirmation status
            for sig, confirmed in confirmation_results.items():
                wallet = wallet_by_sig.get(sig)
                if wallet:
                    if not confirmed:
                        # Transaction was sent but failed/timed out on confirmation
                        # Keep the signature in results for manual verification
                        logger.warning(
                            f"Transfer unconfirmed (may still succeed): {wallet[:16]}... -> {sig[:16]}..."
                        )

        successful = sum(1 for v in results.values() if v)
        logger.info(
            f"Token transfers complete: {successful}/{len(recipients)} successful"
        )

        return results

    async def get_recent_distributions(self, limit: int = 10) -> list[Distribution]:
        """
        Get recent distributions.

        Args:
            limit: Maximum number to return.

        Returns:
            List of recent Distribution records.
        """
        result = await self.db.execute(
            select(Distribution).order_by(Distribution.executed_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_wallet_distributions(
        self, wallet: str, limit: int = 10
    ) -> list[DistributionRecipient]:
        """
        Get distribution history for a wallet.

        Args:
            wallet: Wallet address.
            limit: Maximum number to return.

        Returns:
            List of DistributionRecipient records.
        """
        result = await self.db.execute(
            select(DistributionRecipient)
            .join(Distribution)
            .options(selectinload(DistributionRecipient.distribution))
            .where(DistributionRecipient.wallet == wallet)
            .order_by(Distribution.executed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_distributed(self) -> int:
        """
        Get total tokens distributed.

        Returns:
            Total raw token amount distributed.
        """
        result = await self.db.execute(select(func.sum(Distribution.pool_amount)))
        total = result.scalar_one_or_none()
        return int(total) if total else 0

    async def get_distribution_stats(self) -> dict:
        """
        Get distribution statistics.

        Returns:
            Dict with distribution stats.
        """
        result = await self.db.execute(
            select(
                func.count(Distribution.id),
                func.sum(Distribution.pool_amount),
                func.sum(Distribution.recipient_count),
            )
        )
        row = result.one()

        return {
            "total_distributions": row[0] or 0,
            "total_distributed": row[1] or 0,
            "total_recipients": row[2] or 0,
        }

    async def get_failed_transfers(
        self, distribution_id: Optional[str] = None
    ) -> list[DistributionRecipient]:
        """
        Get distribution recipients with failed transfers for reconciliation.

        Args:
            distribution_id: Optional distribution ID to filter by.

        Returns:
            List of DistributionRecipient records with tx_signature=NULL.
        """
        query = select(DistributionRecipient).where(
            DistributionRecipient.tx_signature.is_(None)
        )

        if distribution_id:
            query = query.where(
                DistributionRecipient.distribution_id == distribution_id
            )

        result = await self.db.execute(
            query.options(selectinload(DistributionRecipient.distribution)).order_by(
                DistributionRecipient.id.asc()
            )
        )
        return list(result.scalars().all())

    async def retry_failed_transfer(
        self, recipient: DistributionRecipient, planned_amount: int
    ) -> bool:
        """
        Retry a failed transfer for reconciliation.

        Args:
            recipient: DistributionRecipient with failed transfer.
            planned_amount: Original planned amount to transfer.

        Returns:
            True if retry succeeded, False otherwise.
        """
        if recipient.tx_signature:
            logger.warning(f"Transfer already succeeded for {recipient.wallet}")
            return True

        if not settings.airdrop_pool_private_key or not settings.gold_token_mint:
            logger.error(
                "Cannot retry transfer: missing airdrop_pool_private_key or gold_token_mint"
            )
            return False

        try:
            result = await send_spl_token_transfer(
                from_private_key=settings.airdrop_pool_private_key,
                to_address=recipient.wallet,
                token_mint=settings.gold_token_mint,  # Distribute GOLD tokens
                amount=planned_amount,
            )

            if result.success:
                confirmed = await confirm_transaction(
                    result.signature, timeout_seconds=30
                )
                if confirmed or result.signature:
                    # Update the recipient record
                    recipient.tx_signature = result.signature
                    recipient.amount_received = planned_amount
                    await self.db.commit()
                    logger.info(
                        f"Reconciliation transfer confirmed: {recipient.wallet} -> {result.signature}"
                    )
                    return True

            logger.error(
                f"Reconciliation transfer failed for {recipient.wallet}: {result.error}"
            )
            return False

        except Exception as e:
            logger.error(f"Reconciliation transfer error for {recipient.wallet}: {e}")
            return False

    async def _update_system_stats(self, distribution: Distribution):
        """Update system stats with distribution info using atomic UPDATE."""
        from sqlalchemy import update

        # Use atomic UPDATE to prevent lost updates under concurrency
        await self.db.execute(
            update(SystemStats)
            .where(SystemStats.id == 1)
            .values(
                total_distributed=func.coalesce(SystemStats.total_distributed, 0)
                + distribution.pool_amount,
                last_distribution_at=distribution.executed_at,
                updated_at=utc_now(),
            )
        )


async def acquire_distribution_lock(
    db: AsyncSession, worker_id: str = "celery"
) -> bool:
    """
    Acquire exclusive lock for distribution execution.

    Uses SELECT FOR UPDATE NOWAIT to prevent race conditions where
    multiple Celery workers could execute the same distribution twice.

    Args:
        db: Database session.
        worker_id: Identifier for the worker acquiring the lock.

    Returns:
        True if lock acquired, False if another worker holds it.
    """
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.exc import IntegrityError

    try:
        # Ensure lock row exists using upsert (race-condition safe)
        # This handles the case where migration hasn't been run yet
        try:
            stmt = pg_insert(DistributionLock).values(id=1)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            await db.execute(stmt)
            await db.flush()
        except IntegrityError:
            # Row already exists, which is fine
            pass

        # SELECT FOR UPDATE NOWAIT will raise an error if the row is already locked
        result = await db.execute(
            select(DistributionLock)
            .where(DistributionLock.id == 1)
            .with_for_update(nowait=True)
        )
        lock = result.scalar_one_or_none()

        if lock is None:
            # This should not happen after the upsert above
            logger.error(
                "Distribution lock row not found after upsert - database issue"
            )
            return False

        # Update lock metadata for debugging/monitoring
        lock.locked_at = datetime.now(timezone.utc)
        lock.locked_by = worker_id
        await db.flush()

        return True

    except OperationalError as e:
        # NOWAIT raises OperationalError if row is locked
        # PostgreSQL error code 55P03 = lock_not_available
        if "could not obtain lock" in str(e) or "55P03" in str(e):
            logger.info("Distribution lock held by another worker, skipping")
            return False
        # Re-raise other operational errors
        raise


async def check_and_distribute(db: AsyncSession) -> Optional[Distribution]:
    """
    Check triggers and execute distribution if needed.

    Main entry point for the distribution task. Uses SELECT FOR UPDATE NOWAIT
    to prevent race conditions where multiple workers could distribute twice.

    Args:
        db: Database session.

    Returns:
        Distribution record if executed, None otherwise.
    """
    import socket

    worker_id = f"celery@{socket.gethostname()}"

    # Acquire exclusive lock to prevent double distribution
    if not await acquire_distribution_lock(db, worker_id):
        logger.info("Another worker is processing distribution, skipping")
        return None

    # Lock acquired - proceed with distribution check and execution
    # The lock is held until the transaction commits or rolls back
    service = DistributionService(db)

    should, trigger = await service.should_distribute()

    if not should:
        logger.info("Distribution not triggered")
        # Commit to release the lock cleanly
        await db.commit()
        return None

    logger.info(f"Distribution triggered by: {trigger}")

    plan = await service.calculate_distribution()
    if not plan:
        logger.warning("Could not create distribution plan")
        await db.commit()
        return None

    # execute_distribution commits on success, rolls back on failure
    # Either way, the lock is released
    return await service.execute_distribution(plan)

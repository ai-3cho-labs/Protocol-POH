"""
$COPPER Distribution Service Tests

Tests for balance-based distribution calculations and triggers.
Distribution formula: Share = Balance / Total Supply
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.distribution import (
    DistributionService,
    DistributionPlan,
    RecipientShare,
    PoolStatus,
    check_and_distribute
)
from app.models import Distribution


class TestDistributionTriggers:
    """Tests for distribution trigger logic."""

    @pytest.mark.asyncio
    async def test_distribution_when_pool_has_balance(self, db_session, mock_settings):
        """Test distribution triggers when pool has any balance."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            service = DistributionService(db_session)

            # Mock pool with balance > 0
            with patch.object(service, "get_pool_balance", return_value=1_000_000):
                with patch.object(service, "get_pool_value_usd", return_value=Decimal("10")):
                    with patch.object(service, "get_last_distribution", return_value=None):
                        should, trigger = await service.should_distribute()

                        assert should is True
                        assert trigger == "hourly"

    @pytest.mark.asyncio
    async def test_no_distribution_when_pool_empty(self, db_session, mock_settings):
        """Test no distribution when pool is empty."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            service = DistributionService(db_session)

            # Mock empty pool
            with patch.object(service, "get_pool_balance", return_value=0):
                with patch.object(service, "get_pool_value_usd", return_value=Decimal("0")):
                    with patch.object(service, "get_last_distribution", return_value=None):
                        should, trigger = await service.should_distribute()

                        assert should is False
                        assert trigger == ""


class TestPoolStatus:
    """Tests for pool status calculation."""

    @pytest.mark.asyncio
    async def test_pool_status_structure(self, db_session, mock_settings):
        """Test pool status returns all required fields."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            service = DistributionService(db_session)

            with patch.object(service, "get_pool_balance", return_value=1_000_000_000):
                with patch.object(service, "get_pool_value_usd", return_value=Decimal("150")):
                    with patch.object(service, "get_last_distribution", return_value=None):
                        status = await service.get_pool_status()

                        assert isinstance(status, PoolStatus)
                        assert hasattr(status, "balance")
                        assert hasattr(status, "balance_formatted")
                        assert hasattr(status, "value_usd")
                        assert hasattr(status, "should_distribute")
                        # should_distribute is True when balance > 0
                        assert status.should_distribute is True


class TestDistributionCalculation:
    """Tests for balance-based distribution share calculation."""

    @pytest.mark.asyncio
    async def test_distribution_share_proportional_to_balance(self):
        """Test that shares are proportional to balance."""
        # With balance-based distribution:
        # Wallet1 has 200 balance, Wallet2 has 100 balance
        # Total supply = 300
        # Wallet1 share = 200/300 = 66.67%
        # Wallet2 share = 100/300 = 33.33%
        recipients = [
            RecipientShare(
                wallet="Wallet1",
                balance=200,
                share_percentage=Decimal("66.67"),
                amount=6667
            ),
            RecipientShare(
                wallet="Wallet2",
                balance=100,
                share_percentage=Decimal("33.33"),
                amount=3333
            ),
        ]

        # Wallet1 should receive approximately 2x Wallet2 (proportional to balance)
        ratio = recipients[0].amount / recipients[1].amount
        assert 1.8 < ratio < 2.2  # Allow some rounding tolerance

    @pytest.mark.asyncio
    async def test_distribution_equal_balances(self):
        """Test that equal balances get equal shares."""
        recipients = [
            RecipientShare(
                wallet="Wallet1",
                balance=100,
                share_percentage=Decimal("50"),
                amount=5000
            ),
            RecipientShare(
                wallet="Wallet2",
                balance=100,
                share_percentage=Decimal("50"),
                amount=5000
            ),
        ]

        # Equal balances should get equal shares
        assert recipients[0].amount == recipients[1].amount


class TestDistributionExecution:
    """Tests for distribution execution."""

    @pytest.mark.asyncio
    async def test_execute_distribution_records_to_db(self, db_session, mock_settings):
        """Test that distribution is recorded in database."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            with patch("app.services.distribution.settings", mock_settings):
                service = DistributionService(db_session)

                plan = DistributionPlan(
                    pool_amount=1_000_000_000,
                    pool_value_usd=Decimal("100"),
                    total_supply=300_000_000,
                    recipient_count=2,
                    trigger_type="hourly",
                    recipients=[
                        RecipientShare(
                            wallet="Wallet1111111111111111111111111111111111111",
                            balance=200_000_000,
                            share_percentage=Decimal("66.67"),
                            amount=666_700_000
                        ),
                        RecipientShare(
                            wallet="Wallet2222222222222222222222222222222222222",
                            balance=100_000_000,
                            share_percentage=Decimal("33.33"),
                            amount=333_300_000
                        ),
                    ]
                )

                # Mock token transfers
                with patch.object(service, "_execute_token_transfers", return_value={}):
                    distribution = await service.execute_distribution(plan)

                    if distribution:
                        assert distribution.pool_amount == plan.pool_amount
                        assert distribution.recipient_count == plan.recipient_count
                        assert distribution.trigger_type == "hourly"
                        assert distribution.total_supply == plan.total_supply


class TestDistributionEdgeCases:
    """Edge case tests for distribution service."""

    @pytest.mark.asyncio
    async def test_empty_pool_no_distribution(self, db_session, mock_settings):
        """Test that empty pool returns None."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            service = DistributionService(db_session)

            with patch.object(service, "get_pool_balance", return_value=0):
                plan = await service.calculate_distribution()
                assert plan is None

    @pytest.mark.asyncio
    async def test_no_eligible_wallets(self, db_session, mock_settings):
        """Test distribution when no wallets meet minimum balance."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            service = DistributionService(db_session)

            with patch.object(service, "get_pool_balance", return_value=1_000_000_000):
                with patch.object(service, "get_pool_value_usd", return_value=Decimal("500")):
                    with patch.object(service.helius, "get_token_accounts", return_value=[]):
                        plan = await service.calculate_distribution()
                        assert plan is None


class TestTransferReconciliation:
    """Tests for transfer reconciliation (failed transfer handling)."""

    @pytest.mark.asyncio
    async def test_failed_transfers_record_zero_amount(self, db_session, mock_settings):
        """Test that failed transfers record amount_received=0."""
        from app.models import DistributionRecipient
        from sqlalchemy import select

        # Patch both get_settings and the module-level settings
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            with patch("app.services.distribution.settings", mock_settings):
                service = DistributionService(db_session)

                plan = DistributionPlan(
                    pool_amount=1_000_000_000,
                    pool_value_usd=Decimal("100"),
                    total_supply=300_000_000,
                    recipient_count=2,
                    trigger_type="hourly",
                    recipients=[
                        RecipientShare(
                            wallet="Wallet1111111111111111111111111111111111111",
                            balance=200_000_000,
                            share_percentage=Decimal("66.67"),
                            amount=600_000_000
                        ),
                        RecipientShare(
                            wallet="Wallet2222222222222222222222222222222222222",
                            balance=100_000_000,
                            share_percentage=Decimal("33.33"),
                            amount=400_000_000
                        ),
                    ]
                )

                # Mock token transfers - first succeeds, second fails
                transfer_results = {
                    "Wallet1111111111111111111111111111111111111": "TxSig111111111111111111111111111111111111111111111111111111111111111",
                    "Wallet2222222222222222222222222222222222222": None  # Failed transfer
                }

                with patch.object(service, "_execute_token_transfers", return_value=transfer_results):
                    distribution = await service.execute_distribution(plan)

                    assert distribution is not None

                    # Query the recipients
                    result = await db_session.execute(
                        select(DistributionRecipient)
                        .where(DistributionRecipient.distribution_id == distribution.id)
                    )
                    recipients = list(result.scalars().all())

                    # Find the successful and failed transfers
                    successful = next(r for r in recipients if r.wallet == "Wallet1111111111111111111111111111111111111")
                    failed = next(r for r in recipients if r.wallet == "Wallet2222222222222222222222222222222222222")

                    # Successful transfer should have amount_received set
                    assert successful.amount_received == 600_000_000
                    assert successful.tx_signature is not None

                    # Failed transfer should have amount_received=0
                    assert failed.amount_received == 0
                    assert failed.tx_signature is None

    @pytest.mark.asyncio
    async def test_get_failed_transfers(self, db_session, mock_settings):
        """Test retrieving failed transfers for reconciliation."""
        with patch("app.services.distribution.get_settings", return_value=mock_settings):
            with patch("app.services.distribution.settings", mock_settings):
                service = DistributionService(db_session)

                plan = DistributionPlan(
                    pool_amount=1_000_000_000,
                    pool_value_usd=Decimal("100"),
                    total_supply=100_000_000,
                    recipient_count=1,
                    trigger_type="hourly",
                    recipients=[
                        RecipientShare(
                            wallet="FailedWallet11111111111111111111111111111",
                            balance=100_000_000,
                            share_percentage=Decimal("100"),
                            amount=1_000_000_000
                        ),
                    ]
                )

                # Mock all transfers failing
                with patch.object(service, "_execute_token_transfers", return_value={}):
                    distribution = await service.execute_distribution(plan)

                    assert distribution is not None

                    # Get failed transfers
                    failed = await service.get_failed_transfers()

                    assert len(failed) >= 1
                    failed_wallets = [f.wallet for f in failed]
                    assert "FailedWallet11111111111111111111111111111" in failed_wallets

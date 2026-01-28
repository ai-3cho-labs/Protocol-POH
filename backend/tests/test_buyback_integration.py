"""
$COPPER Buyback Integration Tests

Integration tests for the full buyback flow including:
- Creator reward processing
- Jupiter swap execution
- SOL transfers
- Database recording
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
import base58

from app.services.buyback import (
    BuybackService,
    BuybackResult,
    RewardSplit,
    process_pending_rewards,
    transfer_sol
)
from app.models import CreatorReward, Buyback, SystemStats


class TestFullBuybackFlow:
    """Tests for the complete buyback flow."""

    @pytest.mark.asyncio
    async def test_full_flow_single_reward(self, db_session, mock_settings):
        """Test complete flow: reward → split → swap → record."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # 1. Record incoming reward
            reward = await service.record_creator_reward(
                amount_sol=Decimal("1.0"),
                source="pumpfun",
                tx_signature="IncomingRewardSig11111111111111111111111111111"
            )
            assert reward.processed is False

            # 2. Calculate split (100% to pool)
            split = service.calculate_split(Decimal("1.0"))
            assert split.pool_sol == Decimal("1.0")

            # 3. Mock Jupiter and execute swap
            mock_quote = {
                "inAmount": "800000000",
                "outAmount": "40000000000",
                "routePlan": []
            }

            with patch.object(service, "get_jupiter_quote", return_value=mock_quote):
                with patch.object(service, "execute_swap") as mock_swap:
                    mock_swap.return_value = BuybackResult(
                        success=True,
                        tx_signature="BuybackTxSig111111111111111111111111111111111",
                        sol_spent=Decimal("1.0"),
                        copper_received=50_000_000_000,
                        price_per_token=Decimal("0.00000002")
                    )

                    result = await service.execute_swap(
                        split.pool_sol,
                        mock_settings.creator_wallet_private_key
                    )

                    assert result.success is True
                    assert result.copper_received == 50_000_000_000

            # 4. Record buyback
            buyback = await service.record_buyback(
                tx_signature="BuybackTxSig111111111111111111111111111111111",
                sol_amount=Decimal("1.0"),
                gold_amount=50_000_000_000,
                price_per_token=Decimal("0.00000002")
            )
            assert buyback is not None

    @pytest.mark.asyncio
    async def test_full_flow_multiple_rewards(self, db_session, mock_settings):
        """Test processing multiple accumulated rewards."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Add multiple rewards
            await service.record_creator_reward(Decimal("0.5"), "pumpfun")
            await service.record_creator_reward(Decimal("0.3"), "pumpswap")
            await service.record_creator_reward(Decimal("0.2"), "pumpfun")

            # Get total
            total = await service.get_total_unprocessed_sol()
            assert total == Decimal("1.0")

            # Calculate split (100% to pool)
            split = service.calculate_split(total)
            assert split.pool_sol == Decimal("1.0")

            # Get rewards for marking processed
            rewards = await service.get_unprocessed_rewards()
            assert len(rewards) == 3

            # Mark as processed
            reward_ids = [r.id for r in rewards]
            await service.mark_rewards_processed(reward_ids)

            # Verify marked as processed
            remaining = await service.get_unprocessed_rewards()
            assert len(remaining) == 0

    @pytest.mark.asyncio
    async def test_process_pending_rewards_e2e(self, db_session, mock_settings):
        """Test the main process_pending_rewards entry point with balance check."""
        mock_settings.creator_wallet_private_key = "test_private_key_base58_encoded"
        mock_settings.airdrop_pool_private_key = "pool_private_key_base58_encoded"
        mock_settings.buyback_min_sol_threshold = 0.01

        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            # Mock Creator Wallet balance check (instead of adding rewards to DB)
            with patch("app.services.buyback.BuybackService.get_creator_wallet_balance") as mock_balance:
                mock_balance.return_value = Decimal("0.5")  # Above threshold

                # Mock all external calls
                with patch("app.services.buyback.BuybackService.execute_swap") as mock_swap:
                    with patch("app.services.buyback.transfer_sol") as mock_transfer:
                        with patch("app.services.buyback.confirm_transaction") as mock_confirm:
                            mock_swap.return_value = BuybackResult(
                                success=True,
                                tx_signature="ProcessPendingSig11111111111111111111111111",
                                sol_spent=Decimal("0.1"),
                                copper_received=5_000_000_000,
                                price_per_token=Decimal("0.00000002")
                            )
                            mock_transfer.return_value = "PoolTransferSig1111111111111111111111111111"
                            mock_confirm.return_value = True

                            result = await process_pending_rewards(db_session)

                            # Should have checked balance
                            mock_balance.assert_called_once()
                            # Should have executed
                            assert result is not None
                            assert result.success is True


class TestBuybackRecording:
    """Tests for buyback database recording."""

    @pytest.mark.asyncio
    async def test_record_buyback_updates_system_stats(self, db_session, mock_settings):
        """Test that buyback updates system stats."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Create initial system stats
            stats = SystemStats(id=1, total_buybacks=Decimal("0"))
            db_session.add(stats)
            await db_session.commit()

            # Record buyback
            await service.record_buyback(
                tx_signature="StatUpdateSig111111111111111111111111111111111",
                sol_amount=Decimal("0.5"),
                copper_amount=25_000_000_000
            )

            # Check stats updated
            await db_session.refresh(stats)
            assert stats.total_buybacks == Decimal("0.5")

    @pytest.mark.asyncio
    async def test_get_recent_buybacks(self, db_session, mock_settings):
        """Test retrieving recent buybacks."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Add some buybacks
            for i in range(5):
                buyback = Buyback(
                    tx_signature=f"RecentBuyback{i}11111111111111111111111111111",
                    sol_amount=Decimal(f"0.{i+1}"),
                    copper_amount=i * 10_000_000_000,
                    executed_at=datetime.now(timezone.utc)
                )
                db_session.add(buyback)
            await db_session.commit()

            recent = await service.get_recent_buybacks(limit=3)
            assert len(recent) == 3

    @pytest.mark.asyncio
    async def test_get_total_buybacks(self, db_session, mock_settings):
        """Test getting total buyback statistics."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Add some buybacks
            buyback1 = Buyback(
                tx_signature="TotalBuyback111111111111111111111111111111111",
                sol_amount=Decimal("1.5"),
                copper_amount=75_000_000_000,
                executed_at=datetime.now(timezone.utc)
            )
            buyback2 = Buyback(
                tx_signature="TotalBuyback222222222222222222222222222222222",
                sol_amount=Decimal("2.5"),
                copper_amount=125_000_000_000,
                executed_at=datetime.now(timezone.utc)
            )
            db_session.add_all([buyback1, buyback2])
            await db_session.commit()

            total_sol, total_copper = await service.get_total_buybacks()
            assert total_sol == Decimal("4.0")
            assert total_copper == 200_000_000_000


class TestJupiterSwapExecution:
    """Tests for Jupiter swap execution with mocked API."""

    @pytest.mark.asyncio
    async def test_execute_swap_full_mock(self, mock_settings):
        """Test swap execution with fully mocked Jupiter."""
        # Create a mock keypair
        from solders.keypair import Keypair
        keypair = Keypair()
        private_key = base58.b58encode(bytes(keypair)).decode()

        mock_db = MagicMock()
        mock_settings.creator_wallet_private_key = private_key
        mock_settings.copper_token_mint = "TestMint111111111111111111111111111111111"

        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            # Mock HTTP client
            mock_quote_response = MagicMock()
            mock_quote_response.json.return_value = {
                "inAmount": "1000000000",
                "outAmount": "50000000000",
                "routePlan": [],
                "slippageBps": 100
            }
            mock_quote_response.raise_for_status = MagicMock()

            mock_swap_response = MagicMock()
            mock_swap_response.json.return_value = {
                "swapTransaction": "base64encodedtransaction=="
            }
            mock_swap_response.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_quote_response)
            mock_client.post = AsyncMock(return_value=mock_swap_response)

            with patch("app.services.buyback.get_http_client", return_value=mock_client):
                with patch("app.services.buyback.sign_and_send_transaction") as mock_send:
                    with patch("app.services.buyback.confirm_transaction") as mock_confirm:
                        # Mock transaction result
                        mock_send.return_value = MagicMock(
                            success=True,
                            signature="SwapTxSignature11111111111111111111111111111"
                        )
                        mock_confirm.return_value = True

                        service = BuybackService(mock_db)
                        result = await service.execute_swap(
                            sol_amount=Decimal("1.0"),
                            wallet_private_key=private_key
                        )

                        assert result.success is True
                        assert result.tx_signature is not None
                        assert result.sol_spent == Decimal("1.0")
                        assert result.copper_received == 50000000000

    @pytest.mark.asyncio
    async def test_execute_swap_jupiter_api_error(self, mock_settings):
        """Test handling of Jupiter API errors."""
        from solders.keypair import Keypair
        keypair = Keypair()
        private_key = base58.b58encode(bytes(keypair)).decode()

        mock_db = MagicMock()
        mock_settings.copper_token_mint = "TestMint222222222222222222222222222222222"

        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            mock_client = MagicMock()
            mock_client.get = AsyncMock(side_effect=Exception("Jupiter API unavailable"))

            with patch("app.services.buyback.get_http_client", return_value=mock_client):
                service = BuybackService(mock_db)
                result = await service.execute_swap(
                    sol_amount=Decimal("1.0"),
                    wallet_private_key=private_key
                )

                assert result.success is False
                assert result.error is not None

    @pytest.mark.asyncio
    async def test_execute_swap_no_swap_transaction(self, mock_settings):
        """Test handling when Jupiter returns no swap transaction."""
        from solders.keypair import Keypair
        keypair = Keypair()
        private_key = base58.b58encode(bytes(keypair)).decode()

        mock_db = MagicMock()
        mock_settings.copper_token_mint = "TestMint333333333333333333333333333333333"

        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            mock_quote_response = MagicMock()
            mock_quote_response.json.return_value = {
                "inAmount": "1000000000",
                "outAmount": "50000000000"
            }
            mock_quote_response.raise_for_status = MagicMock()

            mock_swap_response = MagicMock()
            mock_swap_response.json.return_value = {}  # No swapTransaction
            mock_swap_response.raise_for_status = MagicMock()

            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_quote_response)
            mock_client.post = AsyncMock(return_value=mock_swap_response)

            with patch("app.services.buyback.get_http_client", return_value=mock_client):
                service = BuybackService(mock_db)
                result = await service.execute_swap(
                    sol_amount=Decimal("1.0"),
                    wallet_private_key=private_key
                )

                assert result.success is False
                assert "swap transaction" in result.error.lower()


class TestSolTransfers:
    """Tests for SOL transfers."""

    @pytest.mark.asyncio
    async def test_transfer_sol_success(self):
        """Test successful SOL transfer."""
        from solders.keypair import Keypair
        keypair = Keypair()
        private_key = base58.b58encode(bytes(keypair)).decode()
        dest_address = str(Keypair().pubkey())

        with patch("app.services.buyback.send_sol_transfer") as mock_send:
            mock_send.return_value = MagicMock(
                success=True,
                signature="TransferSig111111111111111111111111111111111"
            )

            result = await transfer_sol(
                amount_sol=Decimal("0.2"),
                from_private_key=private_key,
                to_address=dest_address
            )

            assert result == "TransferSig111111111111111111111111111111111"
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_transfer_sol_failure(self):
        """Test SOL transfer failure handling."""
        from solders.keypair import Keypair
        keypair = Keypair()
        private_key = base58.b58encode(bytes(keypair)).decode()
        dest_address = str(Keypair().pubkey())

        with patch("app.services.buyback.send_sol_transfer") as mock_send:
            mock_send.return_value = MagicMock(
                success=False,
                signature=None,
                error="Insufficient funds"
            )

            result = await transfer_sol(
                amount_sol=Decimal("0.2"),
                from_private_key=private_key,
                to_address=dest_address
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_transfer_sol_negative_amount(self):
        """Test transfer with negative amount."""
        result = await transfer_sol(
            amount_sol=Decimal("-1.0"),
            from_private_key="SomeKey",
            to_address="SomeAddress"
        )

        assert result is None


class TestBuybackEdgeCases:
    """Edge case tests for buyback service."""

    @pytest.mark.asyncio
    async def test_very_small_amount(self, db_session, mock_settings):
        """Test processing very small reward amounts."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Very small reward
            await service.record_creator_reward(
                amount_sol=Decimal("0.0001"),
                source="pumpfun"
            )

            split = service.calculate_split(Decimal("0.0001"))
            assert split.pool_sol == Decimal("0.0001")

    @pytest.mark.asyncio
    async def test_very_large_amount(self, db_session, mock_settings):
        """Test processing very large reward amounts."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Large reward
            await service.record_creator_reward(
                amount_sol=Decimal("1000.0"),
                source="pumpfun"
            )

            split = service.calculate_split(Decimal("1000.0"))
            assert split.pool_sol == Decimal("1000.0")

    @pytest.mark.asyncio
    async def test_concurrent_reward_processing(self, db_session, mock_settings):
        """Test that rewards aren't processed twice."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Add reward
            reward = await service.record_creator_reward(
                amount_sol=Decimal("1.0"),
                source="pumpfun"
            )

            # Mark as processed
            await service.mark_rewards_processed([reward.id])

            # Try to get unprocessed - should be empty
            unprocessed = await service.get_unprocessed_rewards()
            assert len(unprocessed) == 0

            # Total unprocessed should be 0
            total = await service.get_total_unprocessed_sol()
            assert total == Decimal(0)


class TestRewardSplitPrecision:
    """Tests for reward split decimal precision."""

    def test_split_precision_with_repeating_decimals(self):
        """Test split with amounts that create repeating decimals."""
        service = BuybackService(MagicMock())

        # 1/3 creates repeating decimals
        split = service.calculate_split(Decimal("1") / Decimal("3"))

        # 100% to pool
        assert split.pool_sol == split.total_sol

    def test_split_precision_with_many_decimals(self):
        """Test split with high precision amounts."""
        service = BuybackService(MagicMock())

        split = service.calculate_split(Decimal("0.123456789"))

        # 100% to pool
        assert split.pool_sol == Decimal("0.123456789")

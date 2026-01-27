"""
$COPPER Buyback Service Tests

Tests for buyback execution and reward processing.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.buyback import (
    BuybackService,
    BuybackResult,
    RewardSplit,
    process_pending_rewards,
    transfer_to_team_wallet
)
from app.models import CreatorReward, Buyback


class TestRewardSplit:
    """Tests for reward split calculation."""

    def test_80_10_10_split_calculation(self):
        """Test that rewards are split 80/10/10 correctly."""
        service = BuybackService(MagicMock())

        split = service.calculate_split(Decimal("100"))

        assert split.total_sol == Decimal("100")
        assert split.buyback_sol == Decimal("80")  # 80% to reward pool
        assert split.algo_bot_sol == Decimal("10")  # 10% to algo bot
        assert split.team_sol == Decimal("10")  # 10% to team

    def test_split_with_decimal_amounts(self):
        """Test split with decimal amounts."""
        service = BuybackService(MagicMock())

        split = service.calculate_split(Decimal("1.5"))

        assert split.total_sol == Decimal("1.5")
        assert split.buyback_sol == Decimal("1.2")  # 80%
        assert split.algo_bot_sol == Decimal("0.15")  # 10%
        assert split.team_sol == Decimal("0.15")  # 10%

    def test_split_with_zero(self):
        """Test split with zero amount."""
        service = BuybackService(MagicMock())

        split = service.calculate_split(Decimal("0"))

        assert split.total_sol == Decimal("0")
        assert split.buyback_sol == Decimal("0")
        assert split.algo_bot_sol == Decimal("0")
        assert split.team_sol == Decimal("0")


class TestJupiterIntegration:
    """Tests for Jupiter API integration."""

    @pytest.mark.asyncio
    async def test_get_jupiter_quote_success(self, mock_settings):
        """Test successful Jupiter quote retrieval."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "inAmount": "1000000000",
                "outAmount": "50000000000",
                "routePlan": []
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response

            with patch("app.services.buyback.get_http_client", return_value=mock_client):
                service = BuybackService(MagicMock())
                quote = await service.get_jupiter_quote(1_000_000_000)

                assert quote is not None
                # quote is now a JupiterQuote object with data and timestamp
                assert quote.data["inAmount"] == "1000000000"
                assert quote.is_fresh()  # Should be fresh when just fetched

    @pytest.mark.asyncio
    async def test_get_jupiter_quote_no_mint(self, mock_settings):
        """Test quote fails when token mint not configured."""
        mock_settings.copper_token_mint = None

        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(MagicMock())
            quote = await service.get_jupiter_quote(1_000_000_000)

            assert quote is None


class TestSwapExecution:
    """Tests for swap execution."""

    @pytest.mark.asyncio
    async def test_execute_swap_no_private_key(self, mock_settings):
        """Test swap fails without private key."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(MagicMock())

            result = await service.execute_swap(Decimal("1"), "")

            assert result.success is False
            assert "private key" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_swap_quote_failure(self, mock_settings):
        """Test swap fails when quote fails."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(MagicMock())

            with patch.object(service, "get_jupiter_quote", return_value=None):
                result = await service.execute_swap(
                    Decimal("1"),
                    "ValidPrivateKey111111111111111111111111111111111111111111111111111"
                )

                assert result.success is False
                assert "quote" in result.error.lower()


class TestBuybackResult:
    """Tests for BuybackResult dataclass."""

    def test_successful_result(self):
        """Test successful buyback result."""
        result = BuybackResult(
            success=True,
            tx_signature="TestSignature111111111111111111111111111111111111111111111111111111111",
            sol_spent=Decimal("1.5"),
            copper_received=75_000_000_000,
            price_per_token=Decimal("0.00000002")
        )

        assert result.success is True
        assert result.tx_signature is not None
        assert result.error is None

    def test_failed_result(self):
        """Test failed buyback result."""
        result = BuybackResult(
            success=False,
            tx_signature=None,
            sol_spent=Decimal("0"),
            copper_received=0,
            price_per_token=None,
            error="Transaction failed"
        )

        assert result.success is False
        assert result.error == "Transaction failed"


class TestJupiterQuoteFreshness:
    """Tests for Jupiter quote freshness tracking."""

    def test_fresh_quote(self):
        """Test that a new quote is fresh."""
        from app.services.buyback import JupiterQuote, utc_now

        quote = JupiterQuote(
            data={"inAmount": "1000", "outAmount": "2000"},
            fetched_at=utc_now()
        )

        assert quote.is_fresh() is True
        assert quote.age_seconds() < 1

    def test_stale_quote(self):
        """Test that an old quote is stale."""
        from app.services.buyback import JupiterQuote, JUPITER_QUOTE_MAX_AGE_SECONDS, utc_now
        from datetime import timedelta

        # Create a quote that's older than the max age
        old_time = utc_now() - timedelta(seconds=JUPITER_QUOTE_MAX_AGE_SECONDS + 10)
        quote = JupiterQuote(
            data={"inAmount": "1000", "outAmount": "2000"},
            fetched_at=old_time
        )

        assert quote.is_fresh() is False
        assert quote.age_seconds() > JUPITER_QUOTE_MAX_AGE_SECONDS


class TestCreatorRewardRecording:
    """Tests for creator reward recording."""

    @pytest.mark.asyncio
    async def test_record_creator_reward(self, db_session, mock_settings):
        """Test recording a new creator reward."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            reward = await service.record_creator_reward(
                amount_sol=Decimal("0.5"),
                source="pumpfun",
                tx_signature="TestSig111111111111111111111111111111111111111111111111111111111111"
            )

            assert reward is not None
            assert reward.amount_sol == Decimal("0.5")
            assert reward.source == "pumpfun"
            assert reward.processed is False

    @pytest.mark.asyncio
    async def test_creator_reward_idempotency(self, db_session, mock_settings):
        """Test that duplicate tx_signatures are handled idempotently."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)
            tx_sig = "DupeSig111111111111111111111111111111111111111111111111111111111111"

            # Record first reward
            reward1 = await service.record_creator_reward(
                amount_sol=Decimal("0.5"),
                source="pumpfun",
                tx_signature=tx_sig
            )

            # Try to record duplicate - should return existing record
            reward2 = await service.record_creator_reward(
                amount_sol=Decimal("0.5"),
                source="pumpfun",
                tx_signature=tx_sig
            )

            assert reward1.id == reward2.id  # Same record returned

            # Verify only one reward exists with this signature
            rewards = await service.get_unprocessed_rewards()
            matching = [r for r in rewards if r.tx_signature == tx_sig]
            assert len(matching) == 1

    @pytest.mark.asyncio
    async def test_get_unprocessed_rewards(self, db_session, mock_settings):
        """Test retrieving unprocessed rewards."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            service = BuybackService(db_session)

            # Add some rewards
            await service.record_creator_reward(Decimal("0.3"), "pumpfun")
            await service.record_creator_reward(Decimal("0.2"), "pumpswap")

            rewards = await service.get_unprocessed_rewards()

            assert len(rewards) >= 2


class TestTeamWalletTransfer:
    """Tests for team wallet transfer."""

    @pytest.mark.asyncio
    async def test_transfer_to_team_wallet_no_config(self):
        """Test transfer fails with missing config."""
        result = await transfer_to_team_wallet(
            Decimal("1"),
            "",  # No private key
            "TeamWallet"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_transfer_to_team_wallet_zero_amount(self):
        """Test transfer with zero amount."""
        result = await transfer_to_team_wallet(
            Decimal("0"),
            "PrivateKey",
            "TeamWallet"
        )

        assert result is None


class TestProcessPendingRewards:
    """Tests for the main reward processing function."""

    @pytest.mark.asyncio
    async def test_no_pending_rewards(self, db_session, mock_settings):
        """Test processing when no rewards are pending."""
        with patch("app.services.buyback.get_settings", return_value=mock_settings):
            result = await process_pending_rewards(db_session)

            # Should return None when no rewards
            assert result is None

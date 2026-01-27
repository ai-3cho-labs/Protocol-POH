"""
TWAB Forward-Fill Interpolation Edge Case Tests

Tests edge cases in the _compute_twab algorithm.
These are pure unit tests that don't require a database.

TODO item tested:
- [ ] Test forward-fill interpolation edge cases
"""

from decimal import Decimal
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from app.services.twab import TWABService


class TestForwardFillInterpolation:
    """Edge case tests for _compute_twab forward-fill algorithm."""

    def setup_method(self):
        """Create a TWABService with a mock db (not used for _compute_twab)."""
        self.service = TWABService(MagicMock())

    def test_empty_balances_returns_zero(self):
        """No balance snapshots should return 0 TWAB."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)

        result = self.service._compute_twab([], start, end)

        assert result == 0

    def test_zero_duration_returns_zero(self):
        """If start == end, should return 0."""
        ts = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        balances = [(ts, 1_000_000)]

        result = self.service._compute_twab(balances, ts, ts)

        assert result == 0

    def test_negative_duration_returns_zero(self):
        """If end < start, should return 0."""
        start = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        balances = [(start, 1_000_000)]

        result = self.service._compute_twab(balances, start, end)

        assert result == 0

    def test_single_balance_full_period(self):
        """Single balance at start of period covers full period."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours
        balance = 1_000_000

        # Balance at exactly start time
        balances = [(start, balance)]

        result = self.service._compute_twab(balances, start, end)

        # Full period coverage = full balance
        assert result == balance

    def test_single_balance_mid_period(self):
        """Single balance mid-period only counts from snapshot to end."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours
        balance = 1_000_000

        # Balance at 12 hours into period (50% through)
        mid_point = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        balances = [(mid_point, balance)]

        result = self.service._compute_twab(balances, start, end)

        # Only 50% coverage = 50% of balance
        # (0 * 12h + 1_000_000 * 12h) / 24h = 500_000
        assert result == 500_000

    def test_single_balance_at_end(self):
        """Single balance at end of period should contribute almost nothing."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        balance = 1_000_000

        # Balance 1 second before end
        near_end = end - timedelta(seconds=1)
        balances = [(near_end, balance)]

        result = self.service._compute_twab(balances, start, end)

        # 1 second out of 86400 seconds = ~0.001%
        # 1_000_000 * 1 / 86400 ≈ 11
        assert result < 20  # Very small

    def test_single_balance_before_period(self):
        """Balance before start should count from start."""
        start = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 12, 0, tzinfo=timezone.utc)  # 24 hours
        balance = 1_000_000

        # Balance recorded 6 hours BEFORE start
        before_start = datetime(2024, 1, 1, 6, 0, tzinfo=timezone.utc)
        balances = [(before_start, balance)]

        result = self.service._compute_twab(balances, start, end)

        # Balance is clamped to start, so full coverage
        assert result == balance

    def test_single_balance_after_period(self):
        """Balance after end should contribute nothing."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        balance = 1_000_000

        # Balance recorded after end
        after_end = datetime(2024, 1, 3, 0, 0, tzinfo=timezone.utc)
        balances = [(after_end, balance)]

        result = self.service._compute_twab(balances, start, end)

        # Duration would be clamped to 0 or negative
        assert result == 0

    def test_two_balances_equal_split(self):
        """Two equal balances should average correctly."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours

        # Two balances at start and midpoint
        balances = [
            (start, 1_000_000),
            (datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc), 2_000_000),
        ]

        result = self.service._compute_twab(balances, start, end)

        # First 12h: 1_000_000
        # Second 12h: 2_000_000
        # Average: (1_000_000 * 12 + 2_000_000 * 12) / 24 = 1_500_000
        assert result == 1_500_000

    def test_balance_increase_mid_period(self):
        """Buying more tokens mid-period should weight correctly."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours

        # Start with 100k, buy 900k more at 75% through period
        balances = [
            (start, 100_000),
            (datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc), 1_000_000),  # 6h remaining
        ]

        result = self.service._compute_twab(balances, start, end)

        # First 18h: 100_000
        # Last 6h: 1_000_000
        # (100_000 * 18 + 1_000_000 * 6) / 24 = (1_800_000 + 6_000_000) / 24 = 325_000
        assert result == 325_000

    def test_balance_decrease_mid_period(self):
        """Selling tokens mid-period should weight correctly."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours

        # Start with 1M, sell 900k at 25% through period
        balances = [
            (start, 1_000_000),
            (datetime(2024, 1, 1, 6, 0, tzinfo=timezone.utc), 100_000),  # 18h remaining
        ]

        result = self.service._compute_twab(balances, start, end)

        # First 6h: 1_000_000
        # Last 18h: 100_000
        # (1_000_000 * 6 + 100_000 * 18) / 24 = (6_000_000 + 1_800_000) / 24 = 325_000
        assert result == 325_000

    def test_many_snapshots(self):
        """Multiple snapshots should all contribute correctly."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours

        # Hourly snapshots with increasing balance
        balances = [
            (start + timedelta(hours=i), (i + 1) * 100_000)
            for i in range(24)
        ]

        result = self.service._compute_twab(balances, start, end)

        # Each hour: 100k, 200k, 300k, ..., 2400k
        # Sum = 100k * (1 + 2 + ... + 24) = 100k * 300 = 30,000,000
        # Average = 30,000,000 / 24 = 1,250,000
        assert result == 1_250_000

    def test_zero_balance_snapshot(self):
        """Zero balance snapshot should contribute zero for its period."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)

        balances = [
            (start, 0),
            (datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc), 1_000_000),
        ]

        result = self.service._compute_twab(balances, start, end)

        # First 12h: 0
        # Last 12h: 1_000_000
        # Average: 500_000
        assert result == 500_000

    def test_naive_datetime_handling(self):
        """Naive datetimes should be treated as UTC."""
        # Using naive datetimes (no tzinfo)
        start = datetime(2024, 1, 1, 0, 0)  # naive
        end = datetime(2024, 1, 2, 0, 0)    # naive
        balance = 1_000_000

        balances = [(start, balance)]

        result = self.service._compute_twab(balances, start, end)

        # Should work the same as timezone-aware
        assert result == balance

    def test_mixed_timezone_handling(self):
        """Mix of naive and aware datetimes should work."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        balance = 1_000_000

        # Naive timestamp in balance
        naive_ts = datetime(2024, 1, 1, 0, 0)
        balances = [(naive_ts, balance)]

        result = self.service._compute_twab(balances, start, end)

        assert result == balance

    def test_precise_decimal_calculation(self):
        """Large numbers should not lose precision."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)

        # Very large balance (10 trillion tokens with 9 decimals)
        large_balance = 10_000_000_000_000_000_000

        balances = [(start, large_balance)]

        result = self.service._compute_twab(balances, start, end)

        # Should preserve precision
        assert result == large_balance

    def test_fractional_seconds_precision(self):
        """Sub-second precision should work correctly."""
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 0, 0, 10, tzinfo=timezone.utc)  # 10 seconds

        # Balance at 5.5 seconds
        mid = datetime(2024, 1, 1, 0, 0, 5, 500000, tzinfo=timezone.utc)
        balances = [(mid, 1_000_000)]

        result = self.service._compute_twab(balances, start, end)

        # 4.5 seconds out of 10 = 45%
        # 1_000_000 * 4.5 / 10 = 450_000
        assert result == 450_000

    def test_implicit_zero_before_first_snapshot(self):
        """
        Time before first snapshot should contribute zero.

        This is the key forward-fill behavior - we don't backfill.
        """
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)  # 24 hours

        # Wallet only has balance from hour 20 onwards (bought late)
        late_entry = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)
        balance = 1_000_000
        balances = [(late_entry, balance)]

        result = self.service._compute_twab(balances, start, end)

        # Only 4 hours out of 24 = 16.67%
        # 1_000_000 * 4 / 24 = 166_666
        expected = int(Decimal(1_000_000) * Decimal(4) / Decimal(24))
        assert result == expected

    def test_new_holder_vs_existing_holder(self):
        """New holder mid-period should have lower TWAB than existing holder."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        balance = 1_000_000

        # Existing holder (balance from start)
        existing_balances = [(start, balance)]
        existing_twab = self.service._compute_twab(existing_balances, start, end)

        # New holder (bought mid-period)
        mid = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        new_balances = [(mid, balance)]
        new_twab = self.service._compute_twab(new_balances, start, end)

        # Existing holder should have 2x the TWAB
        assert existing_twab == balance
        assert new_twab == balance // 2
        assert existing_twab > new_twab


class TestTWABAccuracyVerification:
    """
    Tests to verify TWAB accuracy with multiple snapshots.

    TODO item tested:
    - [ ] Verify TWAB accuracy with multiple snapshots
    """

    def setup_method(self):
        self.service = TWABService(MagicMock())

    def test_accuracy_constant_balance(self):
        """Constant balance across all snapshots should equal the balance."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        balance = 1_234_567

        # 24 hourly snapshots, all same balance
        balances = [
            (start + timedelta(hours=i), balance)
            for i in range(24)
        ]

        result = self.service._compute_twab(balances, start, end)

        assert result == balance

    def test_accuracy_linear_increase(self):
        """Linear balance increase should average to midpoint."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)

        # Balance increases by 100k each hour: 0, 100k, 200k, ..., 2300k
        balances = [
            (start + timedelta(hours=i), i * 100_000)
            for i in range(24)
        ]

        result = self.service._compute_twab(balances, start, end)

        # With forward-fill, each balance covers 1 hour
        # Sum of areas = 0*1 + 100k*1 + 200k*1 + ... + 2300k*1
        # = 100k * (0 + 1 + 2 + ... + 23) = 100k * 276 = 27,600,000
        # TWAB = 27,600,000 / 24 = 1,150,000
        expected = int(Decimal(100_000) * Decimal(276) / Decimal(24))
        assert result == expected

    def test_accuracy_step_function(self):
        """Step changes in balance should weight by duration."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)

        # 1M for first 6h, 2M for next 12h, 500k for last 6h
        balances = [
            (start, 1_000_000),
            (start + timedelta(hours=6), 2_000_000),
            (start + timedelta(hours=18), 500_000),
        ]

        result = self.service._compute_twab(balances, start, end)

        # (1M * 6 + 2M * 12 + 500k * 6) / 24
        # = (6M + 24M + 3M) / 24 = 33M / 24 = 1,375,000
        expected = (1_000_000 * 6 + 2_000_000 * 12 + 500_000 * 6) // 24
        assert result == expected

    def test_accuracy_volatile_balance(self):
        """High frequency changes should still calculate correctly."""
        start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc)  # 1 hour = 3600 seconds

        # Balance changes every minute for an hour
        balances = []
        for minute in range(60):
            ts = start + timedelta(minutes=minute)
            # Oscillate between 1M and 2M
            balance = 1_000_000 if minute % 2 == 0 else 2_000_000
            balances.append((ts, balance))

        result = self.service._compute_twab(balances, start, end)

        # 30 minutes at 1M, 30 minutes at 2M = average 1.5M
        assert result == 1_500_000

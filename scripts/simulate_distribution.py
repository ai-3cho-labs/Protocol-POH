"""
CPU Mining Distribution Simulator

Simulates the distribution of $GOLD rewards to CPU holders
based on their TWAB and tier multipliers.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List

# Tier configuration (from config.py)
TIER_CONFIG = {
    1: {"name": "Ore", "multiplier": 1.0, "min_hours": 0},
    2: {"name": "Raw Copper", "multiplier": 1.25, "min_hours": 6},
    3: {"name": "Refined", "multiplier": 1.5, "min_hours": 12},
    4: {"name": "Industrial", "multiplier": 2.5, "min_hours": 72},
    5: {"name": "Master Miner", "multiplier": 3.5, "min_hours": 168},
    6: {"name": "Diamond Hands", "multiplier": 5.0, "min_hours": 720},
}


@dataclass
class Holder:
    wallet: str
    balance: int  # CPU tokens held
    twab: int  # Time-weighted average balance
    tier: int  # 1-6
    hours_held: int

    @property
    def multiplier(self) -> float:
        return TIER_CONFIG[self.tier]["multiplier"]

    @property
    def tier_name(self) -> str:
        return TIER_CONFIG[self.tier]["name"]

    @property
    def hash_power(self) -> Decimal:
        return Decimal(self.twab) * Decimal(str(self.multiplier))


@dataclass
class DistributionResult:
    wallet: str
    twab: int
    tier: int
    tier_name: str
    multiplier: float
    hash_power: Decimal
    share_percent: Decimal
    reward: int


def simulate_distribution(holders: List[Holder], pool_amount: int) -> List[DistributionResult]:
    """Simulate a distribution to holders."""

    # Calculate total hash power
    total_hp = sum(h.hash_power for h in holders)

    if total_hp == 0:
        return []

    results = []
    total_distributed = 0

    # Calculate shares
    for h in holders:
        share_pct = (h.hash_power / total_hp) * 100
        reward = int(Decimal(pool_amount) * (h.hash_power / total_hp))
        total_distributed += reward

        results.append(DistributionResult(
            wallet=h.wallet,
            twab=h.twab,
            tier=h.tier,
            tier_name=h.tier_name,
            multiplier=h.multiplier,
            hash_power=h.hash_power,
            share_percent=share_pct,
            reward=reward
        ))

    # Distribute remainder to top holders
    remainder = pool_amount - total_distributed
    if remainder > 0:
        results.sort(key=lambda x: x.hash_power, reverse=True)
        for i in range(remainder):
            results[i % len(results)].reward += 1

    # Sort by reward descending
    results.sort(key=lambda x: x.reward, reverse=True)

    return results


def format_number(n: int) -> str:
    """Format number with commas."""
    return f"{n:,}"


def main():
    print("=" * 80)
    print("CPU MINING - DISTRIBUTION SIMULATOR")
    print("=" * 80)
    print()

    # Simulate holders with different profiles
    holders = [
        Holder(
            wallet="Whale1...ABC",
            balance=10_000_000,
            twab=9_500_000,  # Held consistently
            tier=6,  # Diamond Hands (30+ days)
            hours_held=800
        ),
        Holder(
            wallet="Whale2...DEF",
            balance=5_000_000,
            twab=4_800_000,
            tier=5,  # Master Miner (7+ days)
            hours_held=200
        ),
        Holder(
            wallet="MidHolder1...GHI",
            balance=1_000_000,
            twab=950_000,
            tier=4,  # Industrial (3+ days)
            hours_held=100
        ),
        Holder(
            wallet="MidHolder2...JKL",
            balance=800_000,
            twab=750_000,
            tier=3,  # Refined (12+ hours)
            hours_held=20
        ),
        Holder(
            wallet="SmallHolder1...MNO",
            balance=500_000,
            twab=480_000,
            tier=2,  # Raw Copper (6+ hours)
            hours_held=10
        ),
        Holder(
            wallet="SmallHolder2...PQR",
            balance=250_000,
            twab=200_000,
            tier=1,  # Ore (new holder)
            hours_held=2
        ),
        Holder(
            wallet="NewHolder1...STU",
            balance=100_000,
            twab=50_000,  # Just bought, low TWAB
            tier=1,
            hours_held=1
        ),
        Holder(
            wallet="NewHolder2...VWX",
            balance=75_000,
            twab=30_000,
            tier=1,
            hours_held=1
        ),
    ]

    # Pool amount (in raw tokens, assuming 9 decimals)
    pool_amount = 50_000_000_000_000  # 50,000 GOLD tokens
    pool_display = pool_amount // 1_000_000_000  # Convert to human readable

    print("POOL STATUS")
    print("-" * 40)
    print(f"Pool Balance: {format_number(pool_display)} $GOLD")
    print(f"Total Holders: {len(holders)}")
    print()

    # Display holders
    print("HOLDERS (before distribution)")
    print("-" * 80)
    print(f"{'Wallet':<18} {'Balance':>12} {'TWAB':>12} {'Tier':<14} {'Mult':>6} {'Hash Power':>14}")
    print("-" * 80)

    for h in holders:
        print(f"{h.wallet:<18} {format_number(h.balance):>12} {format_number(h.twab):>12} "
              f"{h.tier_name:<14} {h.multiplier:>5}x {format_number(int(h.hash_power)):>14}")

    total_hp = sum(h.hash_power for h in holders)
    print("-" * 80)
    print(f"{'TOTAL':<18} {'':<12} {'':<12} {'':<14} {'':<6} {format_number(int(total_hp)):>14}")
    print()

    # Run distribution
    results = simulate_distribution(holders, pool_amount)

    print("DISTRIBUTION RESULTS")
    print("-" * 80)
    print(f"{'Wallet':<18} {'Hash Power':>14} {'Share %':>10} {'Reward ($GOLD)':>16}")
    print("-" * 80)

    for r in results:
        reward_display = r.reward // 1_000_000_000
        print(f"{r.wallet:<18} {format_number(int(r.hash_power)):>14} {r.share_percent:>9.2f}% {format_number(reward_display):>16}")

    total_rewards = sum(r.reward for r in results) // 1_000_000_000
    print("-" * 80)
    print(f"{'TOTAL DISTRIBUTED':<18} {'':<14} {'100.00%':>10} {format_number(total_rewards):>16}")
    print()

    # Summary
    print("KEY INSIGHTS")
    print("-" * 40)
    print(f"• Whale1 (Diamond Hands, 5x) gets {results[0].share_percent:.1f}% despite having ~{holders[0].twab/sum(h.twab for h in holders)*100:.1f}% of TWAB")
    print(f"• Tier multiplier significantly boosts rewards for long-term holders")
    print(f"• NewHolder2 with {format_number(holders[-1].twab)} TWAB at Tier 1 gets only {results[-1].share_percent:.2f}%")
    print()

    # Show tier impact
    print("TIER IMPACT ANALYSIS")
    print("-" * 40)
    whale1 = holders[0]
    new_holder = holders[-1]

    # What if whale1 was tier 1?
    whale1_as_tier1 = Decimal(whale1.twab) * Decimal("1.0")
    whale1_actual = whale1.hash_power
    tier_boost = (whale1_actual / whale1_as_tier1 - 1) * 100

    print(f"• Whale1's Tier 6 (5x) boosts hash power by {tier_boost:.0f}%")
    print(f"  - At Tier 1: {format_number(int(whale1_as_tier1))} HP")
    print(f"  - At Tier 6: {format_number(int(whale1_actual))} HP")
    print()

    # Simulate what new holder would get at different tiers
    print("IF NewHolder2 held for 30 days (Tier 6):")
    new_holder_at_t6 = Decimal(new_holder.twab) * Decimal("5.0")
    new_total_hp = total_hp - new_holder.hash_power + new_holder_at_t6
    new_share = (new_holder_at_t6 / new_total_hp) * 100
    new_reward = int(Decimal(pool_amount) * (new_holder_at_t6 / new_total_hp)) // 1_000_000_000
    print(f"  - Hash Power: {format_number(int(new_holder.hash_power))} -> {format_number(int(new_holder_at_t6))}")
    print(f"  - Share: {results[-1].share_percent:.2f}% -> {new_share:.2f}%")
    print(f"  - Reward: {format_number(results[-1].reward // 1_000_000_000)} -> {format_number(new_reward)} $GOLD")
    print()

    print("=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

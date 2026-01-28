"""
CPU + GOLD Dual-Token Backend Configuration

CPU = Token users hold (determines mining eligibility & hash power)
GOLD = Token distributed as rewards

Loads settings from environment variables with sensible defaults.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "development"
    debug: bool = False
    test_mode: bool = False  # Enable mock data for testing
    embedded_celery: bool = False  # Run Celery worker/beat inside FastAPI process

    # Test mode mock values (pool)
    test_pool_balance: float = 500000.0  # Mock pool balance in tokens
    test_pool_value_usd: float = 175.0  # Mock pool USD value
    test_hours_since_distribution: float = 8.0  # Mock hours since last distribution

    # Devnet fallback price (used when price APIs don't have data for test tokens)
    devnet_gold_price_usd: float = 0.001  # $0.001 per GOLD token on devnet

    # Test mode mock values (user) - used when wallet has no real data
    test_user_balance: float = 1000000.0  # Mock user balance in tokens
    test_user_twab: float = 950000.0  # Mock TWAB
    test_user_multiplier: float = 2.5  # Mock multiplier (Industrial tier)
    test_user_hash_power: float = 2375000.0  # twab * multiplier
    test_user_share_percent: float = 15.0  # Mock share of pool

    # Solana Network (mainnet-beta or devnet)
    solana_network: str = "mainnet-beta"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # API Key Authentication
    api_keys: str = ""  # Comma-separated valid API keys
    api_key_header_name: str = "X-API-Key"

    # Admin API Key (for /api/admin/* endpoints)
    admin_api_key: str = ""  # Single key for admin access

    # Database (Neon PostgreSQL)
    database_url: str = ""

    # Redis (Upstash)
    redis_url: str = ""
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""

    # Helius API
    helius_api_key: str = ""
    helius_webhook_secret: str = ""
    helius_webhook_ips: str = ""  # Comma-separated IP allowlist (optional)

    # Solana RPC (override for custom RPC, otherwise uses Helius)
    solana_rpc_url: str = ""

    # Wallet Private Keys (Base58 encoded)
    # Note: Buybacks use creator_wallet - no separate buyback wallet needed
    creator_wallet_private_key: str = ""
    airdrop_pool_private_key: str = ""
    team_wallet_public_key: str = ""
    algo_bot_wallet_public_key: str = ""

    # Token Configuration (Dual-Token Model)
    # CPU = Token users hold (determines mining eligibility & hash power)
    # GOLD = Token distributed as rewards
    cpu_token_mint: str = ""
    cpu_token_decimals: int = 9  # Standard SPL token decimals
    gold_token_mint: str = ""
    gold_token_decimals: int = 6  # GOLD token has 6 decimals

    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    # Distribution Settings
    distribution_threshold_usd: float = 250.0
    distribution_max_hours: int = 24
    min_balance_usd: float = 50.0

    # Reward Split (must total 100)
    reward_pool_percent: int = 80  # % to airdrop pool
    algo_bot_percent: int = 10  # % to algo bot
    team_percent: int = 10  # % to team

    # Buyback Split (of the pool allocation)
    buyback_swap_percent: int = 20  # % swapped to reward token
    buyback_reserve_percent: int = 80  # % kept as SOL reserves

    # Token Branding (for logs/display)
    hold_token_symbol: str = "CPU"  # Token users hold
    reward_token_symbol: str = "GOLD"  # Token distributed as rewards

    # Snapshot Settings
    snapshot_probability: float = 0.4  # 40% chance per hour

    # Jupiter Swap Settings
    # API key for Jupiter paid API (optional, provides better rates and priority)
    jupiter_api_key: str = ""

    # Jupiter API base URL (paid API uses different endpoint)
    # Free: https://quote-api.jup.ag/v6
    # Paid: https://api.jup.ag/swap/v1
    jupiter_api_base_url: str = "https://quote-api.jup.ag/v6"

    # Slippage in basis points (100 = 1%, 50 = 0.5%)
    # Lower slippage protects against MEV sandwich attacks but may cause swap failures
    # SECURITY: Capped at 200 bps (2%) to prevent excessive MEV extraction
    jupiter_slippage_bps: int = 50  # 0.5% slippage (default, configurable via env)

    # Maximum allowed slippage (security cap to prevent MEV attacks)
    jupiter_max_slippage_bps: int = 200  # 2% maximum

    # Emergency fallback price for GOLD token when all price APIs fail
    # Used to prevent distribution failures; set conservatively low
    emergency_gold_price_usd: float = 0.0001  # $0.0001 per GOLD token

    @property
    def safe_slippage_bps(self) -> int:
        """Get slippage capped at maximum safe value to prevent MEV exploitation."""
        return min(self.jupiter_slippage_bps, self.jupiter_max_slippage_bps)

    # Monitoring
    sentry_dsn: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse and validate CORS origins."""
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        # In production, reject wildcard
        if self.is_production and "*" in origins:
            raise ValueError("Wildcard CORS origin not allowed in production")
        return origins

    @property
    def api_keys_list(self) -> List[str]:
        """Parse API keys from comma-separated string."""
        if not self.api_keys:
            return []
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_devnet(self) -> bool:
        """Check if running on Solana devnet."""
        return self.solana_network == "devnet"

    @property
    def helius_rpc_url(self) -> str:
        """Get Helius RPC URL for current network."""
        if self.solana_rpc_url:
            return self.solana_rpc_url
        network = "devnet" if self.is_devnet else "mainnet"
        return f"https://{network}.helius-rpc.com/?api-key={self.helius_api_key}"

    @property
    def helius_api_url(self) -> str:
        """Get Helius API URL for current network."""
        network = "devnet" if self.is_devnet else "mainnet"
        return f"https://api-{network}.helius-rpc.com/v0"

    @property
    def jupiter_api_url(self) -> str:
        """Get Jupiter API URL (same for all networks)."""
        return "https://quote-api.jup.ag/v6"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Tier configuration
TIER_CONFIG = {
    1: {"name": "Ore", "emoji": "\U0001FAA8", "multiplier": 1.0, "min_hours": 0},
    2: {
        "name": "Raw Copper",
        "emoji": "\U0001F536",
        "multiplier": 1.25,
        "min_hours": 6,
    },
    3: {"name": "Refined", "emoji": "\u26A1", "multiplier": 1.5, "min_hours": 12},
    4: {
        "name": "Industrial",
        "emoji": "\U0001F3ED",
        "multiplier": 2.5,
        "min_hours": 72,
    },  # 3 days
    5: {
        "name": "Master Miner",
        "emoji": "\U0001F451",
        "multiplier": 3.5,
        "min_hours": 168,
    },  # 7 days
    6: {
        "name": "Diamond Hands",
        "emoji": "\U0001F48E",
        "multiplier": 5.0,
        "min_hours": 720,
    },  # 30 days
}

# Tier thresholds in hours
TIER_THRESHOLDS = {
    1: 0,  # 0 hours
    2: 6,  # 6 hours
    3: 12,  # 12 hours
    4: 72,  # 3 days
    5: 168,  # 7 days
    6: 720,  # 30 days
}

# Solana constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
LAMPORTS_PER_SOL = 1_000_000_000

# Token decimals - use settings value
# Standard SPL token = 9 decimals, but some tokens (like USDC) use 6
# CPU token is what users hold (for eligibility/hash power calculation)
# GOLD token is what gets distributed as rewards
CPU_DECIMALS = get_settings().cpu_token_decimals
GOLD_DECIMALS = get_settings().gold_token_decimals
TOKEN_MULTIPLIER = 10**CPU_DECIMALS
GOLD_MULTIPLIER = 10**GOLD_DECIMALS

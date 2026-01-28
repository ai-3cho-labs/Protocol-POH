"""
Redis Cache Utility

Provides caching for expensive calculations like leaderboard and pool status.
Uses Upstash Redis with configurable TTLs.
"""

import json
import logging
from typing import Optional, Any

import redis.asyncio as redis
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Cache key prefixes
CACHE_PREFIX = "protocol:cache:"
LEADERBOARD_KEY = f"{CACHE_PREFIX}leaderboard"
POOL_STATUS_KEY = f"{CACHE_PREFIX}pool_status"
USER_PREFIX = f"{CACHE_PREFIX}user:"

# Default TTLs (in seconds)
LEADERBOARD_TTL = 3600  # 1 hour
POOL_STATUS_TTL = 300  # 5 minutes
USER_TTL = 300  # 5 minutes


class CacheService:
    """Redis cache service for expensive calculations."""

    _instance: Optional["CacheService"] = None
    _redis: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            r = await self._get_redis()
            return await r.get(key)
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    async def set(
        self, key: str, value: str, ttl: int = 60
    ) -> bool:
        """Set value in cache with TTL."""
        try:
            r = await self._get_redis()
            await r.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            r = await self._get_redis()
            await r.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache."""
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(
        self, key: str, value: Any, ttl: int = 60
    ) -> bool:
        """Set JSON value in cache."""
        try:
            data = json.dumps(value, default=str)
            return await self.set(key, data, ttl)
        except Exception as e:
            logger.warning(f"Cache set_json error for {key}: {e}")
            return False

    # Specific cache methods

    async def get_leaderboard(self) -> Optional[list]:
        """Get cached leaderboard."""
        return await self.get_json(LEADERBOARD_KEY)

    async def set_leaderboard(self, data: list) -> bool:
        """Cache leaderboard data."""
        return await self.set_json(LEADERBOARD_KEY, data, LEADERBOARD_TTL)

    async def get_pool_status(self) -> Optional[dict]:
        """Get cached pool status."""
        return await self.get_json(POOL_STATUS_KEY)

    async def set_pool_status(self, data: dict) -> bool:
        """Cache pool status."""
        return await self.set_json(POOL_STATUS_KEY, data, POOL_STATUS_TTL)

    async def get_user_data(self, wallet: str) -> Optional[dict]:
        """Get cached user data."""
        return await self.get_json(f"{USER_PREFIX}{wallet}")

    async def set_user_data(self, wallet: str, data: dict) -> bool:
        """Cache user data."""
        return await self.set_json(f"{USER_PREFIX}{wallet}", data, USER_TTL)

    async def invalidate_wallet(self, wallet: str) -> None:
        """Invalidate all cache for a wallet."""
        await self.delete(f"{USER_PREFIX}{wallet}")

    async def invalidate_all(self) -> None:
        """Invalidate all protocol cache (use sparingly)."""
        try:
            r = await self._get_redis()
            cursor = 0
            while True:
                cursor, keys = await r.scan(cursor, match=f"{CACHE_PREFIX}*", count=100)
                if keys:
                    await r.delete(*keys)
                if cursor == 0:
                    break
            logger.info("Invalidated all protocol cache")
        except Exception as e:
            logger.warning(f"Cache invalidate_all error: {e}")


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get cache service singleton."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

"""
$COPPER HTTP Client Manager

Manages shared HTTP client lifecycle for all services.
Ensures proper connection pool management and cleanup.
"""

import asyncio
import logging
from typing import Optional
from collections import defaultdict

import httpx

logger = logging.getLogger(__name__)


class RPCCallCounter:
    """Tracks RPC calls for debugging and monitoring."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all counters."""
        self.calls = defaultdict(int)
        self.total = 0

    def increment(self, endpoint: str):
        """Increment counter for an endpoint."""
        self.calls[endpoint] += 1
        self.total += 1

    def get_stats(self) -> dict:
        """Get call statistics."""
        return {
            "total": self.total,
            "by_endpoint": dict(self.calls),
        }

    def log_summary(self):
        """Log a summary of RPC calls."""
        if self.total == 0:
            return
        logger.info(f"RPC Call Summary: {self.total} total calls")
        for endpoint, count in sorted(self.calls.items(), key=lambda x: -x[1]):
            logger.info(f"  {endpoint}: {count}")


# Global RPC counter
rpc_counter = RPCCallCounter()


class HTTPClientManager:
    """
    Singleton HTTP client manager.

    Provides a shared httpx.AsyncClient that is properly initialized
    and closed with the application lifecycle.

    Includes event loop detection to recreate client if the loop changes,
    preventing PoolTimeout errors from orphaned connections.
    """

    _instance: Optional["HTTPClientManager"] = None
    _client: Optional[httpx.AsyncClient] = None
    _loop_id: Optional[int] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_current_loop_id(self) -> Optional[int]:
        """Get the current event loop's ID, or None if no loop running."""
        try:
            # Use get_running_loop() which is the recommended API for Python 3.10+
            # This only works when called from within an async context
            loop = asyncio.get_running_loop()
            return id(loop) if loop and not loop.is_closed() else None
        except RuntimeError:
            # No running event loop - this is expected when called from sync context
            return None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the shared HTTP client."""
        current_loop_id = self._get_current_loop_id()

        # Recreate client if loop changed (safety check)
        if self._client is not None and self._loop_id != current_loop_id:
            logger.warning("Event loop changed, recreating HTTP client")
            # Don't await close - old loop may be dead
            self._client = None

        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0,
                ),
                follow_redirects=True,
            )
            self._loop_id = current_loop_id
            logger.info("HTTP client initialized")
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("HTTP client closed")


# Global singleton instance
_http_manager = HTTPClientManager()


def get_http_client() -> httpx.AsyncClient:
    """Get the shared HTTP client."""
    return _http_manager.client


async def close_http_client():
    """Close the shared HTTP client. Call on app shutdown."""
    await _http_manager.close()

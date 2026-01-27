"""
$COPPER HTTP Client Manager

Manages shared HTTP client lifecycle for all services.
Ensures proper connection pool management and cleanup.
"""

import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


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
        """Get the current event loop's ID, or None if no loop."""
        try:
            loop = asyncio.get_event_loop()
            return id(loop) if loop and not loop.is_closed() else None
        except RuntimeError:
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
                    keepalive_expiry=30.0
                ),
                follow_redirects=True
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

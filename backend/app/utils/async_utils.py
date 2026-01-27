"""
$COPPER Async Utilities

Shared async utilities for Celery tasks and other sync contexts.
"""

import asyncio
import logging
from typing import TypeVar, Coroutine, Any, Optional

T = TypeVar("T")
logger = logging.getLogger(__name__)

# Persistent event loop for worker process
_worker_loop: Optional[asyncio.AbstractEventLoop] = None


def get_worker_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get or create the persistent event loop for this worker process.

    Unlike asyncio.run() which creates a new loop per call,
    this maintains a single loop for the worker's lifetime.
    This allows async resources (HTTP clients, DB pools) to persist
    and avoid PoolTimeout errors from orphaned connections.

    Returns:
        The worker's event loop.
    """
    global _worker_loop

    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
        logger.info("Created persistent event loop for worker")

    return _worker_loop


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine from a sync context.

    Used by Celery tasks to execute async service methods.
    Uses a persistent event loop per worker process to maintain
    connection pools and async resources across tasks.

    Args:
        coro: Async coroutine to execute.

    Returns:
        Result of the coroutine.
    """
    loop = get_worker_event_loop()
    return loop.run_until_complete(coro)

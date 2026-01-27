"""
$COPPER WebSocket Handlers

Connection event handlers for Socket.IO.
"""

import logging
import re
from typing import Optional

from app.websocket.socket_server import (
    sio,
    connection_tracker,
    get_client_ip,
    GLOBAL_ROOM,
    wallet_room,
    WS_NAMESPACE,
)

logger = logging.getLogger(__name__)

# Wallet address validation pattern (base58, 32-44 chars)
WALLET_PATTERN = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

# Track which wallet each session is subscribed to
_session_wallets: dict[str, str] = {}


def is_valid_wallet(address: str) -> bool:
    """Validate a Solana wallet address."""
    if not address or not isinstance(address, str):
        return False
    return bool(WALLET_PATTERN.match(address))


@sio.event(namespace=WS_NAMESPACE)
async def connect(sid: str, environ: dict, auth: Optional[dict] = None) -> bool:
    """
    Handle new client connection.

    Args:
        sid: Session ID.
        environ: ASGI environ dict with request info.
        auth: Optional auth data from client.

    Returns:
        True to accept connection, False to reject.
    """
    client_ip = get_client_ip(environ)

    # Check rate limit
    if not connection_tracker.can_connect(client_ip):
        logger.warning(f"Connection rejected for {client_ip}: rate limit exceeded")
        return False

    # Track connection with sid->IP mapping for proper cleanup on disconnect
    connection_tracker.add_connection(sid, client_ip)

    # Auto-join global room
    await sio.enter_room(sid, GLOBAL_ROOM, namespace=WS_NAMESPACE)

    logger.info(f"Client connected: sid={sid}, ip={client_ip}")
    return True


@sio.event(namespace=WS_NAMESPACE)
async def disconnect(sid: str) -> None:
    """
    Handle client disconnection.

    Args:
        sid: Session ID.
    """
    # Decrement rate limit counter using sid->IP mapping
    connection_tracker.remove_connection(sid)

    # Clean up wallet subscription
    if sid in _session_wallets:
        wallet = _session_wallets.pop(sid)
        await sio.leave_room(sid, wallet_room(wallet), namespace=WS_NAMESPACE)
        logger.debug(f"Removed wallet subscription for sid={sid}")

    # Leave global room (happens automatically, but be explicit)
    await sio.leave_room(sid, GLOBAL_ROOM, namespace=WS_NAMESPACE)

    logger.info(f"Client disconnected: sid={sid}")


def _sanitize_for_log(value: str, max_len: int = 20) -> str:
    """Sanitize a value for safe logging (remove control chars, truncate)."""
    # Remove control characters and non-printable chars
    sanitized = "".join(c for c in value if c.isprintable() and ord(c) < 128)
    if len(sanitized) > max_len:
        return sanitized[:max_len] + "..."
    return sanitized


@sio.event(namespace=WS_NAMESPACE)
async def subscribe_wallet(sid: str, data: dict) -> dict:
    """
    Subscribe to wallet-specific events.

    Args:
        sid: Session ID.
        data: Dict with 'wallet' key.

    Returns:
        Response dict with success status.
    """
    wallet = data.get("wallet", "") if isinstance(data, dict) else ""

    if not is_valid_wallet(wallet):
        # Sanitize wallet for logging to prevent log injection
        safe_wallet = _sanitize_for_log(str(wallet))
        logger.warning(f"Invalid wallet subscription attempt: sid={sid}, wallet={safe_wallet}")
        return {"success": False, "error": "Invalid wallet address"}

    # Leave previous wallet room if subscribed
    if sid in _session_wallets:
        old_wallet = _session_wallets[sid]
        await sio.leave_room(sid, wallet_room(old_wallet), namespace=WS_NAMESPACE)

    # Join new wallet room
    room = wallet_room(wallet)
    await sio.enter_room(sid, room, namespace=WS_NAMESPACE)
    _session_wallets[sid] = wallet

    logger.debug(f"Wallet subscription: sid={sid}, wallet={wallet[:8]}...")
    return {"success": True, "wallet": wallet}


@sio.event(namespace=WS_NAMESPACE)
async def unsubscribe_wallet(sid: str) -> dict:
    """
    Unsubscribe from wallet-specific events.

    Args:
        sid: Session ID.

    Returns:
        Response dict with success status.
    """
    if sid not in _session_wallets:
        return {"success": True, "message": "Not subscribed to any wallet"}

    wallet = _session_wallets.pop(sid)
    await sio.leave_room(sid, wallet_room(wallet), namespace=WS_NAMESPACE)

    logger.debug(f"Wallet unsubscription: sid={sid}, wallet={wallet[:8]}...")
    return {"success": True}


def get_subscribed_wallet(sid: str) -> Optional[str]:
    """Get the wallet a session is subscribed to."""
    return _session_wallets.get(sid)

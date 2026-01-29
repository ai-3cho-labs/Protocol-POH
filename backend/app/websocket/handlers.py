"""
$COPPER WebSocket Handlers

Connection event handlers for Socket.IO.
Handlers are registered on both "/" and "/ws" namespaces for client compatibility.
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
    WS_NAMESPACES,
)

logger = logging.getLogger(__name__)

# Wallet address validation pattern (base58, 32-44 chars)
WALLET_PATTERN = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

# Track which wallet each session is subscribed to
_session_wallets: dict[str, str] = {}

# Track which namespace each session is connected to
_session_namespaces: dict[str, str] = {}


def is_valid_wallet(address: str) -> bool:
    """Validate a Solana wallet address."""
    if not address or not isinstance(address, str):
        return False
    return bool(WALLET_PATTERN.match(address))


def _sanitize_for_log(value: str, max_len: int = 20) -> str:
    """Sanitize a value for safe logging (remove control chars, truncate)."""
    sanitized = "".join(c for c in value if c.isprintable() and ord(c) < 128)
    if len(sanitized) > max_len:
        return sanitized[:max_len] + "..."
    return sanitized


def get_session_namespace(sid: str) -> str:
    """Get the namespace a session is connected to."""
    return _session_namespaces.get(sid, "/ws")


# ============================================================================
# Handler factory functions - create handlers for each namespace
# ============================================================================


def create_connect_handler(namespace: str):
    """Create a connect handler for a specific namespace."""

    async def connect(sid: str, environ: dict, auth: Optional[dict] = None) -> bool:
        """Handle new client connection."""
        try:
            client_ip = get_client_ip(environ)

            # Check rate limit
            if not connection_tracker.can_connect(client_ip):
                logger.warning(f"Connection rejected for {client_ip}: rate limit exceeded")
                return False

            # Track connection with sid->IP mapping for proper cleanup
            connection_tracker.add_connection(sid, client_ip)

            # Track which namespace this session connected to
            _session_namespaces[sid] = namespace

            # Auto-join global room on the connected namespace
            await sio.enter_room(sid, GLOBAL_ROOM, namespace=namespace)

            logger.info(
                f"Client connected: sid={sid}, ip={client_ip}, namespace={namespace}"
            )
            return True
        except Exception as e:
            logger.error(f"Connect handler error for sid={sid}, namespace={namespace}: {e}", exc_info=True)
            return False

    return connect


def create_disconnect_handler(namespace: str):
    """Create a disconnect handler for a specific namespace."""

    async def disconnect(sid: str) -> None:
        """Handle client disconnection."""
        # Decrement rate limit counter
        connection_tracker.remove_connection(sid)

        # Clean up wallet subscription
        if sid in _session_wallets:
            wallet = _session_wallets.pop(sid)
            await sio.leave_room(sid, wallet_room(wallet), namespace=namespace)
            logger.debug(f"Removed wallet subscription for sid={sid}")

        # Leave global room
        await sio.leave_room(sid, GLOBAL_ROOM, namespace=namespace)

        # Clean up namespace tracking
        _session_namespaces.pop(sid, None)

        logger.info(f"Client disconnected: sid={sid}")

    return disconnect


def create_subscribe_wallet_handler(namespace: str):
    """Create a subscribe_wallet handler for a specific namespace."""

    async def subscribe_wallet(sid: str, data: dict) -> dict:
        """Subscribe to wallet-specific events."""
        wallet = data.get("wallet", "") if isinstance(data, dict) else ""

        if not is_valid_wallet(wallet):
            safe_wallet = _sanitize_for_log(str(wallet))
            logger.warning(
                f"Invalid wallet subscription attempt: sid={sid}, wallet={safe_wallet}"
            )
            return {"success": False, "error": "Invalid wallet address"}

        # Leave previous wallet room if subscribed
        if sid in _session_wallets:
            old_wallet = _session_wallets[sid]
            await sio.leave_room(sid, wallet_room(old_wallet), namespace=namespace)

        # Join new wallet room
        room = wallet_room(wallet)
        await sio.enter_room(sid, room, namespace=namespace)
        _session_wallets[sid] = wallet

        logger.debug(f"Wallet subscription: sid={sid}, wallet={wallet[:8]}...")
        return {"success": True, "wallet": wallet}

    return subscribe_wallet


def create_unsubscribe_wallet_handler(namespace: str):
    """Create an unsubscribe_wallet handler for a specific namespace."""

    async def unsubscribe_wallet(sid: str) -> dict:
        """Unsubscribe from wallet-specific events."""
        if sid not in _session_wallets:
            return {"success": True, "message": "Not subscribed to any wallet"}

        wallet = _session_wallets.pop(sid)
        await sio.leave_room(sid, wallet_room(wallet), namespace=namespace)

        logger.debug(f"Wallet unsubscription: sid={sid}, wallet={wallet[:8]}...")
        return {"success": True}

    return unsubscribe_wallet


# ============================================================================
# Register handlers on ALL supported namespaces
# ============================================================================

for ns in WS_NAMESPACES:
    sio.on("connect", create_connect_handler(ns), namespace=ns)
    sio.on("disconnect", create_disconnect_handler(ns), namespace=ns)
    sio.on("subscribe_wallet", create_subscribe_wallet_handler(ns), namespace=ns)
    sio.on("unsubscribe_wallet", create_unsubscribe_wallet_handler(ns), namespace=ns)

logger.info(f"WebSocket handlers registered on namespaces: {WS_NAMESPACES}")


def get_subscribed_wallet(sid: str) -> Optional[str]:
    """Get the wallet a session is subscribed to."""
    return _session_wallets.get(sid)

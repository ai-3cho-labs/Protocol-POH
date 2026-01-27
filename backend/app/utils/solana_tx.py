"""
$COPPER Solana Transaction Utilities

Handles transaction signing and sending using solders.
"""

import logging
import base64
import base58
from typing import Optional
from dataclasses import dataclass

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from app.utils.http_client import get_http_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Error patterns indicating stale blockhash
BLOCKHASH_ERROR_PATTERNS = [
    "blockhash not found",
    "BlockhashNotFound",
    "block height exceeded",
    "transaction simulation failed",
]

# Maximum retries for stale blockhash
MAX_BLOCKHASH_RETRIES = 2

# SECURITY: Maximum transaction limits to prevent accidental/malicious large transfers
MAX_SOL_LAMPORTS = 100_000_000_000_000  # 100,000 SOL
MAX_TOKEN_AMOUNT = 10**18  # Reasonable upper bound for SPL tokens


@dataclass
class TransactionResult:
    """Result of a transaction send."""

    success: bool
    signature: Optional[str] = None
    error: Optional[str] = None


def keypair_from_base58(private_key: str) -> Keypair:
    """
    Create a Keypair from a base58-encoded private key.

    Args:
        private_key: Base58-encoded private key (64 bytes).

    Returns:
        Keypair instance.
    """
    secret_bytes = base58.b58decode(private_key)
    return Keypair.from_bytes(secret_bytes)


def _is_blockhash_error(error_msg: str) -> bool:
    """Check if an error message indicates a stale blockhash."""
    error_lower = error_msg.lower()
    return any(pattern.lower() in error_lower for pattern in BLOCKHASH_ERROR_PATTERNS)


async def get_recent_blockhash() -> Optional[str]:
    """
    Fetch the most recent blockhash from the Solana network.

    Uses finalized commitment for reliability.

    Returns:
        Blockhash string if successful, None otherwise.
    """
    client = get_http_client()
    try:
        response = await client.post(
            settings.helius_rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": "copper-blockhash",
                "method": "getLatestBlockhash",
                "params": [{"commitment": "finalized"}],
            },
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            logger.error(f"Blockhash fetch error: {data['error']}")
            return None

        return data["result"]["value"]["blockhash"]
    except Exception as e:
        logger.error(f"Failed to fetch blockhash: {e}")
        return None


async def sign_and_send_transaction(
    serialized_tx: str, private_key: str, skip_preflight: bool = False
) -> TransactionResult:
    """
    Sign and send a serialized transaction.

    Args:
        serialized_tx: Base64-encoded serialized transaction from Jupiter.
        private_key: Base58-encoded private key.
        skip_preflight: Skip preflight simulation.

    Returns:
        TransactionResult with signature or error.
    """
    try:
        # Decode the transaction
        tx_bytes = base64.b64decode(serialized_tx)
        transaction = VersionedTransaction.from_bytes(tx_bytes)

        # Create keypair and sign
        keypair = keypair_from_base58(private_key)

        # Sign the transaction
        signed_tx = VersionedTransaction(transaction.message, [keypair])

        # Serialize for sending
        signed_bytes = bytes(signed_tx)
        signed_base64 = base64.b64encode(signed_bytes).decode("utf-8")

        # Send via RPC
        client = get_http_client()
        response = await client.post(
            settings.helius_rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": "copper-tx",
                "method": "sendTransaction",
                "params": [
                    signed_base64,
                    {
                        "encoding": "base64",
                        "skipPreflight": skip_preflight,
                        "preflightCommitment": "confirmed",
                        "maxRetries": 3,
                    },
                ],
            },
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            error_msg = data["error"].get("message", str(data["error"]))
            logger.error(f"Transaction send error: {error_msg}")
            return TransactionResult(success=False, error=error_msg)

        signature = data.get("result")
        if signature:
            logger.info(f"Transaction sent: {signature}")
            return TransactionResult(success=True, signature=signature)

        return TransactionResult(success=False, error="No signature returned")

    except Exception as e:
        # SECURITY: Do not use exc_info=True to avoid exposing private key bytes in stack traces
        logger.error(f"Error signing/sending transaction: {type(e).__name__}: {e}")
        return TransactionResult(success=False, error=str(e))


async def send_sol_transfer(
    from_private_key: str, to_address: str, amount_lamports: int
) -> TransactionResult:
    """
    Send SOL from one wallet to another.

    Includes retry logic for stale blockhash errors.

    Args:
        from_private_key: Base58-encoded private key of sender.
        to_address: Recipient wallet address.
        amount_lamports: Amount in lamports (1 SOL = 1e9 lamports).

    Returns:
        TransactionResult with signature or error.
    """
    # SECURITY: Validate transaction amount
    if amount_lamports <= 0:
        return TransactionResult(success=False, error="Amount must be positive")
    if amount_lamports > MAX_SOL_LAMPORTS:
        return TransactionResult(
            success=False, error=f"Amount exceeds maximum ({MAX_SOL_LAMPORTS} lamports)"
        )

    from solders.pubkey import Pubkey
    from solders.system_program import transfer, TransferParams
    from solders.message import MessageV0
    from solders.hash import Hash

    # Create keypair and destination (done once, outside retry loop)
    keypair = keypair_from_base58(from_private_key)
    to_pubkey = Pubkey.from_string(to_address)

    # Create transfer instruction (reusable across retries)
    transfer_ix = transfer(
        TransferParams(
            from_pubkey=keypair.pubkey(), to_pubkey=to_pubkey, lamports=amount_lamports
        )
    )

    last_error = None

    for attempt in range(MAX_BLOCKHASH_RETRIES + 1):
        try:
            # Fetch fresh blockhash for each attempt (fixes race condition)
            blockhash_str = await get_recent_blockhash()
            if not blockhash_str:
                return TransactionResult(success=False, error="Failed to get blockhash")

            recent_blockhash = Hash.from_string(blockhash_str)

            # Create message and transaction with fresh blockhash
            message = MessageV0.try_compile(
                payer=keypair.pubkey(),
                instructions=[transfer_ix],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash,
            )

            transaction = VersionedTransaction(message, [keypair])

            # Serialize and send immediately after getting blockhash
            tx_bytes = bytes(transaction)
            tx_base64 = base64.b64encode(tx_bytes).decode("utf-8")

            client = get_http_client()
            response = await client.post(
                settings.helius_rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "copper-sol-transfer",
                    "method": "sendTransaction",
                    "params": [
                        tx_base64,
                        {
                            "encoding": "base64",
                            "skipPreflight": False,
                            "preflightCommitment": "confirmed",
                            "maxRetries": 3,
                        },
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", str(data["error"]))

                # Check if this is a stale blockhash error and we can retry
                if _is_blockhash_error(error_msg) and attempt < MAX_BLOCKHASH_RETRIES:
                    logger.warning(
                        f"Stale blockhash on SOL transfer (attempt {attempt + 1}), retrying..."
                    )
                    last_error = error_msg
                    continue

                logger.error(f"SOL transfer error: {error_msg}")
                return TransactionResult(success=False, error=error_msg)

            signature = data.get("result")
            if signature:
                logger.info(f"SOL transfer sent: {signature}")
                return TransactionResult(success=True, signature=signature)

            return TransactionResult(success=False, error="No signature returned")

        except Exception as e:
            last_error = str(e)
            if attempt < MAX_BLOCKHASH_RETRIES:
                logger.warning(
                    f"SOL transfer exception (attempt {attempt + 1}): {e}, retrying..."
                )
                continue
            # SECURITY: Do not use exc_info=True to avoid exposing private key bytes in stack traces
            logger.error(f"Error sending SOL transfer: {type(e).__name__}: {e}")

    return TransactionResult(
        success=False, error=last_error or "Transaction failed after retries"
    )


async def send_spl_token_transfer(
    from_private_key: str, to_address: str, token_mint: str, amount: int
) -> TransactionResult:
    """
    Send SPL tokens from one wallet to another.

    Includes retry logic for stale blockhash errors.

    Args:
        from_private_key: Base58-encoded private key of sender.
        to_address: Recipient wallet address.
        token_mint: Token mint address.
        amount: Raw token amount (with decimals).

    Returns:
        TransactionResult with signature or error.
    """
    # SECURITY: Validate transaction amount
    if amount <= 0:
        return TransactionResult(success=False, error="Amount must be positive")
    if amount > MAX_TOKEN_AMOUNT:
        return TransactionResult(
            success=False, error=f"Amount exceeds maximum ({MAX_TOKEN_AMOUNT})"
        )

    from solders.pubkey import Pubkey
    from solders.message import MessageV0
    from solders.hash import Hash
    from solders.instruction import Instruction, AccountMeta

    # SPL Token Program ID
    TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string(
        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
    )

    # Create keypair and addresses (done once, outside retry loop)
    keypair = keypair_from_base58(from_private_key)
    mint_pubkey = Pubkey.from_string(token_mint)
    to_pubkey = Pubkey.from_string(to_address)

    # Derive ATAs (Associated Token Accounts)
    def get_ata(owner: Pubkey, mint: Pubkey) -> Pubkey:
        seeds = [bytes(owner), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
        ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
        return ata

    from_ata = get_ata(keypair.pubkey(), mint_pubkey)
    to_ata = get_ata(to_pubkey, mint_pubkey)

    # Check if recipient ATA exists (done once before retry loop)
    client = get_http_client()
    try:
        ata_check_response = await client.post(
            settings.helius_rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": "copper-ata-check",
                "method": "getAccountInfo",
                "params": [str(to_ata), {"encoding": "base64"}],
            },
        )
        ata_check_response.raise_for_status()
        ata_check_data = ata_check_response.json()
        ata_exists = ata_check_data.get("result", {}).get("value") is not None
    except Exception as e:
        logger.error(f"Failed to check ATA existence: {e}")
        return TransactionResult(success=False, error=f"ATA check failed: {e}")

    # Build instructions (reusable across retries)
    instructions = []

    # Create ATA if it doesn't exist
    if not ata_exists:
        create_ata_ix = Instruction(
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(
                    keypair.pubkey(), is_signer=True, is_writable=True
                ),  # Payer
                AccountMeta(to_ata, is_signer=False, is_writable=True),  # ATA
                AccountMeta(to_pubkey, is_signer=False, is_writable=False),  # Owner
                AccountMeta(mint_pubkey, is_signer=False, is_writable=False),  # Mint
                AccountMeta(
                    Pubkey.from_string("11111111111111111111111111111111"),
                    is_signer=False,
                    is_writable=False,
                ),  # System
                AccountMeta(
                    TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
                ),  # Token Program
            ],
            data=bytes(),  # No data for create ATA
        )
        instructions.append(create_ata_ix)

    # Transfer instruction data: [3] + amount as u64 little endian
    transfer_data = bytes([3]) + amount.to_bytes(8, "little")

    transfer_ix = Instruction(
        program_id=TOKEN_PROGRAM_ID,
        accounts=[
            AccountMeta(from_ata, is_signer=False, is_writable=True),  # Source
            AccountMeta(to_ata, is_signer=False, is_writable=True),  # Destination
            AccountMeta(
                keypair.pubkey(), is_signer=True, is_writable=False
            ),  # Authority
        ],
        data=transfer_data,
    )
    instructions.append(transfer_ix)

    last_error = None

    for attempt in range(MAX_BLOCKHASH_RETRIES + 1):
        try:
            # Fetch fresh blockhash for each attempt (fixes race condition)
            blockhash_str = await get_recent_blockhash()
            if not blockhash_str:
                return TransactionResult(success=False, error="Failed to get blockhash")

            recent_blockhash = Hash.from_string(blockhash_str)

            # Create message and transaction with fresh blockhash
            message = MessageV0.try_compile(
                payer=keypair.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash,
            )

            transaction = VersionedTransaction(message, [keypair])

            # Serialize and send immediately after getting blockhash
            tx_bytes = bytes(transaction)
            tx_base64 = base64.b64encode(tx_bytes).decode("utf-8")

            response = await client.post(
                settings.helius_rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "copper-token-transfer",
                    "method": "sendTransaction",
                    "params": [
                        tx_base64,
                        {
                            "encoding": "base64",
                            "skipPreflight": False,
                            "preflightCommitment": "confirmed",
                            "maxRetries": 3,
                        },
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", str(data["error"]))

                # Check if this is a stale blockhash error and we can retry
                if _is_blockhash_error(error_msg) and attempt < MAX_BLOCKHASH_RETRIES:
                    logger.warning(
                        f"Stale blockhash on token transfer (attempt {attempt + 1}), retrying..."
                    )
                    last_error = error_msg
                    continue

                logger.error(f"Token transfer error: {error_msg}")
                return TransactionResult(success=False, error=error_msg)

            signature = data.get("result")
            if signature:
                logger.info(f"Token transfer sent: {signature}")
                return TransactionResult(success=True, signature=signature)

            return TransactionResult(success=False, error="No signature returned")

        except Exception as e:
            last_error = str(e)
            if attempt < MAX_BLOCKHASH_RETRIES:
                logger.warning(
                    f"Token transfer exception (attempt {attempt + 1}): {e}, retrying..."
                )
                continue
            # SECURITY: Do not use exc_info=True to avoid exposing private key bytes in stack traces
            logger.error(f"Error sending token transfer: {type(e).__name__}: {e}")

    return TransactionResult(
        success=False, error=last_error or "Transaction failed after retries"
    )


@dataclass
class BatchTransferResult:
    """Result of a batch token transfer."""

    success: bool
    signature: Optional[str] = None
    successful_wallets: list[str] = None
    failed_wallets: list[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.successful_wallets is None:
            self.successful_wallets = []
        if self.failed_wallets is None:
            self.failed_wallets = []


async def send_batch_spl_token_transfers(
    from_private_key: str,
    token_mint: str,
    recipients: list[tuple[str, int]],  # List of (wallet_address, amount)
) -> BatchTransferResult:
    """
    Send SPL tokens to multiple recipients in a single transaction.

    Batches multiple transfers into one transaction for efficiency.
    Maximum ~10-12 recipients per batch (transaction size limit).

    Args:
        from_private_key: Base58-encoded private key of sender.
        token_mint: Token mint address.
        recipients: List of (wallet_address, amount) tuples.

    Returns:
        BatchTransferResult with signature and success status per wallet.
    """
    if not recipients:
        return BatchTransferResult(success=True, successful_wallets=[], failed_wallets=[])

    from solders.pubkey import Pubkey
    from solders.message import MessageV0
    from solders.hash import Hash
    from solders.instruction import Instruction, AccountMeta
    from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

    # SPL Token Program IDs
    TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string(
        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
    )
    SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

    # Create keypair and mint pubkey
    keypair = keypair_from_base58(from_private_key)
    mint_pubkey = Pubkey.from_string(token_mint)

    # Helper to derive ATA
    def get_ata(owner: Pubkey, mint: Pubkey) -> Pubkey:
        seeds = [bytes(owner), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
        ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
        return ata

    from_ata = get_ata(keypair.pubkey(), mint_pubkey)
    client = get_http_client()

    # Collect all recipient ATAs and check existence in batch
    recipient_data = []
    ata_addresses = []

    for wallet_addr, amount in recipients:
        to_pubkey = Pubkey.from_string(wallet_addr)
        to_ata = get_ata(to_pubkey, mint_pubkey)
        recipient_data.append({
            "wallet": wallet_addr,
            "pubkey": to_pubkey,
            "ata": to_ata,
            "amount": amount,
            "ata_exists": False,
        })
        ata_addresses.append(str(to_ata))

    # Batch check ATA existence with getMultipleAccounts
    try:
        ata_check_response = await client.post(
            settings.helius_rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": "copper-batch-ata-check",
                "method": "getMultipleAccounts",
                "params": [ata_addresses, {"encoding": "base64"}],
            },
        )
        ata_check_response.raise_for_status()
        ata_check_data = ata_check_response.json()

        accounts = ata_check_data.get("result", {}).get("value", [])
        for i, account in enumerate(accounts):
            if i < len(recipient_data):
                recipient_data[i]["ata_exists"] = account is not None

    except Exception as e:
        logger.error(f"Failed to batch check ATAs: {e}")
        return BatchTransferResult(
            success=False,
            failed_wallets=[w for w, _ in recipients],
            error=f"ATA batch check failed: {e}",
        )

    # Build instructions
    instructions = []

    # Add compute budget for larger transactions
    # ~50k CU per transfer, plus overhead
    compute_units = 50_000 * len(recipients) + 100_000
    compute_units = min(compute_units, 1_400_000)  # Max 1.4M
    instructions.append(set_compute_unit_limit(compute_units))

    # Add priority fee (1000 micro-lamports per CU)
    instructions.append(set_compute_unit_price(1000))

    # Create ATA instructions for recipients who don't have one
    for rd in recipient_data:
        if not rd["ata_exists"]:
            create_ata_ix = Instruction(
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
                accounts=[
                    AccountMeta(keypair.pubkey(), is_signer=True, is_writable=True),  # Payer
                    AccountMeta(rd["ata"], is_signer=False, is_writable=True),  # ATA
                    AccountMeta(rd["pubkey"], is_signer=False, is_writable=False),  # Owner
                    AccountMeta(mint_pubkey, is_signer=False, is_writable=False),  # Mint
                    AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),  # System
                    AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),  # Token
                ],
                data=bytes(),
            )
            instructions.append(create_ata_ix)

    # Add transfer instructions for all recipients
    for rd in recipient_data:
        transfer_data = bytes([3]) + rd["amount"].to_bytes(8, "little")
        transfer_ix = Instruction(
            program_id=TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(from_ata, is_signer=False, is_writable=True),  # Source
                AccountMeta(rd["ata"], is_signer=False, is_writable=True),  # Destination
                AccountMeta(keypair.pubkey(), is_signer=True, is_writable=False),  # Authority
            ],
            data=transfer_data,
        )
        instructions.append(transfer_ix)

    # Send transaction with retry logic
    last_error = None
    wallets = [w for w, _ in recipients]

    for attempt in range(MAX_BLOCKHASH_RETRIES + 1):
        try:
            blockhash_str = await get_recent_blockhash()
            if not blockhash_str:
                return BatchTransferResult(
                    success=False,
                    failed_wallets=wallets,
                    error="Failed to get blockhash",
                )

            recent_blockhash = Hash.from_string(blockhash_str)

            message = MessageV0.try_compile(
                payer=keypair.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash,
            )

            transaction = VersionedTransaction(message, [keypair])
            tx_bytes = bytes(transaction)
            tx_base64 = base64.b64encode(tx_bytes).decode("utf-8")

            response = await client.post(
                settings.helius_rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "copper-batch-transfer",
                    "method": "sendTransaction",
                    "params": [
                        tx_base64,
                        {
                            "encoding": "base64",
                            "skipPreflight": False,
                            "preflightCommitment": "confirmed",
                            "maxRetries": 3,
                        },
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", str(data["error"]))

                if _is_blockhash_error(error_msg) and attempt < MAX_BLOCKHASH_RETRIES:
                    logger.warning(
                        f"Stale blockhash on batch transfer (attempt {attempt + 1}), retrying..."
                    )
                    last_error = error_msg
                    continue

                logger.error(f"Batch transfer error: {error_msg}")
                return BatchTransferResult(
                    success=False,
                    failed_wallets=wallets,
                    error=error_msg,
                )

            signature = data.get("result")
            if signature:
                logger.info(
                    f"Batch transfer sent: {signature} ({len(recipients)} recipients)"
                )
                return BatchTransferResult(
                    success=True,
                    signature=signature,
                    successful_wallets=wallets,
                    failed_wallets=[],
                )

            return BatchTransferResult(
                success=False,
                failed_wallets=wallets,
                error="No signature returned",
            )

        except Exception as e:
            last_error = str(e)
            if attempt < MAX_BLOCKHASH_RETRIES:
                logger.warning(
                    f"Batch transfer exception (attempt {attempt + 1}): {e}, retrying..."
                )
                continue
            logger.error(f"Error sending batch transfer: {type(e).__name__}: {e}")

    return BatchTransferResult(
        success=False,
        failed_wallets=wallets,
        error=last_error or "Transaction failed after retries",
    )


async def confirm_transaction(signature: str, timeout_seconds: int = 60) -> bool:
    """
    Wait for transaction confirmation.

    Args:
        signature: Transaction signature.
        timeout_seconds: Maximum wait time.

    Returns:
        True if confirmed, False otherwise.
    """
    import asyncio

    client = get_http_client()
    start_time = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
        try:
            response = await client.post(
                settings.helius_rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "copper-confirm",
                    "method": "getSignatureStatuses",
                    "params": [[signature]],
                },
            )
            response.raise_for_status()
            data = response.json()

            statuses = data.get("result", {}).get("value", [])
            if statuses and statuses[0]:
                status = statuses[0]
                if status.get("confirmationStatus") in ["confirmed", "finalized"]:
                    if status.get("err") is None:
                        logger.info(f"Transaction confirmed: {signature}")
                        return True
                    else:
                        logger.error(f"Transaction failed: {status.get('err')}")
                        return False

            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            await asyncio.sleep(1)

    logger.warning(f"Transaction confirmation timeout: {signature}")
    return False


async def batch_confirm_transactions(
    signatures: list[str],
    timeout_seconds: int = 30,
    poll_interval: float = 2.0,
) -> dict[str, bool]:
    """
    Batch confirm multiple transactions with single RPC call per poll.

    Uses getSignatureStatuses to check all signatures at once, reducing
    RPC calls from N*polls to just polls (e.g., 150 -> 15 for 10 transactions).

    Args:
        signatures: List of transaction signatures to confirm.
        timeout_seconds: Maximum wait time for all confirmations.
        poll_interval: Time between poll attempts in seconds.

    Returns:
        Dict mapping signature to confirmation status (True=confirmed, False=failed/timeout).
    """
    import asyncio

    if not signatures:
        return {}

    client = get_http_client()
    results: dict[str, bool] = {sig: False for sig in signatures}
    pending = set(signatures)
    start_time = asyncio.get_event_loop().time()

    logger.info(f"Batch confirming {len(signatures)} transactions (timeout={timeout_seconds}s)")

    while pending and (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
        try:
            # Single RPC call for all pending signatures
            response = await client.post(
                settings.helius_rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": "copper-batch-confirm",
                    "method": "getSignatureStatuses",
                    "params": [list(pending)],
                },
            )
            response.raise_for_status()
            data = response.json()

            statuses = data.get("result", {}).get("value", [])
            pending_list = list(pending)

            for i, status in enumerate(statuses):
                if i >= len(pending_list):
                    break

                sig = pending_list[i]

                if status is None:
                    # Transaction not yet processed
                    continue

                confirmation = status.get("confirmationStatus")
                err = status.get("err")

                if confirmation in ["confirmed", "finalized"]:
                    if err is None:
                        results[sig] = True
                        pending.discard(sig)
                        logger.debug(f"Batch confirm: {sig[:16]}... confirmed")
                    else:
                        # Transaction failed on-chain
                        results[sig] = False
                        pending.discard(sig)
                        logger.warning(f"Batch confirm: {sig[:16]}... failed: {err}")

            if pending:
                await asyncio.sleep(poll_interval)

        except Exception as e:
            logger.error(f"Error in batch confirmation poll: {e}")
            await asyncio.sleep(poll_interval)

    # Log summary
    confirmed = sum(1 for v in results.values() if v)
    timed_out = len(pending)
    logger.info(
        f"Batch confirmation complete: {confirmed}/{len(signatures)} confirmed, "
        f"{timed_out} timed out"
    )

    return results

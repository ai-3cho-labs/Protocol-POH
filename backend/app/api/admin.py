"""
Admin API Routes

Secured endpoints for manual task triggers and debugging.
Requires API key authentication via X-Admin-Key header.
"""

import logging
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult

from app.database import get_db
from app.config import get_settings, GOLD_MULTIPLIER, LAMPORTS_PER_SOL
from app.tasks.celery_app import celery_app
from app.utils.rate_limiter import limiter

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ===========================================
# Authentication
# ===========================================


async def verify_admin_key(x_admin_key: str = Header(..., alias="X-Admin-Key")) -> str:
    """
    Verify admin API key from header.

    Requires X-Admin-Key header with a valid key from ADMIN_API_KEY env var.
    """
    admin_key = settings.admin_api_key

    if not admin_key:
        logger.warning("Admin endpoint accessed but ADMIN_API_KEY not configured")
        raise HTTPException(status_code=503, detail="Admin API not configured")

    if not x_admin_key or x_admin_key != admin_key:
        logger.warning("Invalid admin API key attempt")
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    return x_admin_key


# ===========================================
# Response Models
# ===========================================


class TaskResponse(BaseModel):
    """Response for triggered tasks."""

    task_id: str
    task_name: str
    status: str


class TaskStatusResponse(BaseModel):
    """Response for task status check."""

    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


class PendingRewardsResponse(BaseModel):
    """Response for pending rewards (Creator Wallet balance)."""

    creator_wallet_address: str
    creator_wallet_balance_sol: float
    creator_wallet_balance_lamports: int
    min_threshold_sol: float
    ready_to_process: bool


class PoolBalanceResponse(BaseModel):
    """Response for pool balance check."""

    sol_balance: float
    sol_balance_lamports: int
    gold_balance: float
    gold_balance_raw: int
    pool_address: str


# ===========================================
# Task Trigger Endpoints
# ===========================================


@router.post("/trigger/buyback", response_model=TaskResponse)
@limiter.limit("10/minute")
async def trigger_buyback(request: Request, _: str = Depends(verify_admin_key)):
    """
    Manually trigger the buyback task.

    Processes pending creator rewards with 80/10/10 split
    and executes Jupiter swap (SOL → GOLD).
    """
    from app.tasks.buyback_task import process_creator_rewards

    task = process_creator_rewards.delay()
    logger.info(f"Admin triggered buyback task: {task.id}")

    return TaskResponse(
        task_id=task.id, task_name="process_creator_rewards", status="queued"
    )


@router.post("/trigger/snapshot", response_model=TaskResponse)
@limiter.limit("10/minute")
async def trigger_snapshot(request: Request, _: str = Depends(verify_admin_key)):
    """
    Manually trigger a balance snapshot.

    Takes a snapshot of all holder balances for analytics.
    """
    from app.tasks.snapshot_task import take_snapshot

    task = take_snapshot.delay()
    logger.info(f"Admin triggered snapshot task: {task.id}")

    return TaskResponse(task_id=task.id, task_name="take_snapshot", status="queued")


@router.post("/trigger/distribution", response_model=TaskResponse)
@limiter.limit("10/minute")
async def trigger_distribution(request: Request, _: str = Depends(verify_admin_key)):
    """
    Manually trigger distribution check.

    Checks if distribution triggers are met and executes
    GOLD distribution to holders if conditions are satisfied.
    """
    from app.tasks.distribution_task import check_distribution_triggers

    task = check_distribution_triggers.delay()
    logger.info(f"Admin triggered distribution task: {task.id}")

    return TaskResponse(
        task_id=task.id, task_name="check_distribution_triggers", status="queued"
    )


# ===========================================
# Status & Debug Endpoints
# ===========================================


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
@limiter.limit("30/minute")
async def get_task_status(
    request: Request, task_id: str, _: str = Depends(verify_admin_key)
):
    """
    Check the status of a Celery task by ID.
    """
    result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(
        task_id=task_id,
        status=result.status,
    )

    if result.ready():
        if result.successful():
            response.result = result.result
        else:
            response.error = str(result.result)

    return response


@router.get("/pending-rewards", response_model=PendingRewardsResponse)
@limiter.limit("30/minute")
async def get_pending_rewards(
    request: Request,
    _: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    View Creator Wallet SOL balance (pending rewards waiting for buyback).

    The buyback system now checks Creator Wallet balance directly via RPC
    instead of tracking individual rewards in the database.
    """
    from app.services.buyback import BuybackService
    from app.utils.solana_tx import keypair_from_base58
    from decimal import Decimal

    if not settings.creator_wallet_private_key:
        raise HTTPException(status_code=503, detail="Creator wallet not configured")

    # Get creator wallet address
    keypair = keypair_from_base58(settings.creator_wallet_private_key)
    creator_address = str(keypair.pubkey())

    # Get balance via BuybackService
    service = BuybackService(db)
    balance_sol = await service.get_creator_wallet_balance()
    balance_lamports = int(balance_sol * LAMPORTS_PER_SOL)

    min_threshold = Decimal(str(settings.buyback_min_sol_threshold))
    ready_to_process = balance_sol >= min_threshold

    return PendingRewardsResponse(
        creator_wallet_address=creator_address,
        creator_wallet_balance_sol=float(balance_sol),
        creator_wallet_balance_lamports=balance_lamports,
        min_threshold_sol=float(min_threshold),
        ready_to_process=ready_to_process,
    )


@router.get("/distribution-preview")
@limiter.limit("30/minute")
async def get_distribution_preview(
    request: Request,
    _: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Preview what the next distribution would look like (without executing).
    """
    from app.services.distribution import DistributionService

    service = DistributionService(db)

    try:
        status = await service.get_pool_status()
        plan = await service.calculate_distribution()

        if not plan:
            return {
                "status": "no_distribution",
                "pool_balance": status.balance,
                "pool_value_usd": float(status.value_usd),
                "reason": "no_eligible_recipients_or_empty_pool",
            }

        return {
            "status": "preview",
            "pool_amount": plan.pool_amount,
            "pool_value_usd": float(plan.pool_value_usd),
            "total_supply": plan.total_supply,
            "recipient_count": plan.recipient_count,
            "trigger_type": plan.trigger_type,
            "top_recipients": [
                {
                    "wallet": r.wallet[:8] + "...",
                    "share_pct": float(r.share_percentage),
                    "amount": r.amount,
                }
                for r in plan.recipients[:10]
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/pool-balance", response_model=PoolBalanceResponse)
@limiter.limit("30/minute")
async def get_pool_balance(request: Request, _: str = Depends(verify_admin_key)):
    """
    Check airdrop pool wallet balances (SOL + GOLD).
    """
    from app.services.helius import HeliusService
    from app.utils.solana_tx import keypair_from_base58

    if not settings.airdrop_pool_private_key:
        raise HTTPException(status_code=503, detail="Airdrop pool not configured")

    # Get pool address from private key
    keypair = keypair_from_base58(settings.airdrop_pool_private_key)
    pool_address = str(keypair.pubkey())

    helius = HeliusService()

    # Get SOL balance
    sol_lamports = await helius.get_sol_balance(pool_address)
    sol_balance = Decimal(sol_lamports) / LAMPORTS_PER_SOL

    # Get GOLD token balance
    gold_balance_raw = 0
    if settings.gold_token_mint:
        gold_balance_raw = await helius.get_token_balance(
            pool_address, settings.gold_token_mint
        )

    gold_balance = Decimal(gold_balance_raw) / GOLD_MULTIPLIER

    return PoolBalanceResponse(
        sol_balance=float(sol_balance),
        sol_balance_lamports=sol_lamports,
        gold_balance=float(gold_balance),
        gold_balance_raw=gold_balance_raw,
        pool_address=pool_address,
    )

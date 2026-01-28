# API Reference

Base URL: `http://localhost:8000` (dev) or `https://api.yourdomain.com` (prod)

API Docs: `/docs` (Swagger UI)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Global system statistics |
| GET | `/api/user/{wallet}` | User stats |
| GET | `/api/user/{wallet}/history` | Distribution history |
| GET | `/api/pool` | Reward pool status |
| GET | `/api/distributions` | Recent distributions |
| GET | `/api/leaderboard` | Top holders by balance |

## Response Examples

### GET /api/user/{wallet}

```json
{
  "wallet": "ABC123...",
  "balance": 1000000000,
  "rank": 42,
  "pool_share_percent": 0.15,
  "pending_reward": 12500,
  "total_earned": 150000
}
```

### GET /api/pool

```json
{
  "balance": 1.0,
  "balance_raw": 1000000,
  "value_usd": 5.12,
  "last_distribution": "2026-01-27T18:21:16Z",
  "hours_since_last": 0.65,
  "ready_to_distribute": true
}
```

Note: Distribution happens hourly whenever `ready_to_distribute` is true (pool balance > 0). No USD threshold or time limits.

### GET /api/stats

```json
{
  "total_holders": 1234,
  "total_distributed": 50000000,
  "pool_balance": 1000000,
  "last_distribution": "2026-01-27T18:21:16Z"
}
```

## Webhook

### POST /api/webhook/helius

Receives Helius transaction webhooks.

- Validates HMAC signature
- IP allowlist (Helius IPs only)

## Admin Endpoints

Requires `X-Admin-Key` header with valid `ADMIN_API_KEY`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/trigger/buyback` | Trigger buyback task |
| POST | `/api/admin/trigger/snapshot` | Trigger balance snapshot |
| POST | `/api/admin/trigger/distribution` | Trigger distribution check |
| GET | `/api/admin/task/{task_id}` | Check Celery task status |
| GET | `/api/admin/pending-rewards` | Creator Wallet balance |
| GET | `/api/admin/distribution-preview` | Preview next distribution |
| GET | `/api/admin/pool-balance` | Pool wallet balances |

### GET /api/admin/pending-rewards

Returns Creator Wallet SOL balance (pending rewards waiting for buyback).

```json
{
  "creator_wallet_address": "ABC123...",
  "creator_wallet_balance_sol": 0.5,
  "creator_wallet_balance_lamports": 500000000,
  "min_threshold_sol": 0.01,
  "ready_to_process": true
}
```

Note: The buyback system checks Creator Wallet balance directly via RPC instead of tracking individual rewards in a database table.

## Frontend API Client

`frontend/src/lib/api.ts`:

```typescript
getGlobalStats()               // GET /api/stats
getUserStats(wallet)           // GET /api/user/{wallet}
getLeaderboard(limit)          // GET /api/leaderboard
getPoolStatus()                // GET /api/pool
getDistributions(limit)        // GET /api/distributions
getDistributionHistory(wallet) // GET /api/user/{wallet}/history
```

## Frontend Pages

| Route | Purpose |
|-------|---------|
| `/` | Home/landing |
| `/leaderboard` | Top holders |
| `/docs` | Documentation |

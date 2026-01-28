# API Reference

Base URL: `http://localhost:8000` (dev) or `https://api.yourdomain.com` (prod)

API Docs: `/docs` (Swagger UI)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Global system statistics |
| GET | `/api/user/{wallet}` | User mining stats |
| GET | `/api/user/{wallet}/history` | Distribution history |
| GET | `/api/pool` | Reward pool status |
| GET | `/api/distributions` | Recent distributions |
| GET | `/api/leaderboard` | Top miners by hash power |
| GET | `/api/tiers` | Tier configurations |

## Response Examples

### GET /api/user/{wallet}

```json
{
  "wallet": "ABC123...",
  "balance": 1000000000,
  "twab": 950000000,
  "tier": 3,
  "tier_name": "Refined",
  "multiplier": 1.5,
  "hash_power": 1425000000,
  "rank": 42,
  "pool_share_percent": 0.15,
  "pending_reward": 12500,
  "total_earned": 150000,
  "is_new_holder": false
}
```

### GET /api/pool

```json
{
  "balance": 1000000,
  "balance_formatted": "1.00",
  "value_usd": 5.12,
  "gold_price": 5.12,
  "threshold_met": false,
  "time_trigger_met": false,
  "last_distribution": "2026-01-27T18:21:16Z",
  "next_distribution": "2026-01-27T19:00:00Z"
}
```

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

Receives Helius transaction webhooks for sell detection.

- Validates HMAC signature
- IP allowlist (Helius IPs only)
- Updates HoldStreak on sells

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
| `/dashboard` | Main mining dashboard |
| `/leaderboard` | Top holders |
| `/history` | Distribution history |
| `/docs` | Documentation |

## Dashboard Components

Located in `frontend/src/components/dashboard/`:

| Component | Purpose |
|-----------|---------|
| `MinerDisplay` | Main container |
| `MiningCard` | Balance + TWAB |
| `TierProgress` | Tier + progress bar |
| `PendingRewards` | Estimated pending GOLD |
| `ShareCard` | Pool share % |
| `RewardHistory` | Distribution table |
| `MiniLeaderboard` | Top 5 miners |

# Database Schema

## Tables Overview

| Table | Purpose |
|-------|---------|
| `snapshots` | Balance snapshot metadata |
| `balances` | Per-wallet balance at each snapshot |
| `creator_rewards` | Incoming Pump.fun rewards (DEPRECATED - see note) |
| `buybacks` | Jupiter swap records |
| `distributions` | Distribution cycles |
| `distribution_recipients` | Per-wallet distribution amounts |
| `excluded_wallets` | Wallets excluded from distributions |
| `system_stats` | Cached global stats |
| `distribution_lock` | Concurrency control |

## Model Details

### Snapshot
```python
id: UUID (PK)
timestamp: DateTime
total_holders: Integer
total_supply: BigInteger
```

### Balance
```python
id: UUID (PK)
snapshot_id: UUID (FK → Snapshot)
wallet: String(44)
balance: BigInteger
```

### CreatorReward (DEPRECATED)

> **Note:** This table is deprecated. The buyback system now checks Creator Wallet
> SOL balance directly via RPC (`HeliusService.get_sol_balance()`) instead of
> tracking individual rewards in the database. The table is kept for backward
> compatibility but is no longer actively used.

```python
id: UUID (PK)
amount_sol: BigInteger (lamports)
source: String
tx_signature: String (unique)
processed: Boolean
created_at: DateTime
```

### Buyback
```python
id: UUID (PK)
tx_signature: String (unique)
sol_amount: BigInteger
gold_amount: BigInteger
price_per_token: Float
created_at: DateTime
```

### Distribution
```python
id: UUID (PK)
pool_amount: BigInteger
pool_value_usd: Float
total_supply: BigInteger
recipient_count: Integer
trigger_type: String (hourly/manual)
created_at: DateTime
```

### DistributionRecipient
```python
id: UUID (PK)
distribution_id: UUID (FK → Distribution)
wallet: String(44)
balance: BigInteger
amount_received: BigInteger
tx_signature: String
```

## Migrations

Located in `backend/migrations/`:

| File | Purpose |
|------|---------|
| `001_initial.sql` | Complete schema with indexes |
| `002_distribution_lock.sql` | Concurrency control |
| `003_creator_rewards_unique_tx.sql` | Prevent webhook duplicates |
| `005_add_manual_trigger.sql` | Manual distribution support |
| `006_rename_copper_to_gold.sql` | Column rename |
| `007_remove_twab_tiers.sql` | Simplified distribution (Balance / Total Supply) |

## Run Migrations

```bash
cd backend
python run_migrations.py
```

## Neon Branches

- **main**: Production database
- **dev**: Development database

```bash
# Get connection strings
neonctl connection-string --project-id empty-shape-74454457           # prod
neonctl connection-string --project-id empty-shape-74454457 --branch dev  # dev
```

## Connection Test

```bash
python -c "import asyncio, asyncpg, os; asyncio.run(asyncpg.connect(os.getenv('DATABASE_URL')))"
```

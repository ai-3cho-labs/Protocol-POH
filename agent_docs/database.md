# Database Schema

## Tables Overview

| Table | Purpose |
|-------|---------|
| `snapshots` | Balance snapshot metadata |
| `balances` | Per-wallet balance at each snapshot |
| `hold_streaks` | Tier tracking per wallet |
| `creator_rewards` | Incoming Pump.fun rewards |
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

### HoldStreak
```python
wallet: String(44) (PK)
streak_start: DateTime
current_tier: Integer (1-6)
last_sell_at: DateTime (nullable)
```

### CreatorReward
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
total_hashpower: Float
recipient_count: Integer
trigger_type: String (threshold/time/hourly)
created_at: DateTime
```

### DistributionRecipient
```python
id: UUID (PK)
distribution_id: UUID (FK → Distribution)
wallet: String(44)
twab: Float
multiplier: Float
hash_power: Float
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
| `004_twab_optimization.sql` | Query optimization indexes |
| `005_add_manual_trigger.sql` | Manual distribution support |
| `006_rename_copper_to_gold.sql` | Column rename |

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

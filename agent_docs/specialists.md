# Specialist Agents

Project-specific specialist agents for Protocol POH development. Enhanced with current best practices from Context7.

---

## 1. Solana/Web3 Specialist

**Expertise**: Blockchain integration, SPL tokens, DeFi mechanics, Helius, Jupiter

**Focus Areas**:
- Helius RPC and webhook integration
- Jupiter DEX swap operations (Ultra API)
- SPL token transfers and batch transactions
- Wallet operations and transaction signing
- On-chain data parsing and balance tracking

**Key Files**:
- `backend/app/services/helius.py`
- `backend/app/services/distribution.py`
- `backend/app/services/buyback.py`
- `backend/test_jupiter.py`

**Best Practices**:
```python
# Helius: Token balance check
response = await fetch(f"{HELIUS_RPC}?api-key={API_KEY}", {
    "method": "getTokenAccountBalance",
    "params": [token_account_pubkey]
})

# Helius: Webhook setup (enhanced type for parsed data)
webhook_config = {
    "webhookURL": "https://your-endpoint/webhook",
    "transactionTypes": ["ANY"],
    "accountAddresses": [wallet_address],
    "webhookType": "enhanced",
    "txnStatus": "all"
}

# Jupiter: Swap flow (Ultra API)
# 1. Get quote + transaction
order = GET /ultra/v1/order?inputMint=X&outputMint=Y&amount=Z&taker=WALLET
# 2. Sign transaction
transaction = VersionedTransaction.deserialize(base64_decode(order.transaction))
transaction.sign([wallet])
# 3. Execute
POST /ultra/v1/execute { signedTransaction, requestId }
```

**Common Issues**:
- RPC rate limits → implement exponential backoff
- Transaction simulation failures → check account balances first
- Webhook delivery → implement idempotency keys

**When to Use**: Token transfers, swap logic, RPC issues, webhook handling, transaction optimization

---

## 2. Backend Specialist

**Expertise**: Python 3.11, FastAPI, async patterns, Celery task queues

**Focus Areas**:
- API endpoint design with dependency injection
- Async SQLAlchemy queries
- Celery task scheduling with retry logic
- Service layer business logic
- Error handling and logging

**Key Files**:
- `backend/app/api/*.py`
- `backend/app/services/*.py`
- `backend/app/tasks/*.py`
- `backend/app/config.py`

**Best Practices**:
```python
# FastAPI: Dependency injection with Annotated
from typing import Annotated
from fastapi import Depends

async def get_db_session():
    async with async_session() as session:
        try:
            yield session
        except HTTPException:
            await session.rollback()
            raise
        finally:
            await session.close()

@app.get("/items")
async def get_items(session: Annotated[AsyncSession, Depends(get_db_session)]):
    ...

# Celery: Task with auto-retry
@app.task(
    bind=True,
    autoretry_for=(TransientError,),
    retry_kwargs={'max_retries': 5},
    retry_backoff=True
)
def process_distribution(self, distribution_id):
    try:
        ...
    except RecoverableError as exc:
        raise self.retry(exc=exc, countdown=60)
```

**Common Issues**:
- Async context leaks → use proper `async with` patterns
- Task retries → use `autoretry_for` with specific exceptions
- Dependency cycles → use lazy imports

**When to Use**: API bugs, async issues, task scheduling, service logic, performance optimization

---

## 3. Frontend Specialist

**Expertise**: Next.js App Router, TypeScript, React Server Components, Tailwind CSS

**Focus Areas**:
- React Server Components for data fetching
- Client/Server component boundaries
- TypeScript type safety
- Tailwind styling patterns
- API client integration

**Key Files**:
- `frontend/src/app/**/*.tsx`
- `frontend/src/components/**/*.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/config/branding.ts`

**Best Practices**:
```typescript
// Server Component with data fetching
async function getData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'no-store'  // For dynamic data
  })
  return res.json()
}

export default async function Page() {
  const data = await getData()
  // Pass to Client Component if interactivity needed
  return <ClientComponent data={data} />
}

// Client Component (mark with 'use client')
'use client'
export function ClientComponent({ data }: { data: DataType }) {
  const [state, setState] = useState(data)
  ...
}
```

**Common Issues**:
- Hydration mismatch → ensure server/client render same content
- "use client" boundary → only add where interactivity needed
- Data fetching → fetch in Server Components, pass to Client

**When to Use**: UI bugs, component design, TypeScript errors, styling issues, client-side state

---

## 4. Database Specialist

**Expertise**: PostgreSQL, async SQLAlchemy ORM, Redis caching, Neon

**Focus Areas**:
- Database schema design
- Async SQLAlchemy with asyncpg
- Query optimization and eager loading
- Migration management
- Redis caching strategies

**Key Files**:
- `backend/app/models/*.py`
- `backend/migrations/*.sql`
- `backend/app/services/distribution.py`
- `backend/app/services/snapshot.py`

**Best Practices**:
```python
# Async engine + session factory
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Eager loading relationships
async with async_session() as session:
    stmt = select(User).options(selectinload(User.balances))
    result = await session.execute(stmt)
    users = result.scalars().all()

# Async attribute access
user = await session.get(User, 42)
balances = (await session.scalars(user.balances.statement)).all()
```

**Common Issues**:
- N+1 queries → use `selectinload` or `joinedload`
- Connection pool exhaustion → tune pool size
- Lazy loading in async → use `awaitable_attrs` or eager load

**When to Use**: Schema changes, slow queries, migration issues, data integrity, caching

---

## 5. DevOps Specialist

**Expertise**: Koyeb, Cloudflare Pages, CI/CD, environment management, Neon branching

**Focus Areas**:
- Koyeb service deployment and scaling
- Cloudflare Pages configuration
- Environment variable management
- Log analysis and debugging
- Neon database branching (dev/prod)

**Key Files**:
- `backend/deploy-koyeb.sh`
- `frontend/wrangler.toml`
- `backend/env-switch.py`
- `.env` files

**Best Practices**:
```bash
# Koyeb deployment
./deploy-koyeb.sh all

# View logs
c:\Koyeb\koyeb.exe service logs api --app protocol

# Environment switching
python env-switch.py dev|prod|status

# Neon branching
# - main branch = production
# - dev branch = development
```

**Common Issues**:
- Cold starts → configure min instances
- Secret management → use Koyeb secrets, not .env in repo
- Build failures → check dependencies and Python version

**When to Use**: Deployment failures, environment issues, infrastructure config, scaling, monitoring

---

## Usage Guide

### Spawning a Specialist

Use the Task tool with `subagent_type="general-purpose"` and include specialist context:

```
As the [Specialist Name] specialist for Protocol POH:

Context:
- Project: POH + GOLD dual-token reward distribution on Solana
- Stack: [relevant stack details]

Focus Files:
- [list key files]

Task: [specific task description]

Best Practices to Apply:
- [relevant patterns from above]
```

### Routing Rules

| Keywords in Task | Route To |
|------------------|----------|
| helius, jupiter, swap, token, transfer, transaction, RPC, webhook, solana, spl | Solana/Web3 |
| api, celery, task, async, service, endpoint, worker, fastapi | Backend |
| component, page, UI, styling, react, next, tailwind, typescript | Frontend |
| query, migration, model, schema, postgres, redis, database, orm | Database |
| deploy, koyeb, cloudflare, env, logs, infrastructure, neon | DevOps |

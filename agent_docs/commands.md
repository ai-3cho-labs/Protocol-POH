# Command Reference

## Development

```bash
# Backend - Single process (recommended)
cd backend
python env-switch.py dev
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

## Backend Commands

| Command | Description |
|---------|-------------|
| `python -m uvicorn app.main:app --reload` | Start API server (dev) |
| `python env-switch.py dev\|prod\|status\|diff` | Environment management |
| `python run_migrations.py` | Run database migrations |
| `celery -A app.tasks.celery_app worker --loglevel=info` | Celery worker |
| `celery -A app.tasks.celery_app beat --loglevel=info` | Celery scheduler |
| `celery -A app.tasks.celery_app inspect active` | Check active tasks |

## Testing

```bash
pytest                                    # All tests
pytest -v -s                              # Verbose
pytest tests/ -m 'not integration'        # Unit only
pytest tests/ --cov=app --cov-report=html # Coverage
```

## Code Quality

```bash
black .              # Format Python
ruff check --fix .   # Lint + autofix
mypy app/            # Type check
npm run lint         # Frontend lint
npm run type-check   # TypeScript check
```

## Frontend Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Dev server (localhost:3000) |
| `npm run build` | Production build |
| `npm run start` | Production server |

## Deployment (Koyeb)

```bash
./deploy-koyeb.sh all           # Deploy all services
./deploy-koyeb.sh api           # API only
./deploy-koyeb.sh worker        # Worker only
./deploy-koyeb.sh beat          # Beat only
./deploy-koyeb.sh logs-api      # View API logs
./deploy-koyeb.sh redeploy      # Redeploy all

# Direct Koyeb CLI (Windows: c:\Koyeb\koyeb.exe)
koyeb service list --app protocol
koyeb service logs api --app protocol -f
koyeb service redeploy api --app protocol
```

## Database (Neon)

```bash
neonctl auth
neonctl projects list
neonctl branches list --project-id empty-shape-74454457
neonctl connection-string --project-id empty-shape-74454457 --branch dev
```

## Redis (Upstash)

```bash
upstash auth login
upstash redis list
redis-cli --tls -u $REDIS_URL ping
```

## Connection Tests

```bash
# Database
python -c "import asyncio, asyncpg, os; asyncio.run(asyncpg.connect(os.getenv('DATABASE_URL')))"

# Redis
python -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"
```

## Git Workflow

```bash
git pull origin main
git add .
git commit -m "feat: description"
git push origin main   # Auto-deploys to Koyeb + Cloudflare
```

## Testing Scripts

```bash
python scripts/setup_devnet_testing.py --check
pytest tests/test_devnet_integration.py -v -s
```

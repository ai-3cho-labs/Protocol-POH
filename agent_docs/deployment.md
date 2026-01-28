# Deployment Guide

## Infrastructure Overview

- **Backend**: Koyeb (3 services: api, worker, beat)
- **Frontend**: Cloudflare Pages
- **Database**: Neon (PostgreSQL)
- **Redis**: Upstash

Auto-deploys on `git push origin main`.

## Koyeb Setup

### Install CLI

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | sh

# Windows (PowerShell)
iwr https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.ps1 -useb | iex

# Login
koyeb login
```

Windows CLI path: `c:\Koyeb\koyeb.exe`

### Create Secrets

```bash
koyeb secrets create DATABASE_URL --value "postgresql://..."
koyeb secrets create REDIS_URL --value "rediss://..."
koyeb secrets create HELIUS_API_KEY --value "..."
koyeb secrets create CREATOR_WALLET_PRIVATE_KEY --value "..."
koyeb secrets create AIRDROP_POOL_PRIVATE_KEY --value "..."
koyeb secrets create TEAM_WALLET_PUBLIC_KEY --value "..."
koyeb secrets create ALGO_BOT_WALLET_PUBLIC_KEY --value "..."
koyeb secrets create POH_TOKEN_MINT --value "..."
koyeb secrets create GOLD_TOKEN_MINT --value "GoLDppdjB1vDTPSGxyMJFqdnj134yH6Prg9eqsGDiw6A"
```

### Deploy

```bash
cd backend
./deploy-koyeb.sh all      # Deploy all
./deploy-koyeb.sh api      # API only
./deploy-koyeb.sh worker   # Worker only
./deploy-koyeb.sh beat     # Beat only
```

### Manage

```bash
koyeb service list --app protocol
koyeb service logs api --app protocol -f
koyeb service redeploy api --app protocol
./deploy-koyeb.sh delete   # Remove all
```

## Cloudflare Pages Setup

1. Cloudflare Dashboard → Pages → Create Project
2. Connect GitHub repo
3. Configure:
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Output directory: `.next`
4. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

## GitHub Actions CI/CD

Workflow: `.github/workflows/ci.yml`

| Job | Trigger | Description |
|-----|---------|-------------|
| `backend-test` | push/PR | Lint + pytest |
| `frontend-build` | push/PR | Lint + build |
| `security-scan` | push/PR | Trivy scan |
| `deploy-backend` | push to main | Deploy to Koyeb |
| `deploy-frontend` | push to main | Deploy to Cloudflare |

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `KOYEB_TOKEN` | `koyeb tokens create --name github-actions` |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID |
| `TEST_DATABASE_URL` | Neon dev branch URL |
| `TEST_REDIS_URL` | Upstash Redis URL |

## Database Migrations

```bash
# Test locally (dev branch)
cd backend
DATABASE_URL=<dev-url> python run_migrations.py

# Production (after deploy)
DATABASE_URL=<prod-url> python run_migrations.py
```

## Rollback

```bash
# Revert commit
git revert HEAD
git push origin main

# Force rollback (use with caution)
git reset --hard <commit-hash>
git push origin main --force

# Database: Neon Dashboard → Branches → Restore
```

## Environment Files

```
backend/
├── .env              # Active config (git-ignored)
├── .env.dev          # Development settings
├── .env.prod         # Production settings
├── .env.example      # Template (committed)
└── env-switch.py     # Easy switcher
```

#!/bin/bash
# ===========================================
# Koyeb Deployment Script
# ===========================================
# Prerequisites:
#   1. Install Koyeb CLI: curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | sh
#   2. Login: koyeb login
#   3. Create secrets first (see below)

set -e

APP_NAME="copper"
REGION="was"  # Washington DC (or: fra, sin, sao)
GITHUB_REPO="your-username/copper-processing-unit"  # Change this!
BRANCH="main"

# ===========================================
# Step 1: Create Secrets (run once)
# ===========================================
create_secrets() {
    echo "Creating secrets..."

    # Database
    koyeb secrets create DATABASE_URL --value "your-neon-connection-string"

    # Redis
    koyeb secrets create REDIS_URL --value "your-upstash-redis-url"

    # Helius
    koyeb secrets create HELIUS_API_KEY --value "your-helius-api-key"
    koyeb secrets create HELIUS_WEBHOOK_SECRET --value "your-webhook-secret"

    # Solana RPC
    koyeb secrets create SOLANA_RPC_URL --value "your-rpc-url"

    # Wallets
    koyeb secrets create CREATOR_WALLET_PRIVATE_KEY --value "your-private-key"
    koyeb secrets create AIRDROP_POOL_PRIVATE_KEY --value "your-private-key"
    koyeb secrets create TEAM_WALLET_PUBLIC_KEY --value "your-public-key"
    koyeb secrets create ALGO_BOT_WALLET_PUBLIC_KEY --value "your-public-key"

    # Tokens
    koyeb secrets create CPU_TOKEN_MINT --value "your-cpu-token-mint"
    koyeb secrets create GOLD_TOKEN_MINT --value "GoLDppdjB1vDTPSGxyMJFqdnj134yH6Prg9eqsGDiw6A"

    # Optional
    # koyeb secrets create SENTRY_DSN --value "your-sentry-dsn"

    echo "Secrets created!"
}

# ===========================================
# Step 2: Deploy API Service
# ===========================================
deploy_api() {
    echo "Deploying API service..."

    koyeb app create ${APP_NAME} --region ${REGION} 2>/dev/null || true

    koyeb service create api \
        --app ${APP_NAME} \
        --git github.com/${GITHUB_REPO} \
        --git-branch ${BRANCH} \
        --git-workdir backend \
        --git-builder docker \
        --git-docker-dockerfile Dockerfile.api \
        --instance-type nano \
        --regions ${REGION} \
        --port 8000:http \
        --route /:8000 \
        --health-check-path /api/health \
        --health-check-port 8000 \
        --env ENVIRONMENT=production \
        --env PORT=8000 \
        --env DATABASE_URL=@DATABASE_URL \
        --env REDIS_URL=@REDIS_URL \
        --env CELERY_BROKER_URL=@REDIS_URL \
        --env CELERY_RESULT_BACKEND=@REDIS_URL \
        --env HELIUS_API_KEY=@HELIUS_API_KEY \
        --env HELIUS_WEBHOOK_SECRET=@HELIUS_WEBHOOK_SECRET \
        --env SOLANA_RPC_URL=@SOLANA_RPC_URL \
        --env CREATOR_WALLET_PRIVATE_KEY=@CREATOR_WALLET_PRIVATE_KEY \
        --env AIRDROP_POOL_PRIVATE_KEY=@AIRDROP_POOL_PRIVATE_KEY \
        --env TEAM_WALLET_PUBLIC_KEY=@TEAM_WALLET_PUBLIC_KEY \
        --env ALGO_BOT_WALLET_PUBLIC_KEY=@ALGO_BOT_WALLET_PUBLIC_KEY \
        --env CPU_TOKEN_MINT=@CPU_TOKEN_MINT \
        --env GOLD_TOKEN_MINT=@GOLD_TOKEN_MINT

    echo "API deployed!"
}

# ===========================================
# Step 3: Deploy Worker Service
# ===========================================
deploy_worker() {
    echo "Deploying Worker service..."

    koyeb service create worker \
        --app ${APP_NAME} \
        --git github.com/${GITHUB_REPO} \
        --git-branch ${BRANCH} \
        --git-workdir backend \
        --git-builder docker \
        --git-docker-dockerfile Dockerfile.worker \
        --instance-type nano \
        --regions ${REGION} \
        --env ENVIRONMENT=production \
        --env DATABASE_URL=@DATABASE_URL \
        --env REDIS_URL=@REDIS_URL \
        --env CELERY_BROKER_URL=@REDIS_URL \
        --env CELERY_RESULT_BACKEND=@REDIS_URL \
        --env HELIUS_API_KEY=@HELIUS_API_KEY \
        --env SOLANA_RPC_URL=@SOLANA_RPC_URL \
        --env CREATOR_WALLET_PRIVATE_KEY=@CREATOR_WALLET_PRIVATE_KEY \
        --env AIRDROP_POOL_PRIVATE_KEY=@AIRDROP_POOL_PRIVATE_KEY \
        --env TEAM_WALLET_PUBLIC_KEY=@TEAM_WALLET_PUBLIC_KEY \
        --env ALGO_BOT_WALLET_PUBLIC_KEY=@ALGO_BOT_WALLET_PUBLIC_KEY \
        --env CPU_TOKEN_MINT=@CPU_TOKEN_MINT \
        --env GOLD_TOKEN_MINT=@GOLD_TOKEN_MINT

    echo "Worker deployed!"
}

# ===========================================
# Step 4: Deploy Beat Service
# ===========================================
deploy_beat() {
    echo "Deploying Beat scheduler..."

    koyeb service create beat \
        --app ${APP_NAME} \
        --git github.com/${GITHUB_REPO} \
        --git-branch ${BRANCH} \
        --git-workdir backend \
        --git-builder docker \
        --git-docker-dockerfile Dockerfile.beat \
        --instance-type nano \
        --regions ${REGION} \
        --env ENVIRONMENT=production \
        --env DATABASE_URL=@DATABASE_URL \
        --env REDIS_URL=@REDIS_URL \
        --env CELERY_BROKER_URL=@REDIS_URL \
        --env CELERY_RESULT_BACKEND=@REDIS_URL \
        --env HELIUS_API_KEY=@HELIUS_API_KEY \
        --env SOLANA_RPC_URL=@SOLANA_RPC_URL \
        --env CREATOR_WALLET_PRIVATE_KEY=@CREATOR_WALLET_PRIVATE_KEY \
        --env AIRDROP_POOL_PRIVATE_KEY=@AIRDROP_POOL_PRIVATE_KEY \
        --env TEAM_WALLET_PUBLIC_KEY=@TEAM_WALLET_PUBLIC_KEY \
        --env ALGO_BOT_WALLET_PUBLIC_KEY=@ALGO_BOT_WALLET_PUBLIC_KEY \
        --env CPU_TOKEN_MINT=@CPU_TOKEN_MINT \
        --env GOLD_TOKEN_MINT=@GOLD_TOKEN_MINT

    echo "Beat deployed!"
}

# ===========================================
# Utility Commands
# ===========================================

# List all services
list_services() {
    koyeb service list --app ${APP_NAME}
}

# View logs
logs_api() {
    koyeb service logs api --app ${APP_NAME}
}

logs_worker() {
    koyeb service logs worker --app ${APP_NAME}
}

logs_beat() {
    koyeb service logs beat --app ${APP_NAME}
}

# Redeploy services
redeploy_api() {
    koyeb service redeploy api --app ${APP_NAME}
}

redeploy_worker() {
    koyeb service redeploy worker --app ${APP_NAME}
}

redeploy_beat() {
    koyeb service redeploy beat --app ${APP_NAME}
}

redeploy_all() {
    redeploy_api
    redeploy_worker
    redeploy_beat
}

# Delete services
delete_all() {
    echo "Deleting all services..."
    koyeb service delete api --app ${APP_NAME} -y || true
    koyeb service delete worker --app ${APP_NAME} -y || true
    koyeb service delete beat --app ${APP_NAME} -y || true
    koyeb app delete ${APP_NAME} -y || true
    echo "Deleted!"
}

# ===========================================
# Main
# ===========================================
case "$1" in
    secrets)
        create_secrets
        ;;
    api)
        deploy_api
        ;;
    worker)
        deploy_worker
        ;;
    beat)
        deploy_beat
        ;;
    all)
        deploy_api
        deploy_worker
        deploy_beat
        ;;
    list)
        list_services
        ;;
    logs-api)
        logs_api
        ;;
    logs-worker)
        logs_worker
        ;;
    logs-beat)
        logs_beat
        ;;
    redeploy)
        redeploy_all
        ;;
    delete)
        delete_all
        ;;
    *)
        echo "Usage: $0 {secrets|api|worker|beat|all|list|logs-api|logs-worker|logs-beat|redeploy|delete}"
        echo ""
        echo "Commands:"
        echo "  secrets     - Create all secrets (run once)"
        echo "  api         - Deploy API service"
        echo "  worker      - Deploy Celery worker"
        echo "  beat        - Deploy Celery beat scheduler"
        echo "  all         - Deploy all services"
        echo "  list        - List all services"
        echo "  logs-api    - View API logs"
        echo "  logs-worker - View worker logs"
        echo "  logs-beat   - View beat logs"
        echo "  redeploy    - Redeploy all services"
        echo "  delete      - Delete all services"
        exit 1
        ;;
esac

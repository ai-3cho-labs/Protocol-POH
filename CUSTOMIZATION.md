# White-Label Customization Guide

Deploy your own version of the Protocol with custom branding, tokens, and reward splits.

## Quick Start

1. Fork/clone the repository
2. Configure environment variables
3. Replace branding assets
4. Deploy

---

## Backend Configuration

Set these environment variables in your backend `.env` or hosting platform (Koyeb, etc.):

### Token Configuration

```env
# Your token mint addresses
POH_TOKEN_MINT=YourHoldTokenMintAddress
GOLD_TOKEN_MINT=YourRewardTokenMintAddress

# Token decimals (default: 9 for hold, 6 for reward)
POH_TOKEN_DECIMALS=9
GOLD_TOKEN_DECIMALS=6
```

### Reward Split

Configure how creator rewards are distributed (must total 100):

```env
# Main split (default: 80/10/10)
REWARD_POOL_PERCENT=80    # % to airdrop pool
ALGO_BOT_PERCENT=10       # % to trading bot
TEAM_PERCENT=10           # % to team wallet

# Buyback split (of pool allocation)
BUYBACK_SWAP_PERCENT=20   # % swapped to reward token
BUYBACK_RESERVE_PERCENT=80 # % kept as SOL reserves
```

### Token Branding (for logs)

```env
HOLD_TOKEN_SYMBOL=POH
REWARD_TOKEN_SYMBOL=GOLD
```

### Wallets

```env
CREATOR_WALLET_PRIVATE_KEY=Base58EncodedPrivateKey
AIRDROP_POOL_PRIVATE_KEY=Base58EncodedPrivateKey
TEAM_WALLET_PUBLIC_KEY=YourTeamWalletAddress
ALGO_BOT_WALLET_PUBLIC_KEY=YourBotWalletAddress
```

### Distribution Settings

```env
DISTRIBUTION_THRESHOLD_USD=250  # Min USD value to trigger distribution
DISTRIBUTION_MAX_HOURS=24       # Max hours between distributions
MIN_BALANCE_USD=50              # Min balance to qualify for rewards
```

---

## Frontend Configuration

Set these in your frontend `.env.local` or Cloudflare Pages environment:

### App Identity

```env
NEXT_PUBLIC_APP_NAME=Your App Name
NEXT_PUBLIC_APP_SHORT_NAME=APP
NEXT_PUBLIC_TAGLINE=Your Catchy Tagline Here
NEXT_PUBLIC_DOMAIN=yourapp.xyz
```

### Token Branding

```env
NEXT_PUBLIC_HOLD_TOKEN_SYMBOL=TOKEN
NEXT_PUBLIC_HOLD_TOKEN_NAME=Your Hold Token
NEXT_PUBLIC_REWARD_TOKEN_SYMBOL=REWARD
NEXT_PUBLIC_REWARD_TOKEN_NAME=Your Reward Token
```

### Links

```env
NEXT_PUBLIC_BUY_TOKEN_URL=https://pump.fun/your-token
NEXT_PUBLIC_BUY_TOKEN_LABEL=Buy TOKEN on Pump.fun

# Social links
NEXT_PUBLIC_TWITTER_URL=https://x.com/yourproject
NEXT_PUBLIC_TELEGRAM_URL=https://t.me/yourproject
NEXT_PUBLIC_CONTRACT_URL=https://solscan.io/token/YourMintAddress
```

### Legal

```env
NEXT_PUBLIC_COPYRIGHT_HOLDER=Your Project Name
NEXT_PUBLIC_DISCLAIMER=TOKEN and REWARD are memecoins with no intrinsic value...
```

### Theme Colors

```env
NEXT_PUBLIC_ACCENT_COLOR=#f59e0b    # Primary accent (hex)
NEXT_PUBLIC_ACCENT_LIGHT=#fbbf24   # Light accent variant
NEXT_PUBLIC_THEME_COLOR=#0a0a0a    # Browser theme color
```

### API Connection

```env
NEXT_PUBLIC_API_URL=https://your-api.koyeb.app
NEXT_PUBLIC_WS_URL=wss://your-api.koyeb.app/ws
NEXT_PUBLIC_POH_TOKEN_MINT=YourHoldTokenMintAddress
NEXT_PUBLIC_GOLD_TOKEN_MINT=YourRewardTokenMintAddress
```

---

## Branding Assets

Replace the files in `frontend/public/branding/`:

| File | Dimensions | Purpose |
|------|------------|---------|
| `logo.jpg` | 1024x1024 | Main logo (high-res) |
| `logo-small.jpg` | 256x256 | Header navigation logo |
| `icon.jpg` | 192x192 | Favicon / PWA icon |
| `og-image.jpg` | 1200x630 | Social sharing preview |

### Supported Formats

- `.jpg`, `.png`, `.webp`
- If using a different extension, update references in:
  - `src/app/layout.tsx`
  - `src/components/layout/Header.tsx`

---

## Example: Custom Deployment

### "Moon Mining Protocol" Example

**Backend `.env`:**
```env
CPU_TOKEN_MINT=MoonTokenMintAddress123
GOLD_TOKEN_MINT=StardustTokenMintAddress456

REWARD_POOL_PERCENT=70
ALGO_BOT_PERCENT=15
TEAM_PERCENT=15

HOLD_TOKEN_SYMBOL=MOON
REWARD_TOKEN_SYMBOL=DUST
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_APP_NAME=Moon Mining Protocol
NEXT_PUBLIC_APP_SHORT_NAME=Moon Mine
NEXT_PUBLIC_TAGLINE=Mine Stardust From The Moon

NEXT_PUBLIC_HOLD_TOKEN_SYMBOL=MOON
NEXT_PUBLIC_HOLD_TOKEN_NAME=Moon Token
NEXT_PUBLIC_REWARD_TOKEN_SYMBOL=DUST
NEXT_PUBLIC_REWARD_TOKEN_NAME=Stardust

NEXT_PUBLIC_BUY_TOKEN_URL=https://pump.fun/moon
NEXT_PUBLIC_BUY_TOKEN_LABEL=Buy MOON on Pump.fun
NEXT_PUBLIC_DOMAIN=moonmine.xyz

NEXT_PUBLIC_ACCENT_COLOR=#8b5cf6
NEXT_PUBLIC_COPYRIGHT_HOLDER=Moon Mining DAO
```

---

## Deployment Checklist

- [ ] Set all backend environment variables
- [ ] Set all frontend environment variables
- [ ] Replace branding images in `public/branding/`
- [ ] Update social links
- [ ] Test locally with `npm run dev` / `uvicorn`
- [ ] Run database migrations
- [ ] Deploy backend (Koyeb/Railway/etc.)
- [ ] Deploy frontend (Cloudflare Pages/Vercel/etc.)
- [ ] Verify API connection
- [ ] Test token display and branding
- [ ] Test reward distribution flow

---

## Defaults Reference

If environment variables are not set, these defaults are used:

| Variable | Default |
|----------|---------|
| `REWARD_POOL_PERCENT` | 80 |
| `ALGO_BOT_PERCENT` | 10 |
| `TEAM_PERCENT` | 10 |
| `BUYBACK_SWAP_PERCENT` | 20 |
| `HOLD_TOKEN_SYMBOL` | POH |
| `REWARD_TOKEN_SYMBOL` | GOLD |
| `NEXT_PUBLIC_APP_NAME` | Protocol |
| `NEXT_PUBLIC_TAGLINE` | Proof of Hold |
| `NEXT_PUBLIC_ACCENT_COLOR` | #f59e0b (amber) |

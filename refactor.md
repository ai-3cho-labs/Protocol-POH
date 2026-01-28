# White-Label Modularization Plan

Make the protocol reusable for any token pair without code changes - only environment variables and branding assets.

## Status: ✅ COMPLETED

## Overview

| Area | Current | After |
|------|---------|-------|
| Reward splits | Hardcoded 80/10/10 | Configurable via env |
| Tier config | Hardcoded in code | JSON env var or defaults |
| Token symbols | "CPU"/"GOLD" hardcoded | Env vars |
| Frontend branding | Hardcoded everywhere | Central config file |
| Logos/assets | Fixed files | Replaceable `/branding/` folder |

---

## Phase 1: Backend Configuration ✅

### Files to Modify

**`backend/app/config.py`** - Add new settings:
```python
# Reward Split (must total 100)
reward_pool_percent: int = 80
algo_bot_percent: int = 10
team_percent: int = 10

# Buyback Split (of the pool allocation)
buyback_swap_percent: int = 20
buyback_reserve_percent: int = 80

# Token Branding (for logs/display)
hold_token_symbol: str = "CPU"
reward_token_symbol: str = "GOLD"

# Tier Config (optional JSON override)
tier_config_json: str = ""
```

**`backend/app/services/buyback.py`** - Replace hardcoded splits:
- Line 155-157: Use `settings.reward_pool_percent / 100` instead of `Decimal("0.8")`
- Line 645: Use `settings.buyback_swap_percent / 100` instead of `Decimal("0.20")`

**`backend/.env.example`** - Document new variables

---

## Phase 2: Frontend Branding System ✅

### New Files to Create

**`frontend/src/config/branding.ts`**:
```typescript
export const branding = {
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'Copper Processing Unit',
  appShortName: process.env.NEXT_PUBLIC_APP_SHORT_NAME || 'CPU Mine',
  tagline: process.env.NEXT_PUBLIC_TAGLINE || 'The Working Man\'s Gold Mine',

  holdToken: {
    symbol: process.env.NEXT_PUBLIC_HOLD_TOKEN_SYMBOL || 'CPU',
    name: process.env.NEXT_PUBLIC_HOLD_TOKEN_NAME || 'Copper Processing Unit',
  },
  rewardToken: {
    symbol: process.env.NEXT_PUBLIC_REWARD_TOKEN_SYMBOL || 'GOLD',
    name: process.env.NEXT_PUBLIC_REWARD_TOKEN_NAME || 'Gold Token',
  },

  domain: process.env.NEXT_PUBLIC_DOMAIN || 'cpu-mine.xyz',
  buyTokenUrl: process.env.NEXT_PUBLIC_BUY_TOKEN_URL || 'https://pump.fun',
  buyTokenLabel: process.env.NEXT_PUBLIC_BUY_TOKEN_LABEL || 'Buy CPU on Pump.fun',

  socials: {
    twitter: process.env.NEXT_PUBLIC_TWITTER_URL,
    telegram: process.env.NEXT_PUBLIC_TELEGRAM_URL,
  },

  disclaimer: process.env.NEXT_PUBLIC_DISCLAIMER || 'CPU and $GOLD are memecoins...',
  copyrightHolder: process.env.NEXT_PUBLIC_COPYRIGHT_HOLDER || 'CPU Mine',
};
```

**`frontend/src/config/theme.ts`**:
```typescript
export const themeColors = {
  accent: process.env.NEXT_PUBLIC_ACCENT_COLOR || '#f59e0b',
  accentLight: process.env.NEXT_PUBLIC_ACCENT_LIGHT || '#fbbf24',
};
```

**`frontend/src/config/index.ts`** - Barrel export

### Files to Modify

| File | Changes |
|------|---------|
| `constants.ts` | Import from branding config |
| `layout.tsx` | Use `branding.*` for metadata |
| `Hero.tsx` | Use `branding.tagline`, `branding.holdToken.symbol` |
| `Footer.tsx` | Use `branding.copyrightHolder`, `branding.socials` |
| `HowItWorks.tsx` | Use `branding.holdToken.symbol`, `branding.rewardToken.symbol` |
| `shareCard.ts` | Use `branding.*` and `themeColors.*` |
| `MinerDisplay.tsx` | Use `branding.rewardToken.symbol` |
| `Header.tsx` | Use branding for logo alt text |

---

## Phase 3: Asset Structure ✅

### Create directory structure:
```
frontend/public/branding/
  logo.png          # 1024x1024 main logo
  logo-small.png    # 256x256 for header
  icon.png          # 192x192 favicon
  og-image.png      # 1200x630 Open Graph
```

### Update references:
- `layout.tsx`: icons and OG images point to `/branding/`
- `Header.tsx`: logo src from `/branding/logo-small.png`

---

## New Environment Variables

### Backend (.env)
```env
# Reward Split
REWARD_POOL_PERCENT=80
ALGO_BOT_PERCENT=10
TEAM_PERCENT=10
BUYBACK_SWAP_PERCENT=20

# Token Symbols
HOLD_TOKEN_SYMBOL=CPU
REWARD_TOKEN_SYMBOL=GOLD
```

### Frontend (.env.local)
```env
# Branding
NEXT_PUBLIC_APP_NAME=Copper Processing Unit
NEXT_PUBLIC_APP_SHORT_NAME=CPU Mine
NEXT_PUBLIC_TAGLINE=The Working Man's Gold Mine
NEXT_PUBLIC_DOMAIN=cpu-mine.xyz

# Tokens
NEXT_PUBLIC_HOLD_TOKEN_SYMBOL=CPU
NEXT_PUBLIC_REWARD_TOKEN_SYMBOL=GOLD

# Links
NEXT_PUBLIC_BUY_TOKEN_URL=https://pump.fun
NEXT_PUBLIC_BUY_TOKEN_LABEL=Buy CPU on Pump.fun

# Theme
NEXT_PUBLIC_ACCENT_COLOR=#f59e0b
```

---

## Verification

1. **Backend**: Run `python test_celery_tasks.py all` - should work with defaults
2. **Frontend**: Run `npm run build` - no hardcoded references errors
3. **New deployment test**:
   - Change token symbols in env
   - Replace logos in `/branding/`
   - Verify UI shows new branding
4. **Existing deployment**: Verify unchanged behavior with defaults

---

## Implementation Order

1. Backend config changes (low risk, defaults preserve behavior)
2. Create frontend config files
3. Update `constants.ts` and `layout.tsx`
4. Update landing page components
5. Update dashboard components
6. Update shareCard.ts
7. Restructure assets folder
8. Update `.env.example` files with documentation

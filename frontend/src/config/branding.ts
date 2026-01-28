/**
 * Branding Configuration
 *
 * Centralized branding for white-label deployments.
 * Override via environment variables for custom deployments.
 */

export const branding = {
  // App identity
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'Copper Processing Unit',
  appShortName: process.env.NEXT_PUBLIC_APP_SHORT_NAME || 'CPU Mine',
  tagline: process.env.NEXT_PUBLIC_TAGLINE || "The Working Man's Gold Mine",

  // Token branding
  holdToken: {
    symbol: process.env.NEXT_PUBLIC_HOLD_TOKEN_SYMBOL || 'CPU',
    name: process.env.NEXT_PUBLIC_HOLD_TOKEN_NAME || 'Copper Processing Unit',
  },
  rewardToken: {
    symbol: process.env.NEXT_PUBLIC_REWARD_TOKEN_SYMBOL || 'GOLD',
    name: process.env.NEXT_PUBLIC_REWARD_TOKEN_NAME || 'Gold Token',
  },

  // Links
  domain: process.env.NEXT_PUBLIC_DOMAIN || 'cpu-mine.xyz',
  buyTokenUrl: process.env.NEXT_PUBLIC_BUY_TOKEN_URL || 'https://pump.fun',
  buyTokenLabel:
    process.env.NEXT_PUBLIC_BUY_TOKEN_LABEL ||
    `Buy ${process.env.NEXT_PUBLIC_HOLD_TOKEN_SYMBOL || 'CPU'} on Pump.fun`,

  // Social links
  socials: {
    twitter: process.env.NEXT_PUBLIC_TWITTER_URL || 'https://x.com',
    telegram: process.env.NEXT_PUBLIC_TELEGRAM_URL || 'https://t.me',
    contract: process.env.NEXT_PUBLIC_CONTRACT_URL || 'https://solscan.io',
  },

  // Legal
  disclaimer:
    process.env.NEXT_PUBLIC_DISCLAIMER ||
    `${process.env.NEXT_PUBLIC_HOLD_TOKEN_SYMBOL || 'CPU'} and $${process.env.NEXT_PUBLIC_REWARD_TOKEN_SYMBOL || 'GOLD'} are memecoins with no intrinsic value or expectation of financial return. Not financial advice. Trade at your own risk.`,
  copyrightHolder: process.env.NEXT_PUBLIC_COPYRIGHT_HOLDER || 'CPU Mine',

  // SEO
  seoDescription:
    process.env.NEXT_PUBLIC_SEO_DESCRIPTION ||
    `Hold ${process.env.NEXT_PUBLIC_HOLD_TOKEN_SYMBOL || 'CPU'} tokens to mine $${process.env.NEXT_PUBLIC_REWARD_TOKEN_SYMBOL || 'GOLD'} rewards. Trading fees fund the pool. Build streaks, get paid.`,
  seoKeywords: (
    process.env.NEXT_PUBLIC_SEO_KEYWORDS ||
    'solana,memecoin,mining,crypto,rewards,defi,cpu,gold'
  ).split(','),
} as const;

// Type for branding config
export type Branding = typeof branding;

/**
 * Application Constants
 */

import { branding } from '@/config';

// ===========================================
// API Configuration
// ===========================================

/** Base URL for the backend API */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/** WebSocket URL for real-time updates */
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000';

/** API Key for authenticated requests (optional for public endpoints) */
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

/**
 * Solana RPC URL
 * In production, use the proxy to keep API key server-side.
 * Falls back to direct RPC URL if configured.
 */
export const SOLANA_RPC_URL = process.env.NEXT_PUBLIC_SOLANA_RPC_URL
  || `${API_BASE_URL}/api/proxy/rpc`;

// ===========================================
// UI Configuration
// ===========================================

/** Desktop breakpoint in pixels */
export const DESKTOP_BREAKPOINT = 768;

/** Token decimals for hold token */
export const TOKEN_DECIMALS = 6;

/** Hold token symbol - what users hold for eligibility */
export const POH_TOKEN_SYMBOL = branding.holdToken.symbol;

/** Reward token symbol - what users earn as rewards */
export const TOKEN_SYMBOL = branding.rewardToken.symbol;

/** Hold token mint address */
export const POH_TOKEN_MINT = process.env.NEXT_PUBLIC_POH_TOKEN_MINT || '';

/** Reward token mint address */
export const TOKEN_MINT = process.env.NEXT_PUBLIC_GOLD_TOKEN_MINT || '';

// ===========================================
// Explorer URLs
// ===========================================

/** Base URL for Solscan explorer */
export const SOLSCAN_BASE_URL = 'https://solscan.io';

/**
 * Get Solscan URL for a wallet address
 * Validates address format to prevent URL injection
 */
export function getAddressUrl(address: string): string {
  // Import validation inline to avoid circular deps
  const base58Regex = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;
  if (!address || !base58Regex.test(address)) {
    return '#'; // Safe fallback for invalid addresses
  }
  return `${SOLSCAN_BASE_URL}/account/${encodeURIComponent(address)}`;
}

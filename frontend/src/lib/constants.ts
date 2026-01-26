/**
 * Application Constants
 */

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
// Query Configuration
// ===========================================

/** Default stale time for React Query (5 minutes) */
export const DEFAULT_STALE_TIME = 5 * 60 * 1000;

/** Default refetch interval for global stats (30 seconds) */
export const DEFAULT_REFETCH_INTERVAL = 30 * 1000;

/** Refetch interval for pool status (15 seconds) */
export const POOL_REFETCH_INTERVAL = 15 * 1000;

/** Refetch interval for user stats (30 seconds) */
export const USER_STATS_REFETCH_INTERVAL = 30 * 1000;

// ===========================================
// UI Configuration
// ===========================================

/** Desktop breakpoint in pixels */
export const DESKTOP_BREAKPOINT = 768;

/** Token decimals for CPU */
export const TOKEN_DECIMALS = 6;

/** CPU token symbol - what users hold for mining eligibility */
export const CPU_TOKEN_SYMBOL = 'CPU';

/** GOLD token symbol - what users earn as rewards */
export const TOKEN_SYMBOL = 'GOLD';

/** CPU token mint address */
export const CPU_TOKEN_MINT = process.env.NEXT_PUBLIC_CPU_TOKEN_MINT || '';

/** GOLD token mint address */
export const TOKEN_MINT = process.env.NEXT_PUBLIC_GOLD_TOKEN_MINT || '';

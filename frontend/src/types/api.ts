/**
 * API Response Types
 * These types match the backend API responses exactly.
 * Reference: backend/app/api/routes.py
 */

// ===========================================
// API Response Types
// ===========================================

/** GET /api/stats - Global statistics */
export interface GlobalStatsResponse {
  /** Total number of token holders */
  total_holders: number;
  /** 24-hour trading volume */
  total_volume_24h: number;
  /** Total SOL spent on buybacks */
  total_buybacks_sol: number;
  /** Total tokens distributed (human-readable) */
  total_distributed: number;
  /** When last balance snapshot occurred (ISO string) */
  last_snapshot_at: string | null;
  /** When last distribution was executed (ISO string) */
  last_distribution_at: string | null;
}

/** GET /api/user/{wallet} - User mining statistics */
export interface UserStatsResponse {
  /** User's wallet address */
  wallet: string;
  /** Current token balance (human-readable) */
  balance: number;
  /** Current token balance (raw with decimals) */
  balance_raw: number;
  /** Global rank by balance */
  rank: number | null;
  /** Estimated pending reward from pool */
  pending_reward_estimate: number;
  /** User's percentage share of the reward pool */
  pool_share_percent: number;
  /** Is this a new holder with no snapshot data yet? */
  is_new_holder?: boolean;
}

/** GET /api/user/{wallet}/history - Distribution history item */
export interface DistributionHistoryItem {
  /** UUID of the distribution */
  distribution_id: string;
  /** When distribution was executed (ISO string) */
  executed_at: string;
  /** User's balance at that time */
  balance: number;
  /** User's share percentage at that time */
  share_percent: number;
  /** Tokens received (human-readable) */
  amount_received: number;
  /** Solana transaction signature */
  tx_signature: string | null;
}

/** GET /api/leaderboard - Leaderboard entry */
export interface LeaderboardEntry {
  /** Position on leaderboard (1-indexed) */
  rank: number;
  /** Full wallet address */
  wallet: string;
  /** Shortened wallet format (first 4 + last 4) */
  wallet_short: string;
  /** Total GOLD earned across all distributions */
  total_earned: number;
}

/** GET /api/pool - Airdrop pool status */
export interface PoolStatusResponse {
  /** Pool balance (human-readable tokens) */
  balance: number;
  /** Pool balance (raw with decimals) */
  balance_raw: number;
  /** Current USD value of pool */
  value_usd: number;
  /** Current GOLD token price in USD */
  gold_price_usd: number;
  /** When last distribution occurred (ISO string) */
  last_distribution: string | null;
  /** Hours elapsed since last distribution */
  hours_since_last: number | null;
  /** Whether pool has balance to distribute */
  ready_to_distribute: boolean;
}

/** GET /api/distributions - Distribution record */
export interface DistributionItem {
  /** UUID of distribution */
  id: string;
  /** Total tokens distributed (human-readable) */
  pool_amount: number;
  /** USD value of pool at execution */
  pool_value_usd: number | null;
  /** Total supply at distribution time */
  total_supply: number;
  /** Number of wallets that received rewards */
  recipient_count: number;
  /** What triggered the distribution */
  trigger_type: 'hourly' | 'manual';
  /** When distribution occurred (ISO string) */
  executed_at: string;
}

// ===========================================
// Error Types
// ===========================================

/** API error response */
export interface ApiError {
  /** HTTP status code */
  status: number;
  /** Error message */
  message: string;
  /** Additional error detail */
  detail?: string;
}

/** Type guard for API errors */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    'message' in error
  );
}

// ===========================================
// Request Parameter Types
// ===========================================

/** Pagination parameters */
export interface PaginationParams {
  /** Number of items to return (default: 10) */
  limit?: number;
  /** Offset for pagination */
  offset?: number;
}

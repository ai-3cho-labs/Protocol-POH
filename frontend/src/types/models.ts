/**
 * Domain Models
 * Transformed/computed types for UI consumption.
 * These extend API types with additional computed properties.
 */

// ===========================================
// User Models
// ===========================================

/** Transformed user mining statistics for UI */
export interface UserMiningStats {
  /** Wallet address */
  wallet: string;
  /** Current balance (human-readable) */
  balance: number;
  /** Current balance (raw) */
  balanceRaw: number;
  /** Global rank */
  rank: number | null;
  /** Pending reward estimate */
  pendingReward: number;
  /** User's percentage share of the reward pool */
  poolSharePercent: number;
  /** Is this a new holder with no snapshot data yet? */
  isNewHolder: boolean;
}

// ===========================================
// Pool Models
// ===========================================

/** Transformed pool information for UI */
export interface PoolInfo {
  /** Pool balance (human-readable) */
  balance: number;
  /** Pool balance (raw) */
  balanceRaw: number;
  /** Current USD value */
  valueUsd: number;
  /** Current GOLD token price in USD */
  goldPriceUsd: number;
  /** Last payout timestamp */
  lastPayout: Date | null;
  /** Hours since last payout */
  hoursSinceLast: number | null;
  /** Whether pool has balance to distribute */
  readyToDistribute: boolean;
}

// ===========================================
// Leaderboard Models
// ===========================================

/** Leaderboard entry with formatted data */
export interface LeaderboardUser {
  /** Position on leaderboard */
  rank: number;
  /** Full wallet address */
  wallet: string;
  /** Shortened wallet (4...4) */
  walletShort: string;
  /** Balance */
  balance: number;
  /** Is this the connected user? */
  isCurrentUser: boolean;
}

// ===========================================
// Transaction Models
// ===========================================

/** Payout with formatted data */
export interface FormattedPayout {
  /** Payout ID */
  id: string;
  /** Pool amount */
  poolAmount: number;
  /** USD value */
  poolValueUsd: number | null;
  /** Total supply */
  totalSupply: number;
  /** Recipient count */
  recipientCount: number;
  /** Trigger type */
  triggerType: 'hourly' | 'manual';
  /** Execution timestamp */
  executedAt: Date;
  /** Relative time */
  timeAgo: string;
}

// Legacy type alias for backwards compatibility
export type FormattedDistribution = FormattedPayout;

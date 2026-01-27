/**
 * Utility Functions
 */

import { TIER_CONFIG, type TierId } from '@/types/models';

// ===========================================
// Number Formatting
// ===========================================

/**
 * Format a number in compact notation (e.g., 1.2K, 3.4M)
 */
export function formatCompactNumber(value: number): string {
  if (value === 0) return '0';

  const formatter = new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1,
  });

  return formatter.format(value);
}

/**
 * Format a number as USD currency
 * @param compact - Use compact notation for large numbers (e.g., $1.2K)
 */
export function formatUSD(value: number, compact = false): string {
  if (compact) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      compactDisplay: 'short',
      maximumFractionDigits: 1,
    }).format(value);
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format a multiplier value (e.g., 1.5x)
 */
export function formatMultiplier(value: number): string {
  return `${value.toFixed(1)}x`;
}

/**
 * Format a number with commas
 */
export function formatNumber(value: number, decimals = 0): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

// ===========================================
// Time Formatting
// ===========================================

/**
 * Format duration in hours to human-readable string
 */
export function formatDuration(hours: number): string {
  if (hours < 1) {
    const minutes = Math.round(hours * 60);
    return `${minutes}m`;
  }
  if (hours < 24) {
    return `${Math.round(hours)}h`;
  }
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  if (remainingHours === 0) {
    return `${days}d`;
  }
  return `${days}d ${remainingHours}h`;
}

/**
 * Format a date as a readable date/time string (e.g., "Jan 15, 2:30 PM")
 */
export function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Format a date as relative time (e.g., "2 hours ago")
 */
export function formatTimeAgo(date: Date | string): string {
  const now = new Date();
  const then = typeof date === 'string' ? new Date(date) : date;
  const diffMs = now.getTime() - then.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) {
    return 'just now';
  }
  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  }
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }
  if (diffDays < 7) {
    return `${diffDays}d ago`;
  }
  return then.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// ===========================================
// Address Formatting
// ===========================================

/**
 * Shorten a Solana wallet address (e.g., "ABC1...XYZ9")
 */
export function shortenAddress(address: string, chars = 4): string {
  if (!address) return '';
  if (address.length <= chars * 2 + 3) return address;
  return `${address.slice(0, chars)}...${address.slice(-chars)}`;
}

// ===========================================
// Tier Utilities
// ===========================================

/**
 * Calculate progress percentage to next tier
 */
export function calculateTierProgress(
  currentTier: number,
  streakHours: number
): number {
  const currentTierId = currentTier as TierId;
  const nextTierId = (currentTier + 1) as TierId;

  // If at max tier, return 100%
  if (currentTier >= 6) return 100;

  const currentConfig = TIER_CONFIG[currentTierId];
  const nextConfig = TIER_CONFIG[nextTierId];

  if (!currentConfig || !nextConfig) return 0;

  const hoursInCurrentTier = streakHours - currentConfig.minHours;
  const hoursNeeded = nextConfig.minHours - currentConfig.minHours;

  if (hoursNeeded <= 0) return 100;

  return Math.min(100, Math.max(0, (hoursInCurrentTier / hoursNeeded) * 100));
}

/**
 * Get tier info by tier ID
 */
export function getTierInfo(tierId: TierId) {
  return TIER_CONFIG[tierId];
}

// ===========================================
// Token Formatting
// ===========================================

/**
 * Format a CPU token amount (what users hold)
 */
export function formatCPU(value: number, decimals = 2): string {
  if (value === 0) return '0';
  if (value < 0.01) return '<0.01';
  return formatNumber(value, decimals);
}

/**
 * Format a $GOLD token amount (rewards)
 * Handles tiny amounts common in early distributions
 */
export function formatGOLD(value: number, decimals = 2): string {
  if (value === 0) return '0';
  // For very tiny amounts, show with enough decimals to see the value
  if (value < 0.01) {
    // Find first significant digit and show 2 more
    const exp = Math.floor(Math.log10(Math.abs(value)));
    const sigFigs = Math.max(2, -exp + 1);
    return value.toFixed(Math.min(sigFigs, 9));
  }
  return formatNumber(value, decimals);
}

/**
 * Format a percentage value
 */
export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

// ===========================================
// Earning Rate Utilities
// ===========================================

/**
 * Calculate earning rate per hour from pending reward and elapsed hours.
 * Returns null if hours is not available or zero.
 */
export function calculateEarningRate(
  pendingReward: number,
  hoursSinceLast: number | null
): number | null {
  if (!hoursSinceLast || hoursSinceLast <= 0) {
    return null;
  }
  return pendingReward / hoursSinceLast;
}

/**
 * Format earning rate as USD per hour
 */
export function formatEarningRate(ratePerHour: number): string {
  if (ratePerHour === 0) return '$0/hr';
  if (ratePerHour < 0.01) return '<$0.01/hr';
  return `$${ratePerHour.toFixed(2)}/hr`;
}

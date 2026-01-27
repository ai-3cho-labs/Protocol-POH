'use client';

import { formatUSD, formatGOLD } from '@/lib/utils';
import type { PoolInfo } from '@/types/models';
import { PAYOUT_THRESHOLD_USD } from '@/types/models';
import {
  TerminalCard,
  ProgressBar,
  AsciiProgressBar,
  Skeleton,
} from '@/components/ui';

export interface TotalMinedProps {
  /** Lifetime earnings from all distributions (GOLD tokens) */
  lifetimeEarnings: number | undefined;
  /** Total number of distributions received */
  distributionCount?: number;
  /** Pool information for countdown */
  pool?: PoolInfo | null;
  /** Is data loading */
  isLoading?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * TotalMined - Shows lifetime mining earnings and pool status
 */
export function PendingRewards({
  lifetimeEarnings,
  distributionCount = 0,
  pool,
  isLoading = false,
  className,
}: TotalMinedProps) {
  if (isLoading) {
    return <TotalMinedSkeleton className={className} />;
  }

  const hasEarnings = lifetimeEarnings !== undefined && lifetimeEarnings > 0;

  return (
    <div className={className}>
      {/* Total Mined Section */}
      <TerminalCard title="TOTAL MINED" className="mb-4">
        <div className="space-y-4">
          {/* Lifetime Earnings Amount */}
          <div className="text-center py-4">
            <div className="text-xs text-zinc-500 mb-1 lg:font-mono lg:text-gray-500">
              LIFETIME EARNINGS
            </div>
            <div className="text-3xl sm:text-4xl lg:text-4xl font-bold text-white glow-white lg:font-mono tabular-nums">
              {hasEarnings ? formatGOLD(lifetimeEarnings!) : '0.00'}
            </div>
            <div className="text-sm text-zinc-500 mt-1">$GOLD</div>
          </div>

          {/* Distribution Stats */}
          <div className="space-y-3 border-t border-zinc-800 lg:border-terminal-border pt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-500 lg:font-mono lg:text-gray-500">
                Distributions Received
              </span>
              <span className="font-medium text-zinc-100 lg:font-mono">
                {distributionCount}
              </span>
            </div>

            {hasEarnings && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-500 lg:font-mono lg:text-gray-500">
                  Avg per Distribution
                </span>
                <span className="font-medium text-zinc-100 lg:font-mono">
                  {formatGOLD(lifetimeEarnings! / Math.max(distributionCount, 1))} GOLD
                </span>
              </div>
            )}
          </div>

          {/* No Earnings State */}
          {!hasEarnings && (
            <div className="text-center py-2 px-4 rounded bg-zinc-800/50 border border-zinc-700">
              <span className="text-sm text-zinc-400 lg:font-mono">
                No distributions received yet
              </span>
            </div>
          )}
        </div>
      </TerminalCard>

      {/* Reward Pool Section */}
      {pool && (
        <TerminalCard title="REWARD POOL">
          <div className="space-y-4">
            {/* Pool Value */}
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-500 lg:font-mono lg:text-gray-500">
                Pool Value
              </span>
              <span className="font-medium text-zinc-100 lg:font-mono">
                {formatUSD(pool.valueUsd)} / {formatUSD(PAYOUT_THRESHOLD_USD)}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="hidden lg:block">
              <AsciiProgressBar value={pool.progressToThreshold} />
            </div>
            <div className="lg:hidden">
              <ProgressBar
                value={pool.progressToThreshold}
                variant="default"
                size="md"
              />
            </div>

            {/* Pool Balance */}
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-500 lg:font-mono lg:text-gray-500">
                Pool Balance
              </span>
              <span className="font-medium text-zinc-100 lg:font-mono">
                {formatGOLD(pool.balance)} GOLD
              </span>
            </div>

            {/* Ready State */}
            {pool.thresholdMet && (
              <div className="text-center py-2 px-4 rounded bg-white/10 border border-white/30">
                <span className="text-sm text-white glow-white lg:font-mono">
                  Payout threshold reached!
                </span>
              </div>
            )}
          </div>
        </TerminalCard>
      )}
    </div>
  );
}

/**
 * Countdown display component
 */
/**
 * Loading skeleton
 */
function TotalMinedSkeleton({
  className,
}: {
  className?: string;
}) {
  return (
    <div className={className}>
      <TerminalCard title="TOTAL MINED" className="mb-4">
        <div className="space-y-4">
          <div className="text-center py-2">
            <Skeleton className="h-3 w-32 mx-auto mb-2" />
            <Skeleton className="h-10 w-28 mx-auto" />
            <Skeleton className="h-4 w-16 mx-auto mt-1" />
          </div>
          <div className="space-y-3 pt-2">
            <div className="flex justify-between">
              <Skeleton className="h-4 w-36" />
              <Skeleton className="h-4 w-8" />
            </div>
          </div>
        </div>
      </TerminalCard>
      <TerminalCard title="REWARD POOL">
        <div className="space-y-4">
          <div className="flex justify-between">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-24" />
          </div>
          <Skeleton className="h-2.5 w-full rounded-full" />
          <div className="flex justify-between pt-2">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      </TerminalCard>
    </div>
  );
}

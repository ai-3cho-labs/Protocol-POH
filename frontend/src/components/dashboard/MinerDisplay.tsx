'use client';

import { useWalletAddress } from '@/hooks/useWallet';
import { useUserStats, usePoolStatus } from '@/hooks/api';
import { formatCompactNumber, formatMultiplier } from '@/lib/utils';
import { cn } from '@/lib/cn';
import { PixelMiner } from './PixelMiner';
import { MineTilemap } from './MineTilemap';
import { Skeleton } from '@/components/ui/Skeleton';

interface MinerDisplayProps {
  onViewDetails: () => void;
  className?: string;
}

interface StatBadgeProps {
  label: string;
  value: string;
  subtext?: string;
  glow?: boolean;
  className?: string;
}

function StatBadge({ label, value, subtext, glow, className }: StatBadgeProps) {
  return (
    <div className={cn('text-center', className)}>
      <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">
        {label}
      </div>
      <div
        className={cn(
          'text-xl lg:text-2xl font-bold font-mono',
          glow ? 'text-white glow-white' : 'text-gray-200'
        )}
      >
        {value}
      </div>
      {subtext && (
        <div className="text-xs text-gray-500 mt-0.5">{subtext}</div>
      )}
    </div>
  );
}

function StatBadgeSkeleton() {
  return (
    <div className="text-center">
      <Skeleton className="h-3 w-16 mx-auto mb-2" />
      <Skeleton className="h-7 w-20 mx-auto" />
    </div>
  );
}

/**
 * Main dashboard centerpiece with animated pixel miner and 4 core stats.
 * Stats: Balance, Hash Power, Tier, Pending Reward
 */
export function MinerDisplay({ onViewDetails, className }: MinerDisplayProps) {
  const wallet = useWalletAddress();
  const { data: stats, isLoading: statsLoading } = useUserStats(wallet);
  const { data: pool, isLoading: poolLoading } = usePoolStatus();

  const isLoading = statsLoading || poolLoading;

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center min-h-[60vh] px-4',
        className
      )}
    >
      {/* Desktop Layout */}
      <div className="hidden lg:flex flex-col items-center gap-8">
        {/* Tier badge on top */}
        {isLoading ? (
          <StatBadgeSkeleton />
        ) : (
          <StatBadge
            label="Tier"
            value={stats?.tier.emoji ?? '🪨'}
            subtext={stats?.tier.name}
          />
        )}

        {/* Tilemap with side stats */}
        <div className="relative">
          <div className="absolute -left-32 top-1/2 -translate-y-1/2">
            {isLoading ? (
              <StatBadgeSkeleton />
            ) : (
              <StatBadge
                label="Balance"
                value={formatCompactNumber(stats?.balance ?? 0)}
                subtext="$CPU"
              />
            )}
          </div>

          <div className="absolute -right-32 top-1/2 -translate-y-1/2">
            {isLoading ? (
              <StatBadgeSkeleton />
            ) : (
              <StatBadge
                label="Hash Power"
                value={formatCompactNumber(stats?.hashPower ?? 0)}
                glow
              />
            )}
          </div>

          {/* Mine Tilemap with Miner */}
          <MineTilemap scale={4} minerPosition={{ x: 0, y: 2 }}>
            <PixelMiner scale={4} animation="drilling" frameTime={150} />
          </MineTilemap>
        </div>

        {/* Pending reward below */}
        {isLoading ? (
          <StatBadgeSkeleton />
        ) : (
          <StatBadge
            label="Pending Reward"
            value={`+${formatCompactNumber(stats?.pendingReward ?? 0)}`}
            subtext="$CPU"
            glow
          />
        )}
      </div>

      {/* Mobile Layout */}
      <div className="lg:hidden flex flex-col items-center gap-6 w-full max-w-xs">
        {/* Tier badge on top */}
        {isLoading ? (
          <StatBadgeSkeleton />
        ) : (
          <StatBadge
            label="Tier"
            value={stats?.tier.emoji ?? '🪨'}
            subtext={`${stats?.tier.name} (${formatMultiplier(stats?.multiplier ?? 1)})`}
          />
        )}

        {/* Mine Tilemap with Miner */}
        <MineTilemap scale={2.5} minerPosition={{ x: 0, y: 2 }}>
          <PixelMiner scale={2.5} animation="drilling" frameTime={150} />
        </MineTilemap>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-6 w-full">
          {isLoading ? (
            <>
              <StatBadgeSkeleton />
              <StatBadgeSkeleton />
              <StatBadgeSkeleton />
              <StatBadgeSkeleton />
            </>
          ) : (
            <>
              <StatBadge
                label="Balance"
                value={formatCompactNumber(stats?.balance ?? 0)}
                subtext="$CPU"
              />
              <StatBadge
                label="Hash Power"
                value={formatCompactNumber(stats?.hashPower ?? 0)}
                glow
              />
              <StatBadge
                label="Rank"
                value={stats?.rank ? `#${stats.rank}` : '-'}
              />
              <StatBadge
                label="Pending"
                value={`+${formatCompactNumber(stats?.pendingReward ?? 0)}`}
                glow
              />
            </>
          )}
        </div>
      </div>

      {/* View Details Button */}
      <button
        onClick={onViewDetails}
        className={cn(
          'mt-8 px-6 py-3 rounded-lg font-mono text-sm',
          'bg-white/10 hover:bg-white/20 text-white',
          'border border-white/20 hover:border-white/40',
          'transition-all duration-200',
          'lg:mt-24'
        )}
      >
        View Details
      </button>

      {/* Pool status hint */}
      {!isLoading && pool && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          Pool: {pool.progressToThreshold.toFixed(0)}% to payout
          {pool.thresholdMet && (
            <span className="ml-2 text-white animate-pulse">READY</span>
          )}
        </div>
      )}
    </div>
  );
}

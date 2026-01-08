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
    <div className={cn('text-center min-w-[100px]', className)}>
      <div className="text-[10px] text-gray-400 uppercase tracking-widest font-medium mb-2">
        {label}
      </div>
      <div
        className={cn(
          'text-2xl lg:text-3xl font-bold font-mono leading-none',
          glow
            ? 'text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.5)]'
            : 'text-white'
        )}
      >
        {value}
      </div>
      {subtext && (
        <div className={cn(
          'text-xs mt-1.5 font-medium',
          glow ? 'text-amber-400/70' : 'text-gray-500'
        )}>
          {subtext}
        </div>
      )}
    </div>
  );
}

function StatBadgeSkeleton() {
  return (
    <div className="text-center min-w-[100px]">
      <Skeleton className="h-2.5 w-14 mx-auto mb-3" />
      <Skeleton className="h-8 w-16 mx-auto" />
      <Skeleton className="h-3 w-10 mx-auto mt-2" />
    </div>
  );
}

const cardBaseStyles = cn(
  'relative overflow-hidden rounded-xl px-6 py-5',
  'bg-gradient-to-b from-white/[0.08] to-white/[0.02]',
  'border border-white/10',
  'backdrop-blur-sm',
  'transition-all duration-300',
  'hover:border-white/20 hover:from-white/[0.12] hover:to-white/[0.04]',
  'hover:scale-[1.02] hover:shadow-lg hover:shadow-black/20'
);

const glowCardStyles = cn(
  'relative overflow-hidden rounded-xl px-6 py-5',
  'bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02]',
  'border border-amber-500/20',
  'backdrop-blur-sm',
  'transition-all duration-300',
  'hover:border-amber-500/40 hover:from-amber-500/15 hover:to-amber-500/[0.05]',
  'hover:scale-[1.02] hover:shadow-lg hover:shadow-amber-500/10'
);

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
      <div className="hidden lg:flex flex-col items-center gap-6">
        {/* Mine Tilemap with Miner */}
        <MineTilemap scale={4} minerPosition={{ x: 0.5, y: 1.8 }}>
          <PixelMiner scale={4} animation="drilling" frameTime={150} />
        </MineTilemap>

        {/* Stats Cards */}
        <div className="flex items-stretch gap-3">
          {isLoading ? (
            <>
              <div className={cardBaseStyles}>
                <StatBadgeSkeleton />
              </div>
              <div className={cardBaseStyles}>
                <StatBadgeSkeleton />
              </div>
              <div className={glowCardStyles}>
                <StatBadgeSkeleton />
              </div>
              <div className={glowCardStyles}>
                <StatBadgeSkeleton />
              </div>
            </>
          ) : (
            <>
              <div className={cardBaseStyles}>
                <StatBadge
                  label="Tier"
                  value={stats?.tier.emoji ?? '🪨'}
                  subtext={stats?.tier.name}
                />
              </div>
              <div className={cardBaseStyles}>
                <StatBadge
                  label="Balance"
                  value={formatCompactNumber(stats?.balance ?? 0)}
                  subtext="$CPU"
                />
              </div>
              <div className={glowCardStyles}>
                <StatBadge
                  label="Hash Power"
                  value={formatCompactNumber(stats?.hashPower ?? 0)}
                  subtext="H/s"
                  glow
                />
              </div>
              <div className={glowCardStyles}>
                <StatBadge
                  label="Pending"
                  value={`+${formatCompactNumber(stats?.pendingReward ?? 0)}`}
                  subtext="$CPU"
                  glow
                />
              </div>
            </>
          )}
        </div>
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
        <MineTilemap scale={2.5} minerPosition={{ x: 2, y: 2 }}>
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
          'mt-6 px-6 py-3 rounded-lg font-mono text-sm',
          'bg-white/10 hover:bg-white/20 text-white',
          'border border-white/20 hover:border-white/40',
          'transition-all duration-200'
        )}
      >
        View Details
      </button>

      {/* Pool status hint */}
      {!isLoading && pool && (
        <div className="mt-3 text-xs text-gray-500 text-center">
          Pool: {pool.progressToThreshold.toFixed(0)}% to payout
          {pool.thresholdMet && (
            <span className="ml-2 text-white animate-pulse">READY</span>
          )}
        </div>
      )}
    </div>
  );
}

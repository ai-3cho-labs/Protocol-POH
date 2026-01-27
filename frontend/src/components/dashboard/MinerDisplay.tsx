'use client';

import { useMemo } from 'react';
import { useWalletAddress } from '@/hooks/useWallet';
import { useUserStats, usePoolStatus, useGlobalStats, useUserHistory } from '@/hooks/api';
import { useTickingCounter } from '@/hooks/useCountdown';
import {
  formatCompactNumber,
  formatGOLD,
  formatMultiplier,
  calculateEarningRate,
  formatEarningRate,
  formatDuration,
  formatUSD,
} from '@/lib/utils';
import { cn } from '@/lib/cn';
import { PixelMiner } from './PixelMiner';
import { MineTilemap } from './MineTilemap';
import { ShareCard } from './ShareCard';
import { Skeleton } from '@/components/ui/Skeleton';
import { TIER_CONFIG, type TierId, PAYOUT_THRESHOLD_USD } from '@/types/models';

interface MinerDisplayProps {
  onViewDetails: () => void;
  className?: string;
}

/**
 * Main dashboard with improved visual hierarchy.
 * Desktop: 3-column layout with miner in center, stats on sides
 * Mobile: Stacked layout with clear groupings
 */
export function MinerDisplay({ onViewDetails, className }: MinerDisplayProps) {
  const wallet = useWalletAddress();
  const { data: stats, isLoading: statsLoading } = useUserStats(wallet);
  const { data: pool, isLoading: poolLoading } = usePoolStatus();
  const { data: globalStats } = useGlobalStats();
  const { data: history } = useUserHistory(wallet, 50); // Backend max is 50

  const isLoading = statsLoading || poolLoading;
  const earningRate = calculateEarningRate(stats?.pendingReward ?? 0, pool?.hoursSinceLast ?? null);
  const tickingReward = useTickingCounter(stats?.pendingReward ?? 0, earningRate);

  // Calculate lifetime earnings from history
  const lifetimeEarnings = useMemo(() => {
    if (!history || history.length === 0) return undefined;
    return history.reduce((sum, item) => sum + item.amount_received, 0);
  }, [history]);

  // Calculate USD values for share card
  const pendingRewardUsd = useMemo(() => {
    const poolSharePercent = stats?.poolSharePercent ?? 0;
    return (poolSharePercent / 100) * (pool?.valueUsd ?? 0);
  }, [stats?.poolSharePercent, pool?.valueUsd]);

  const lifetimeEarningsUsd = useMemo(() => {
    if (!lifetimeEarnings || !pool?.balance || pool.balance <= 0) return 0;
    return (lifetimeEarnings / pool.balance) * pool.valueUsd;
  }, [lifetimeEarnings, pool?.balance, pool?.valueUsd]);

  return (
    <div className={cn('px-4 py-6 lg:py-8', className)}>
      {/* Desktop Layout - 3 Column */}
      <div className="hidden lg:grid lg:grid-cols-[1fr_auto_1fr] lg:gap-8 lg:max-w-6xl lg:mx-auto lg:items-start">
        {/* Left Panel - Your Stats */}
        <div className="space-y-4">
          <LeftPanel stats={stats} isLoading={isLoading} />
        </div>

        {/* Center - Miner + View Details + Share */}
        <div className="flex flex-col items-center">
          <MineTilemap scale={4} minerPosition={{ x: 0.5, y: 1.8 }}>
            <PixelMiner scale={4} animation="mining" frameTime={150} />
          </MineTilemap>
          <div className="flex gap-3 mt-6">
            <button
              onClick={onViewDetails}
              className={cn(
                'px-8 py-3 rounded-xl text-sm font-medium',
                'bg-white/10 text-white border border-white/20',
                'transition-all duration-200',
                'hover:bg-white/20 hover:border-white/40'
              )}
            >
              View Details
            </button>
            <ShareCard
              stats={stats}
              totalHolders={globalStats?.total_holders}
              lifetimeEarnings={lifetimeEarnings}
              lifetimeEarningsUsd={lifetimeEarningsUsd}
              pendingRewardUsd={pendingRewardUsd}
            />
          </div>
        </div>

        {/* Right Panel - Rewards + Pool */}
        <div className="space-y-4">
          <RightPanel
            tickingReward={tickingReward}
            earningRate={earningRate}
            pool={pool}
            stats={stats}
            lifetimeEarnings={lifetimeEarnings}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Mobile Layout - Stacked */}
      <div className="lg:hidden flex flex-col items-center gap-6 max-w-md mx-auto">
        {/* Welcome Banner for New Holders (Mobile) */}
        {stats?.isNewHolder && !isLoading && (
          <div className="w-full p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center text-xl">
                ⛏️
              </div>
              <div>
                <div className="text-sm font-medium text-amber-400">Welcome, Miner!</div>
                <div className="text-xs text-gray-400">
                  Your rewards are being calculated
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Earned Rewards - Hero Section */}
        <RewardsHeroMobile
          tickingReward={tickingReward}
          earningRate={earningRate}
          stats={stats}
          pool={pool}
          lifetimeEarnings={lifetimeEarnings}
          isLoading={isLoading}
        />

        {/* Miner */}
        <MineTilemap scale={2.5} minerPosition={{ x: 0.5, y: 1.8 }}>
          <PixelMiner scale={2.5} animation="mining" frameTime={150} />
        </MineTilemap>

        {/* Stats Grid */}
        <div className="w-full space-y-3">
          {/* Tier Card - Full Width */}
          <TierCardMobile stats={stats} isLoading={isLoading} />

          {/* Balance + Hash Power */}
          <div className="grid grid-cols-2 gap-3">
            <StatCardMobile
              label="Balance"
              value={formatCompactNumber(stats?.balance ?? 0)}
              subtext="CPU"
              isLoading={isLoading}
            />
            <StatCardMobile
              label="Hash Power"
              value={formatCompactNumber(stats?.hashPower ?? 0)}
              subtext={stats ? `${formatMultiplier(stats.multiplier)} bonus` : 'H/s'}
              glow
              badge={stats?.isProjected ? 'Projected' : undefined}
              isLoading={isLoading}
            />
          </div>

          {/* Rank + Pool Progress */}
          <div className="grid grid-cols-2 gap-3">
            <StatCardMobile
              label="Rank"
              value={stats?.rank ? `#${stats.rank}` : '-'}
              subtext="Leaderboard"
              isLoading={isLoading}
            />
            <PoolCardMobile pool={pool} isLoading={isLoading} />
          </div>
        </div>

        {/* View Details + Share */}
        <div className="w-full flex gap-3">
          <button
            onClick={onViewDetails}
            className={cn(
              'flex-1 px-8 py-4 rounded-xl text-sm font-medium',
              'bg-white/10 text-white border border-white/20',
              'transition-all duration-200',
              'active:scale-[0.98] active:bg-white/20'
            )}
          >
            View Details
          </button>
          <ShareCard
            stats={stats}
            totalHolders={globalStats?.total_holders}
            lifetimeEarnings={lifetimeEarnings}
            lifetimeEarningsUsd={lifetimeEarningsUsd}
            pendingRewardUsd={pendingRewardUsd}
            className="px-6 py-4 active:scale-[0.98]"
          />
        </div>
      </div>
    </div>
  );
}

// ===========================================
// Shared Components
// ===========================================

function TierBadge({ tier, size = 'md' }: { tier: TierId; size?: 'sm' | 'md' | 'lg' }) {
  const config = TIER_CONFIG[tier];
  const sizeClasses = {
    sm: 'w-6 h-6 text-[10px]',
    md: 'w-8 h-8 text-xs',
    lg: 'w-10 h-10 text-sm',
  };

  return (
    <div
      className={cn(
        'rounded-full flex items-center justify-center font-bold',
        sizeClasses[size],
        config.bgColor,
        config.color
      )}
    >
      {config.label}
    </div>
  );
}

// ===========================================
// Desktop Components
// ===========================================

function LeftPanel({
  stats,
  isLoading,
}: {
  stats: ReturnType<typeof useUserStats>['data'];
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <>
        <PanelCard>
          <Skeleton className="h-4 w-20 mb-4" />
          <Skeleton className="h-10 w-32 mb-2" />
          <Skeleton className="h-3 w-24" />
        </PanelCard>
        <PanelCard>
          <Skeleton className="h-4 w-24 mb-4" />
          <div className="flex gap-2 mb-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="w-8 h-8 rounded-full" />
            ))}
          </div>
          <Skeleton className="h-2 w-full rounded-full" />
        </PanelCard>
      </>
    );
  }

  const tierProgress = stats?.progressToNextTier ?? 0;
  const currentTierId = (stats?.tier.tier ?? 1) as TierId;

  return (
    <>
      {/* Welcome Banner for New Holders */}
      {stats?.isNewHolder && (
        <PanelCard className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center text-xl">
              ⛏️
            </div>
            <div>
              <div className="text-sm font-medium text-amber-400">Welcome, Miner!</div>
              <div className="text-xs text-gray-400">
                Your rewards are being calculated
              </div>
            </div>
          </div>
        </PanelCard>
      )}

      {/* Balance Card */}
      <PanelCard>
        <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">
          Your Balance
        </div>
        <div className="text-4xl font-bold text-white font-mono tabular-nums">
          {formatCompactNumber(stats?.balance ?? 0)}
        </div>
        <div className="text-sm text-gray-500 mt-1">CPU Tokens</div>
      </PanelCard>

      {/* Tier Progress Card */}
      <PanelCard>
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs text-gray-400 uppercase tracking-wider">
            Tier Progress
          </div>
          {stats?.rank && (
            <div className="text-xs text-amber-400 font-medium">
              Rank #{stats.rank}
            </div>
          )}
        </div>

        {/* Tier Timeline */}
        <div className="flex items-center justify-between mb-4">
          {Object.entries(TIER_CONFIG).map(([id, config]) => {
            const tierId = parseInt(id) as TierId;
            const isActive = tierId === currentTierId;
            const isPast = tierId < currentTierId;

            return (
              <div
                key={id}
                className={cn(
                  'flex flex-col items-center gap-1 transition-all',
                  isActive && 'scale-110'
                )}
                title={`${config.name} (${formatMultiplier(config.multiplier)})`}
              >
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold',
                    isActive && 'ring-2 ring-white',
                    isActive || isPast ? config.bgColor : 'bg-white/5',
                    isActive || isPast ? config.color : 'text-white/40'
                  )}
                >
                  {config.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Current Tier Info */}
        <div className="flex items-center justify-between text-sm mb-2">
          <div className="flex items-center gap-2">
            <TierBadge tier={(stats?.tier.tier ?? 1) as TierId} />
            <span className="text-white font-medium">{stats?.tier.name}</span>
          </div>
          <span className="text-amber-400 font-mono">
            {formatMultiplier(stats?.multiplier ?? 1)}
          </span>
        </div>

        {/* Progress Bar */}
        {stats?.nextTier && (
          <>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-500"
                style={{ width: `${tierProgress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1.5">
              <span>{formatDuration(stats.streakHours)} held</span>
              <span>
                {stats.hoursToNextTier !== null
                  ? `${formatDuration(stats.hoursToNextTier)} to ${stats.nextTier.name}`
                  : 'Max tier!'}
              </span>
            </div>
          </>
        )}
        {!stats?.nextTier && (
          <div className="text-center py-2 px-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <span className="text-sm text-amber-400">Max Tier Achieved!</span>
          </div>
        )}
      </PanelCard>

      {/* Hash Power Card */}
      <PanelCard glow>
        <div className="flex items-center justify-between mb-1">
          <div className="text-xs text-amber-400/70 uppercase tracking-wider">
            Hash Power
          </div>
          {stats?.isProjected && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
              Projected
            </span>
          )}
        </div>
        <div className="text-3xl font-bold text-amber-400 font-mono tabular-nums drop-shadow-[0_0_12px_rgba(251,191,36,0.4)]">
          {formatCompactNumber(stats?.hashPower ?? 0)}
        </div>
        <div className="text-sm text-amber-400/60 mt-1">H/s</div>
        <div className="text-xs text-gray-500 mt-2">
          TWAB ({formatCompactNumber(stats?.twab ?? 0)}) × {formatMultiplier(stats?.multiplier ?? 1)}
        </div>
        {stats?.isProjected && (
          <div className="text-[10px] text-gray-500 mt-1">
            Based on current balance
          </div>
        )}
      </PanelCard>
    </>
  );
}

function RightPanel({
  tickingReward,
  earningRate,
  pool,
  stats,
  lifetimeEarnings,
  isLoading,
}: {
  tickingReward: number;
  earningRate: number | null;
  pool: ReturnType<typeof usePoolStatus>['data'];
  stats: ReturnType<typeof useUserStats>['data'];
  lifetimeEarnings: number | undefined;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <>
        <PanelCard glow className="py-8">
          <Skeleton className="h-4 w-32 mx-auto mb-4" />
          <Skeleton className="h-12 w-40 mx-auto mb-2" />
          <Skeleton className="h-4 w-20 mx-auto" />
        </PanelCard>
        <PanelCard>
          <Skeleton className="h-4 w-24 mb-4" />
          <Skeleton className="h-3 w-full mb-2" />
          <Skeleton className="h-2 w-full rounded-full" />
        </PanelCard>
      </>
    );
  }

  const poolSharePercent = stats?.poolSharePercent ?? 0;

  return (
    <>
      {/* Rewards - Hero */}
      <PanelCard glow className="py-6">
        <div className="flex justify-between items-start">
          {/* Pending Rewards */}
          <div className="text-center flex-1">
            <div className="text-xs text-amber-400/70 uppercase tracking-wider mb-2">
              Pending Rewards
            </div>
            <div className="text-4xl font-bold text-amber-400 font-mono tabular-nums drop-shadow-[0_0_20px_rgba(251,191,36,0.5)]">
              +{formatGOLD(tickingReward)}
            </div>
            <div className="text-sm text-amber-400/80 mt-1">$GOLD</div>
            <div className="text-lg text-white mt-1 font-mono">
              {formatUSD((poolSharePercent / 100) * (pool?.valueUsd ?? 0))}
            </div>
          </div>

          {/* Divider */}
          <div className="w-px h-24 bg-white/10 mx-4 self-center" />

          {/* Total Mined */}
          <div className="text-center flex-1">
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">
              Total Mined
            </div>
            <div className="text-4xl font-bold text-white font-mono tabular-nums">
              {lifetimeEarnings !== undefined && lifetimeEarnings > 0
                ? formatGOLD(lifetimeEarnings)
                : '0.00'}
            </div>
            <div className="text-sm text-gray-400 mt-1">$GOLD</div>
            <div className="text-lg text-gray-500 mt-1 font-mono">
              {lifetimeEarnings !== undefined && lifetimeEarnings > 0 && pool?.balance && pool.balance > 0
                ? formatUSD((lifetimeEarnings / pool.balance) * pool.valueUsd)
                : formatUSD(0)}
            </div>
          </div>
        </div>

        {/* Pool Share & Earning Rate */}
        <div className="mt-4 flex items-center justify-center gap-3">
          {poolSharePercent > 0 && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <span className="text-xs text-gray-400">Your share:</span>
              <span className="text-sm text-white font-mono font-medium">
                {poolSharePercent < 0.01 ? '<0.01' : poolSharePercent.toFixed(2)}%
              </span>
            </div>
          )}
          {earningRate !== null && (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              <span className="text-sm text-amber-400 font-mono">
                {formatEarningRate(earningRate)}
              </span>
            </div>
          )}
        </div>

        {/* Projected indicator for new holders */}
        {stats?.isProjected && (
          <div className="mt-2 text-xs text-gray-500 text-center">
            Projected based on current balance
          </div>
        )}
      </PanelCard>

      {/* Pool Status */}
      <PanelCard>
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs text-gray-400 uppercase tracking-wider">
            Reward Pool
          </div>
          {(pool?.thresholdMet || pool?.timeTriggerMet) && (
            <span className="text-xs font-medium text-amber-400 animate-pulse">
              READY
            </span>
          )}
        </div>

        {/* Pool Value */}
        <div className="flex items-baseline justify-between mb-3">
          <span className="text-2xl font-bold text-white font-mono">
            {formatUSD(pool?.valueUsd ?? 0)}
          </span>
          <span className="text-sm text-gray-500">
            / {formatUSD(PAYOUT_THRESHOLD_USD)}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="h-3 bg-white/10 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-500 rounded-full',
              pool?.thresholdMet
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 animate-pulse'
                : 'bg-gradient-to-r from-white/40 to-white/60'
            )}
            style={{ width: `${pool?.progressToThreshold ?? 0}%` }}
          />
        </div>
        <div className="text-xs text-gray-500 mt-2">
          <span>{pool?.progressToThreshold.toFixed(0)}% filled</span>
        </div>
      </PanelCard>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3">
        <PanelCard small>
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">
            Pool Balance
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {formatGOLD(pool?.balance ?? 0)}
          </div>
          <div className="text-xs text-gray-500">GOLD</div>
        </PanelCard>
        <PanelCard small>
          <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">
            Time Since Last
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {pool && pool.hoursSinceLast !== null
              ? formatDuration(pool.hoursSinceLast)
              : '-'}
          </div>
          <div className="text-xs text-gray-500">elapsed</div>
        </PanelCard>
      </div>
    </>
  );
}

function PanelCard({
  children,
  glow,
  small,
  className,
}: {
  children: React.ReactNode;
  glow?: boolean;
  small?: boolean;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'rounded-xl backdrop-blur-sm',
        small ? 'p-4' : 'p-5',
        glow
          ? 'bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02] border border-amber-500/20'
          : 'bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10',
        className
      )}
    >
      {children}
    </div>
  );
}

// ===========================================
// Mobile Components
// ===========================================

function RewardsHeroMobile({
  tickingReward,
  earningRate,
  stats,
  pool,
  lifetimeEarnings,
  isLoading,
}: {
  tickingReward: number;
  earningRate: number | null;
  stats: ReturnType<typeof useUserStats>['data'];
  pool: ReturnType<typeof usePoolStatus>['data'];
  lifetimeEarnings: number | undefined;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="w-full p-6 rounded-2xl bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02] border border-amber-500/20">
        <div className="flex justify-between">
          <Skeleton className="h-16 w-28" />
          <Skeleton className="h-16 w-28" />
        </div>
        <Skeleton className="h-5 w-32 mx-auto mt-3" />
      </div>
    );
  }

  const poolSharePercent = stats?.poolSharePercent ?? 0;
  const earnedUsd = (poolSharePercent / 100) * (pool?.valueUsd ?? 0);

  return (
    <div className="w-full p-5 rounded-2xl bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02] border border-amber-500/20">
      <div className="flex justify-between items-start">
        {/* Pending Rewards */}
        <div className="text-center flex-1">
          <div className="text-[10px] text-amber-400/70 uppercase tracking-wider mb-1">
            Pending Rewards
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono tabular-nums drop-shadow-[0_0_16px_rgba(251,191,36,0.5)]">
            +{formatGOLD(tickingReward)}
          </div>
          <div className="text-xs text-amber-400/80">$GOLD</div>
          <div className="text-sm text-white font-mono">
            {formatUSD(earnedUsd)}
          </div>
        </div>

        {/* Divider */}
        <div className="w-px h-16 bg-white/10 mx-3 self-center" />

        {/* Total Mined */}
        <div className="text-center flex-1">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">
            Total Mined
          </div>
          <div className="text-2xl font-bold text-white font-mono tabular-nums">
            {lifetimeEarnings !== undefined && lifetimeEarnings > 0
              ? formatGOLD(lifetimeEarnings)
              : '0.00'}
          </div>
          <div className="text-xs text-gray-400">$GOLD</div>
          <div className="text-sm text-gray-500 font-mono">
            {lifetimeEarnings !== undefined && lifetimeEarnings > 0 && pool?.balance && pool.balance > 0
              ? formatUSD((lifetimeEarnings / pool.balance) * pool.valueUsd)
              : formatUSD(0)}
          </div>
        </div>
      </div>

      {/* Pool Share & Earning Rate */}
      <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
        {poolSharePercent > 0 && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/10">
            <span className="text-[10px] text-gray-400">Share:</span>
            <span className="text-xs text-white font-mono font-medium">
              {poolSharePercent < 0.01 ? '<0.01' : poolSharePercent.toFixed(2)}%
            </span>
          </div>
        )}
        {earningRate !== null && (
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-xs text-amber-400 font-mono">
              {formatEarningRate(earningRate)}
            </span>
          </div>
        )}
      </div>

      {/* Projected indicator */}
      {stats?.isProjected && (
        <div className="mt-2 text-[10px] text-gray-500 text-center">
          Projected based on current balance
        </div>
      )}
    </div>
  );
}

function TierCardMobile({
  stats,
  isLoading,
}: {
  stats: ReturnType<typeof useUserStats>['data'];
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="p-4 rounded-2xl bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Skeleton className="w-12 h-12 rounded-full" />
            <div>
              <Skeleton className="h-5 w-24 mb-1" />
              <Skeleton className="h-3 w-16" />
            </div>
          </div>
          <Skeleton className="h-6 w-12" />
        </div>
      </div>
    );
  }

  const tierProgress = stats?.progressToNextTier ?? 0;

  const tierId = (stats?.tier.tier ?? 1) as TierId;
  const tierStyle = TIER_CONFIG[tierId];

  return (
    <div className="p-4 rounded-2xl bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn(
            'w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold',
            tierStyle.bgColor,
            tierStyle.color
          )}>
            {tierStyle.label}
          </div>
          <div>
            <div className="text-white font-medium">{stats?.tier.name ?? 'Ore'}</div>
            <div className="text-xs text-gray-500">
              {formatDuration(stats?.streakHours ?? 0)} streak
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-amber-400 font-mono font-bold">
            {formatMultiplier(stats?.multiplier ?? 1)}
          </div>
          <div className="text-xs text-gray-500">multiplier</div>
        </div>
      </div>

      {stats?.nextTier && (
        <>
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-500"
              style={{ width: `${tierProgress}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 mt-1.5 text-right">
            {stats.hoursToNextTier !== null
              ? `${formatDuration(stats.hoursToNextTier)} to ${stats.nextTier.name}`
              : ''}
          </div>
        </>
      )}
    </div>
  );
}

function StatCardMobile({
  label,
  value,
  subtext,
  glow,
  badge,
  isLoading,
}: {
  label: string;
  value: string;
  subtext: string;
  glow?: boolean;
  badge?: string;
  isLoading?: boolean;
}) {
  if (isLoading) {
    return (
      <div
        className={cn(
          'p-4 rounded-2xl',
          glow
            ? 'bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02] border border-amber-500/20'
            : 'bg-gradient-to-b from-white/[0.06] to-white/[0.02] border border-white/10'
        )}
      >
        <Skeleton className="h-2.5 w-14 mb-2" />
        <Skeleton className="h-6 w-16 mb-1" />
        <Skeleton className="h-3 w-10" />
      </div>
    );
  }

  return (
    <div
      className={cn(
        'p-4 rounded-2xl text-center',
        glow
          ? 'bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02] border border-amber-500/20'
          : 'bg-gradient-to-b from-white/[0.06] to-white/[0.02] border border-white/10'
      )}
    >
      <div className="flex items-center justify-center gap-1.5 mb-1">
        <div className="text-[10px] text-gray-400 uppercase tracking-widest">
          {label}
        </div>
        {badge && (
          <span className="text-[8px] px-1 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
            {badge}
          </span>
        )}
      </div>
      <div
        className={cn(
          'text-xl font-bold font-mono',
          glow ? 'text-amber-400' : 'text-white'
        )}
      >
        {value}
      </div>
      <div className={cn('text-xs mt-0.5', glow ? 'text-amber-400/60' : 'text-gray-500')}>
        {subtext}
      </div>
    </div>
  );
}

function PoolCardMobile({
  pool,
  isLoading,
}: {
  pool: ReturnType<typeof usePoolStatus>['data'];
  isLoading?: boolean;
}) {
  if (isLoading) {
    return (
      <div className="p-4 rounded-2xl bg-gradient-to-b from-white/[0.06] to-white/[0.02] border border-white/10">
        <Skeleton className="h-2.5 w-14 mb-2" />
        <Skeleton className="h-6 w-16 mb-1" />
        <Skeleton className="h-1.5 w-full rounded-full" />
      </div>
    );
  }

  return (
    <div
      className={cn(
        'p-4 rounded-2xl',
        pool?.thresholdMet
          ? 'bg-gradient-to-b from-amber-500/10 to-amber-500/[0.02] border border-amber-500/20'
          : 'bg-gradient-to-b from-white/[0.06] to-white/[0.02] border border-white/10'
      )}
    >
      <div className="text-[10px] text-gray-400 uppercase tracking-widest mb-1">
        Pool
      </div>
      <div
        className={cn(
          'text-xl font-bold font-mono',
          pool?.thresholdMet ? 'text-amber-400' : 'text-white'
        )}
      >
        {pool?.progressToThreshold.toFixed(0) ?? 0}%
      </div>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mt-2">
        <div
          className={cn(
            'h-full transition-all duration-500 rounded-full',
            pool?.thresholdMet
              ? 'bg-gradient-to-r from-amber-500 to-amber-400 animate-pulse'
              : 'bg-gradient-to-r from-white/40 to-white/60'
          )}
          style={{ width: `${pool?.progressToThreshold ?? 0}%` }}
        />
      </div>
      {pool?.thresholdMet && (
        <div className="text-xs text-amber-400 mt-1 text-center">READY</div>
      )}
    </div>
  );
}

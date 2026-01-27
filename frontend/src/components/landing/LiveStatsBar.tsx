'use client';

import { cn } from '@/lib/cn';
import { formatCompactNumber, formatUSD } from '@/lib/utils';
import { Skeleton } from '@/components/ui';
import { useCountdown, useAnimatedNumber } from '@/hooks/useCountdown';
import { useSocketContext } from '@/components/providers/SocketProvider';

export interface LiveStatsBarProps {
  /** Total holders */
  holders: number;
  /** Total GOLD distributed */
  totalDistributed: number;
  /** 24h volume (USD) */
  volume24h: number;
  /** Pool value (USD) */
  poolValueUsd: number;
  /** Hours until next distribution */
  hoursUntilNext: number | null;
  /** Is loading */
  isLoading?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * LiveStatsBar - Real-time ticker of global stats with count-up animation
 * Shows actual WebSocket connection status when wallet is connected
 */
export function LiveStatsBar({
  holders,
  totalDistributed,
  volume24h,
  poolValueUsd,
  hoursUntilNext,
  isLoading = false,
  className,
}: LiveStatsBarProps) {
  const countdown = useCountdown(hoursUntilNext);
  const { status: socketStatus } = useSocketContext();

  // Animated number values for smooth count-up effect
  const animatedHolders = useAnimatedNumber(holders, 800);
  const animatedDistributed = useAnimatedNumber(totalDistributed, 800);
  const animatedVolume = useAnimatedNumber(volume24h, 800);
  const animatedPool = useAnimatedNumber(poolValueUsd, 800);

  if (isLoading) {
    return <LiveStatsBarSkeleton className={className} />;
  }

  return (
    <div
      className={cn(
        'w-full py-3 px-4',
        // Desktop: Terminal style
        'lg:bg-terminal-card lg:border-y lg:border-terminal-border',
        // Mobile: Clean style
        'bg-zinc-900/50 border-y border-zinc-800',
        className
      )}
    >
      <div className="max-w-6xl mx-auto">
        {/* Desktop Layout - Horizontal */}
        <div className="hidden lg:flex items-center justify-center gap-8 font-mono text-sm">
          {/* Connection-aware Live Indicator */}
          <ConnectionIndicator socketStatus={socketStatus} />
          <Divider />
          <StatItem
            label="MINERS"
            value={formatCompactNumber(Math.round(animatedHolders))}
          />
          <Divider />
          <StatItem
            label="DISTRIBUTED"
            value={`${formatCompactNumber(Math.round(animatedDistributed))} $GOLD`}
          />
          <Divider />
          <StatItem
            label="24H VOLUME"
            value={formatUSD(animatedVolume, true)}
          />
          <Divider />
          <StatItem
            label="POOL"
            value={formatUSD(animatedPool)}
            highlight={poolValueUsd >= 250}
          />
          <Divider />
          <StatItem
            label="NEXT PAYOUT"
            value={countdown.formatted}
            highlight={countdown.isComplete}
          />
        </div>

        {/* Mobile Layout - 2x2 Grid with Live indicator */}
        <div className="lg:hidden">
          {/* Live indicator row */}
          <div className="flex items-center justify-center mb-2">
            <ConnectionIndicator socketStatus={socketStatus} compact />
          </div>
          {/* Stats grid */}
          <div className="grid grid-cols-5 gap-1">
            <MobileStatItem label="Miners" value={formatCompactNumber(Math.round(animatedHolders))} />
            <MobileStatItem label="Distributed" value={`${formatCompactNumber(Math.round(animatedDistributed))}`} />
            <MobileStatItem label="Volume" value={formatUSD(animatedVolume, true)} />
            <MobileStatItem
              label="Pool"
              value={formatUSD(animatedPool)}
              highlight={poolValueUsd >= 250}
            />
            <MobileStatItem
              label="Next"
              value={countdown.formattedCompact}
              highlight={countdown.isComplete}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Connection indicator component
 * Shows WebSocket connection status independent of wallet state
 */
function ConnectionIndicator({
  socketStatus,
  compact = false,
}: {
  socketStatus: 'connected' | 'connecting' | 'disconnected';
  compact?: boolean;
}) {
  const isLive = socketStatus === 'connected';
  const isConnecting = socketStatus === 'connecting';

  // Colors and labels based on WebSocket status
  let dotColor: string;
  let label: string;
  let showPing: boolean;

  if (isLive) {
    dotColor = 'bg-green-400';
    label = 'Live';
    showPing = true;
  } else if (isConnecting) {
    dotColor = 'bg-amber-400';
    label = 'Connecting';
    showPing = false;
  } else {
    // Disconnected
    dotColor = 'bg-gray-400';
    label = 'Offline';
    showPing = false;
  }

  const dotSize = compact ? 'w-1.5 h-1.5' : 'w-2 h-2';
  const textSize = compact ? 'text-[10px]' : 'text-xs';

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex items-center justify-center">
        {/* Core dot */}
        <span
          className={cn(
            dotSize,
            'rounded-full',
            dotColor,
            isConnecting && 'animate-pulse'
          )}
        />
        {/* Ping animation for live status */}
        {showPing && (
          <span
            className={cn(
              'absolute',
              dotSize,
              'rounded-full animate-ping',
              'bg-green-400/50'
            )}
          />
        )}
      </div>
      <span
        className={cn(
          textSize,
          'font-medium uppercase tracking-wider',
          isLive && 'text-green-400',
          isConnecting && 'text-amber-400',
          !isLive && !isConnecting && 'text-gray-400'
        )}
      >
        {label}
      </span>
    </div>
  );
}

/**
 * Desktop stat item with hover effect
 */
function StatItem({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="group cursor-default transition-all duration-200 hover:scale-105">
      <div className="text-caption text-gray-500 uppercase tracking-wider">{label}</div>
      <div
        className={cn(
          'font-terminal text-lg tabular-nums transition-all duration-200',
          highlight ? 'text-white glow-white' : 'text-gray-200',
          'group-hover:text-white'
        )}
      >
        {value}
      </div>
    </div>
  );
}

/**
 * Mobile stat item with hover effect
 */
function MobileStatItem({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="text-center group">
      <div
        className={cn(
          'text-sm font-medium tabular-nums transition-colors duration-200',
          highlight ? 'text-white glow-white' : 'text-gray-200'
        )}
      >
        {value}
      </div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

/**
 * Enhanced vertical divider
 */
function Divider() {
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="w-px h-2 bg-gray-700" />
      <div className="w-1 h-1 rounded-full bg-gray-700" />
      <div className="w-px h-2 bg-gray-700" />
    </div>
  );
}

/**
 * Loading skeleton
 */
function LiveStatsBarSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'w-full py-3 px-4',
        'lg:bg-terminal-card lg:border-y lg:border-terminal-border',
        'bg-zinc-900/50 border-y border-zinc-800',
        className
      )}
    >
      <div className="max-w-6xl mx-auto">
        {/* Desktop */}
        <div className="hidden lg:flex items-center justify-center gap-8">
          {/* Live indicator skeleton */}
          <div className="flex items-center gap-2">
            <Skeleton className="w-2 h-2 rounded-full" />
            <Skeleton className="h-3 w-12" />
          </div>
          <div className="w-px h-8 bg-terminal-border" />
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-8">
              <div className="space-y-1">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-5 w-20" />
              </div>
              {i < 5 && <div className="w-px h-8 bg-terminal-border" />}
            </div>
          ))}
        </div>
        {/* Mobile */}
        <div className="lg:hidden">
          <div className="flex justify-center mb-2">
            <Skeleton className="h-3 w-16" />
          </div>
          <div className="grid grid-cols-5 gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="text-center space-y-1">
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-3 w-8 mx-auto" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

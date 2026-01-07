'use client';

import { cn } from '@/lib/cn';
import type { TierInfo } from '@/types/api';

export interface BadgeProps {
  /** Badge variant */
  variant?: 'default' | 'accent' | 'muted' | 'tier';
  /** Badge size */
  size?: 'sm' | 'md' | 'lg';
  /** Badge content */
  children: React.ReactNode;
  /** Additional class names */
  className?: string;
}

/**
 * Badge component with monochrome palette
 */
export function Badge({
  variant = 'default',
  size = 'md',
  children,
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        // Base styles
        'inline-flex items-center font-medium rounded-full',
        // Size variants
        size === 'sm' && 'px-2 py-0.5 text-xs',
        size === 'md' && 'px-2.5 py-0.5 text-sm',
        size === 'lg' && 'px-3 py-1 text-sm',
        // Color variants (monochrome)
        variant === 'default' && 'bg-bg-surface text-text-secondary',
        variant === 'accent' && 'bg-white/20 text-white',
        variant === 'muted' && 'bg-gray-700/50 text-gray-400',
        variant === 'tier' && 'bg-white/10 text-white border border-white/30',
        className
      )}
    >
      {children}
    </span>
  );
}

/**
 * Tier badge component
 * Displays tier name in brackets [TIER]
 */
export function TierBadge({
  tier,
  showMultiplier = false,
  size = 'md',
  className,
}: {
  tier: TierInfo;
  showMultiplier?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}) {
  return (
    <Badge variant="tier" size={size} className={className}>
      <span>[{tier.name.toUpperCase()}]</span>
      {showMultiplier && (
        <span className="ml-1 text-gray-500">({tier.multiplier}x)</span>
      )}
    </Badge>
  );
}

/**
 * Rank badge component
 * Displays user rank
 */
export function RankBadge({
  rank,
  size = 'md',
  className,
}: {
  rank: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}) {
  return (
    <Badge
      variant={rank <= 3 ? 'accent' : 'default'}
      size={size}
      className={className}
    >
      <span>#{rank}</span>
    </Badge>
  );
}

/**
 * Status badge component
 */
export function StatusBadge({
  status,
  size = 'md',
  className,
}: {
  status: 'online' | 'offline' | 'pending' | 'success' | 'error';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}) {
  const statusConfig = {
    online: { variant: 'accent' as const, label: '[ONLINE]' },
    offline: { variant: 'muted' as const, label: '[OFFLINE]' },
    pending: { variant: 'default' as const, label: '[PENDING]' },
    success: { variant: 'accent' as const, label: '[SUCCESS]' },
    error: { variant: 'muted' as const, label: '[ERROR]' },
  };

  const { variant, label } = statusConfig[status];

  return (
    <Badge variant={variant} size={size} className={className}>
      {label}
    </Badge>
  );
}

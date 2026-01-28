'use client';

import { cn } from '@/lib/cn';

export interface BadgeProps {
  /** Badge variant */
  variant?: 'default' | 'accent' | 'muted';
  /** Badge size */
  size?: 'sm' | 'md' | 'lg';
  /** Badge content */
  children: React.ReactNode;
  /** Additional class names */
  className?: string;
}

/**
 * Badge component with light theme palette
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
        // Color variants (light theme)
        variant === 'default' && 'bg-gray-100 text-gray-700',
        variant === 'accent' && 'bg-gray-900 text-white',
        variant === 'muted' && 'bg-gray-50 text-gray-500',
        className
      )}
    >
      {children}
    </span>
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
    online: { variant: 'accent' as const, label: 'Online' },
    offline: { variant: 'muted' as const, label: 'Offline' },
    pending: { variant: 'default' as const, label: 'Pending' },
    success: { variant: 'accent' as const, label: 'Success' },
    error: { variant: 'muted' as const, label: 'Error' },
  };

  const { variant, label } = statusConfig[status];

  return (
    <Badge variant={variant} size={size} className={className}>
      {label}
    </Badge>
  );
}

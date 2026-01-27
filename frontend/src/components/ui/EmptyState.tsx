'use client';

import { cn } from '@/lib/cn';
import { Button } from './Button';

export interface EmptyStateProps {
  /** Icon (emoji or ASCII art) */
  icon?: string;
  /** Title */
  title: string;
  /** Description */
  description?: string;
  /** Action button */
  action?: {
    label: string;
    onClick: () => void;
  };
  /** Additional class names */
  className?: string;
}

/**
 * Empty state component
 * Shown when there's no data to display
 */
export function EmptyState({
  icon = '[ ]',
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-8 text-center',
        className
      )}
    >
      {/* Icon */}
      <div
        className="text-4xl text-gray-500 mb-4 font-mono"
        aria-hidden="true"
      >
        {icon}
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>

      {/* Description */}
      {description && (
        <p className="text-sm text-gray-500 max-w-sm mb-4">{description}</p>
      )}

      {/* Action */}
      {action && (
        <Button variant="outline" size="sm" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
}

export function ConnectWalletEmpty() {
  return (
    <EmptyState
      icon="🔗"
      title="Enter your wallet address"
      description="Paste your Solana wallet address to view your mining stats"
    />
  );
}

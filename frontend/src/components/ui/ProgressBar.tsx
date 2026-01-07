'use client';

import { cn } from '@/lib/cn';

export interface ProgressBarProps {
  /** Progress value (0-100) */
  value: number;
  /** Maximum value (default: 100) */
  max?: number;
  /** Show percentage label */
  showLabel?: boolean;
  /** Custom label */
  label?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Color variant */
  variant?: 'default' | 'gradient';
  /** Additional class names */
  className?: string;
}

/**
 * Progress bar component
 * Monochrome terminal aesthetic
 */
export function ProgressBar({
  value,
  max = 100,
  showLabel = false,
  label,
  size = 'md',
  variant = 'default',
  className,
}: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  // Size classes
  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  // Color classes for the fill
  const fillClasses = {
    default: 'bg-white',
    gradient: 'bg-gradient-to-r from-gray-500 via-gray-300 to-white',
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Label */}
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1">
          {label && (
            <span className="text-xs text-gray-500 font-mono">{label}</span>
          )}
          {showLabel && (
            <span className="text-xs text-gray-400 font-mono">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}

      {/* Progress track */}
      <div
        className={cn(
          'w-full rounded-full overflow-hidden',
          'bg-gray-700',
          sizeClasses[size]
        )}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        {/* Progress fill */}
        <div
          className={cn(
            'h-full rounded-full transition-all duration-300 ease-out',
            fillClasses[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

/**
 * ASCII-style progress bar (desktop only)
 * Shows progress like: [████████░░░░░░░░] 50%
 */
export function AsciiProgressBar({
  value,
  max = 100,
  width = 20,
  className,
}: {
  value: number;
  max?: number;
  width?: number;
  className?: string;
}) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  const filled = Math.round((percentage / 100) * width);
  const empty = width - filled;

  const filledChars = '█'.repeat(filled);
  const emptyChars = '░'.repeat(empty);

  return (
    <span className={cn('font-mono text-sm whitespace-pre', className)}>
      <span className="text-gray-500">[</span>
      <span className="text-white">{filledChars}</span>
      <span className="text-gray-600">{emptyChars}</span>
      <span className="text-gray-500">]</span>
      <span className="text-gray-500 ml-2">{Math.round(percentage)}%</span>
    </span>
  );
}

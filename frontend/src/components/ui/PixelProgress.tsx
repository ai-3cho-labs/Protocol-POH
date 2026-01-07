'use client';

import { cn } from '@/lib/cn';

export interface PixelProgressProps {
  /** Current progress value */
  value: number;
  /** Maximum value (default: 100) */
  max?: number;
  /** Number of segments */
  segments?: number;
  /** Show percentage label */
  showLabel?: boolean;
  /** Custom label text */
  label?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Color variant */
  variant?: 'default' | 'gradient';
  /** Additional class names */
  className?: string;
}

/**
 * Pixel-styled segmented progress bar
 * Monochrome terminal aesthetic
 */
export function PixelProgress({
  value,
  max = 100,
  segments = 10,
  showLabel = false,
  label,
  size = 'md',
  variant = 'default',
  className,
}: PixelProgressProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  const filledSegments = Math.round((percentage / 100) * segments);

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* Progress bar container */}
      <div
        className={cn(
          'flex gap-0.5 bg-bg-dark rounded p-1',
          size === 'sm' && 'p-0.5',
          size === 'lg' && 'p-1.5'
        )}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        {Array.from({ length: segments }).map((_, i) => {
          const isFilled = i < filledSegments;
          return (
            <div
              key={i}
              className={cn(
                'transition-all duration-150',
                // Size
                size === 'sm' && 'w-2 h-3',
                size === 'md' && 'w-3 h-4',
                size === 'lg' && 'w-4 h-5',
                // Rounded ends
                i === 0 && 'rounded-l',
                i === segments - 1 && 'rounded-r',
                // Filled state
                isFilled
                  ? cn(
                      variant === 'default' && 'bg-white',
                      variant === 'gradient' &&
                        i < filledSegments * 0.33
                        ? 'bg-gray-500'
                        : i < filledSegments * 0.66
                        ? 'bg-gray-300'
                        : 'bg-white'
                    )
                  : 'bg-bg-surface'
              )}
            />
          );
        })}
      </div>

      {/* Label */}
      {showLabel && (
        <span className="text-sm text-text-secondary font-medium min-w-[3ch]">
          {label || `${Math.round(percentage)}%`}
        </span>
      )}
    </div>
  );
}

/**
 * Simple linear progress bar (non-segmented)
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
}: Omit<PixelProgressProps, 'segments'>) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* Progress bar container */}
      <div
        className={cn(
          'flex-1 bg-bg-surface rounded-full overflow-hidden',
          size === 'sm' && 'h-2',
          size === 'md' && 'h-3',
          size === 'lg' && 'h-4'
        )}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out rounded-full',
            variant === 'default' && 'bg-white',
            variant === 'gradient' &&
              'bg-gradient-to-r from-gray-500 via-gray-300 to-white'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Label */}
      {showLabel && (
        <span className="text-sm text-text-secondary font-medium min-w-[3ch]">
          {label || `${Math.round(percentage)}%`}
        </span>
      )}
    </div>
  );
}

/**
 * ASCII-style progress bar (backwards compatibility alias)
 * Now renders as PixelProgress with segments
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
  return (
    <PixelProgress
      value={value}
      max={max}
      segments={width}
      showLabel
      size="sm"
      variant="default"
      className={className}
    />
  );
}

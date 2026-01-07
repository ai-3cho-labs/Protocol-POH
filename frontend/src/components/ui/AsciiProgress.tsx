'use client';

import { cn } from '@/lib/cn';

export interface AsciiProgressProps {
  /** Progress value (0-100) */
  value: number;
  /** Maximum value */
  max?: number;
  /** Width in characters */
  width?: number;
  /** Show percentage label */
  showLabel?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * AsciiProgress component
 * Terminal-style ASCII progress bar: [███░░░░░░░] 50%
 */
export function AsciiProgress({
  value,
  max = 100,
  width = 10,
  showLabel = true,
  className,
}: AsciiProgressProps) {
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
      {showLabel && (
        <span className="text-gray-400 ml-2">{Math.round(percentage)}%</span>
      )}
    </span>
  );
}

/**
 * AsciiLoadingBar component
 * Animated loading bar for indeterminate progress
 */
export function AsciiLoadingBar({
  width = 10,
  className,
}: {
  width?: number;
  className?: string;
}) {
  return (
    <span className={cn('font-mono text-sm whitespace-pre inline-flex', className)}>
      <span className="text-gray-500">[</span>
      <span className="text-white animate-pulse">
        {'█'.repeat(Math.floor(width / 3))}
      </span>
      <span className="text-gray-600">
        {'░'.repeat(width - Math.floor(width / 3))}
      </span>
      <span className="text-gray-500">]</span>
    </span>
  );
}

/**
 * AsciiSpinner component
 * Rotating ASCII spinner
 */
export function AsciiSpinner({
  className,
}: {
  className?: string;
}) {
  return (
    <span className={cn('font-mono text-white inline-block animate-spin', className)}>
      ◐
    </span>
  );
}

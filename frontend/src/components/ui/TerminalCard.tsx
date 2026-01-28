'use client';

import { forwardRef, HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/cn';

export interface TerminalCardProps extends HTMLAttributes<HTMLDivElement> {
  /** Card title (displayed in header) */
  title?: string;
  /** Card variant */
  variant?: 'default' | 'highlight' | 'success' | 'error';
  /** Remove default padding */
  noPadding?: boolean;
  /** Header right content */
  headerRight?: ReactNode;
}

/**
 * Card component - Light theme
 * Converted from terminal aesthetic to modern light design
 */
export const TerminalCard = forwardRef<HTMLDivElement, TerminalCardProps>(
  (
    {
      className,
      title,
      variant = 'default',
      noPadding = false,
      headerRight,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base styles
          'rounded-xl overflow-hidden',
          'bg-white border border-gray-100',
          // Shadow
          'shadow-sm',
          // Variant styles
          variant === 'highlight' && 'border-gray-300 shadow-md',
          variant === 'success' && 'border-emerald-200',
          variant === 'error' && 'border-red-200',
          className
        )}
        {...props}
      >
        {/* Header */}
        {title && (
          <div
            className={cn(
              'px-4 py-2.5 border-b flex items-center justify-between',
              'border-gray-100 bg-gray-50/50'
            )}
          >
            <span className="font-medium text-sm text-gray-900">
              {title}
            </span>
            {headerRight && (
              <div className="flex items-center gap-2">{headerRight}</div>
            )}
          </div>
        )}

        {/* Content */}
        <div className={cn(!noPadding && 'p-4')}>{children}</div>
      </div>
    );
  }
);

TerminalCard.displayName = 'TerminalCard';

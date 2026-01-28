'use client';

import { forwardRef, HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/cn';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Card title (displayed in header) */
  title?: string;
  /** Card variant */
  variant?: 'default' | 'highlight' | 'success' | 'error';
  /** Remove default padding */
  noPadding?: boolean;
  /** Header right content */
  headerRight?: ReactNode;
  /** Add accent border */
  pixelAccent?: boolean;
}

/**
 * Card component with light modern aesthetic
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      title,
      variant = 'default',
      noPadding = false,
      headerRight,
      pixelAccent = false,
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
          // Accent border
          pixelAccent && 'border-2 border-gray-200',
          className
        )}
        {...props}
      >
        {/* Header */}
        {title && (
          <div
            className={cn(
              'px-4 py-3 border-b border-gray-100 flex items-center justify-between',
              'bg-gray-50/50'
            )}
          >
            <span
              className={cn(
                'font-medium text-sm text-gray-900'
              )}
            >
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

Card.displayName = 'Card';

// Backwards compatibility alias
export const TerminalCard = Card;
export type TerminalCardProps = CardProps;

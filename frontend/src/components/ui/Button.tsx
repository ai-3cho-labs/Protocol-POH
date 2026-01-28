'use client';

import { forwardRef, ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/cn';
import { LoadingSpinner } from './LoadingSpinner';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Show loading state */
  loading?: boolean;
  /** Make button full width */
  fullWidth?: boolean;
  /** Left icon */
  leftIcon?: React.ReactNode;
  /** Right icon */
  rightIcon?: React.ReactNode;
}

/**
 * Button component
 * Light modern aesthetic
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      fullWidth = false,
      leftIcon,
      rightIcon,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center gap-2',
          'font-medium transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-gray-900/20 focus:ring-offset-2 focus:ring-offset-white',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          // Size variants
          size === 'sm' && 'px-3 py-1.5 text-sm rounded-md',
          size === 'md' && 'px-4 py-2 text-sm rounded-lg',
          size === 'lg' && 'px-6 py-3 text-base rounded-lg',
          // Variant styles
          variant === 'primary' && [
            'bg-black text-white shadow-md',
            'hover:bg-gray-800',
            'active:bg-gray-700',
          ],
          variant === 'secondary' && [
            'bg-gray-100 text-gray-900',
            'border border-gray-200',
            'hover:bg-gray-200',
          ],
          variant === 'outline' && [
            'bg-transparent text-gray-600',
            'border border-gray-200',
            'hover:border-gray-900 hover:text-gray-900',
          ],
          variant === 'ghost' && [
            'bg-transparent text-gray-600',
            'hover:bg-gray-100 hover:text-gray-900',
          ],
          variant === 'danger' && [
            'bg-red-50 text-red-600',
            'border border-red-200',
            'hover:bg-red-100',
          ],
          // Full width
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {/* Loading spinner */}
        {loading && <LoadingSpinner size="sm" />}

        {/* Left icon */}
        {!loading && leftIcon && (
          <span className="flex-shrink-0">{leftIcon}</span>
        )}

        {/* Children */}
        {children}

        {/* Right icon */}
        {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';

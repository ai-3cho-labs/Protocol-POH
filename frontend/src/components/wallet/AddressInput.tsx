'use client';

import { useState, useCallback, KeyboardEvent, ChangeEvent } from 'react';
import { useAddressContext } from '@/contexts/AddressContext';
import { isValidSolanaAddress } from '@/lib/validators';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/Button';

export interface AddressInputProps {
  /** Button/input size */
  size?: 'sm' | 'md' | 'lg';
  /** Make input full width */
  fullWidth?: boolean;
  /** Custom class names */
  className?: string;
}

/**
 * Address input component
 * Shows input field when disconnected, wallet info when connected
 */
export function AddressInput({
  size = 'md',
  fullWidth = false,
  className,
}: AddressInputProps) {
  const { address, shortAddress, isConnected, setAddress, clearAddress, error, clearError } =
    useAddressContext();

  const [inputValue, setInputValue] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const [isFocused, setIsFocused] = useState(false);

  // Combined error from context or local validation
  const displayError = localError || error;

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      setInputValue(e.target.value);
      // Clear errors when user starts typing
      if (localError) setLocalError(null);
      if (error) clearError();
    },
    [localError, error, clearError]
  );

  const handleSubmit = useCallback(() => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    // Validate locally first for immediate feedback
    if (!isValidSolanaAddress(trimmed)) {
      setLocalError('Invalid Solana address');
      return;
    }

    // Set address through context (validates again)
    const success = setAddress(trimmed);
    if (success) {
      setInputValue('');
      setLocalError(null);
    }
  }, [inputValue, setAddress]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handleClear = useCallback(() => {
    clearAddress();
    setInputValue('');
    setLocalError(null);
  }, [clearAddress]);

  // Size-based styles
  const sizeStyles = {
    sm: {
      input: 'px-3 py-1.5 text-sm',
      button: 'px-2',
      icon: 'w-3.5 h-3.5',
    },
    md: {
      input: 'px-4 py-2 text-sm',
      button: 'px-2.5',
      icon: 'w-4 h-4',
    },
    lg: {
      input: 'px-5 py-3 text-base',
      button: 'px-3',
      icon: 'w-5 h-5',
    },
  };

  const styles = sizeStyles[size];

  // Connected state - show address with clear button
  if (isConnected && shortAddress) {
    return (
      <div className={cn('flex items-center gap-2', fullWidth && 'w-full')}>
        {/* Address display button */}
        <Button
          variant="secondary"
          size={size}
          className={cn('flex-1 font-mono', className)}
          onClick={() => {
            // Copy full address to clipboard
            if (address) {
              navigator.clipboard.writeText(address).catch(() => {});
            }
          }}
          title="Click to copy address"
        >
          <span className="font-mono">{shortAddress}</span>
        </Button>

        {/* Clear/disconnect button */}
        <Button
          variant="ghost"
          size={size}
          onClick={handleClear}
          aria-label="Clear wallet address"
          className="px-2"
        >
          <svg
            className={styles.icon}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </Button>
      </div>
    );
  }

  // Disconnected state - show input field
  return (
    <div className={cn('relative', fullWidth && 'w-full', className)}>
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={inputValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => {
              setIsFocused(false);
              // Submit on blur if there's a value
              if (inputValue.trim()) {
                handleSubmit();
              }
            }}
            placeholder="Paste wallet address..."
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck="false"
            className={cn(
              // Base styles
              'w-full font-mono rounded-lg transition-all duration-200',
              'bg-bg-card text-text-primary placeholder:text-text-muted',
              'border focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-bg-dark',
              // Size styles
              styles.input,
              // Error state
              displayError
                ? 'border-red-500/50 focus:border-red-500 focus:ring-red-500/50'
                : 'border-border focus:border-gray-500 focus:ring-white/50',
              // Focus state
              isFocused && !displayError && 'border-gray-500'
            )}
          />
        </div>

        {/* Submit button (visible when there's input) */}
        {inputValue.trim() && (
          <Button
            variant="primary"
            size={size}
            onClick={handleSubmit}
            aria-label="Submit address"
          >
            <svg
              className={styles.icon}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </Button>
        )}
      </div>

      {/* Error message */}
      {displayError && (
        <p className="absolute mt-1 text-xs text-red-400">{displayError}</p>
      )}
    </div>
  );
}

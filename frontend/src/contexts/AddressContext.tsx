'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
  FC,
} from 'react';
import { isValidSolanaAddress } from '@/lib/validators';
import { shortenAddress } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface AddressContextType {
  /** Full wallet address or null if not set */
  address: string | null;
  /** Shortened address (e.g., "ABC1...XYZ9") or null */
  shortAddress: string | null;
  /** Whether an address is currently set */
  isConnected: boolean;
  /** Set a new address. Returns false if invalid. */
  setAddress: (addr: string) => boolean;
  /** Clear the stored address */
  clearAddress: () => void;
  /** Current error message (e.g., "Invalid address") */
  error: string | null;
  /** Clear the error message */
  clearError: () => void;
}

// ============================================================================
// Constants
// ============================================================================

const STORAGE_KEY = 'cpu_wallet_address';

// ============================================================================
// Context
// ============================================================================

const AddressContext = createContext<AddressContextType>({
  address: null,
  shortAddress: null,
  isConnected: false,
  setAddress: () => false,
  clearAddress: () => {},
  error: null,
  clearError: () => {},
});

/**
 * Hook to access the address context
 */
export function useAddressContext(): AddressContextType {
  const context = useContext(AddressContext);
  if (!context) {
    throw new Error('useAddressContext must be used within an AddressProvider');
  }
  return context;
}

// ============================================================================
// Provider
// ============================================================================

interface AddressProviderProps {
  children: ReactNode;
}

/**
 * Address Provider Component
 *
 * Manages wallet address state with localStorage persistence.
 * Always validates addresses before storing or using them.
 */
export const AddressProvider: FC<AddressProviderProps> = ({ children }) => {
  const [address, setAddressState] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  // Load address from localStorage on mount (client-side only)
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        // Security: Always validate stored value
        if (isValidSolanaAddress(stored)) {
          setAddressState(stored);
        } else {
          // Invalid stored value - clear it
          localStorage.removeItem(STORAGE_KEY);
          console.warn('Cleared invalid address from localStorage');
        }
      }
    } catch (e) {
      // localStorage might not be available (SSR or privacy mode)
      console.warn('Could not access localStorage:', e);
    }
    setIsHydrated(true);
  }, []);

  // Set a new address with validation
  const setAddress = useCallback((addr: string): boolean => {
    const trimmed = addr.trim();

    // Validate address format
    if (!isValidSolanaAddress(trimmed)) {
      setError('Invalid Solana address format');
      return false;
    }

    // Store in localStorage
    try {
      localStorage.setItem(STORAGE_KEY, trimmed);
    } catch (e) {
      console.warn('Could not save to localStorage:', e);
    }

    setAddressState(trimmed);
    setError(null);
    return true;
  }, []);

  // Clear the stored address
  const clearAddress = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      console.warn('Could not clear localStorage:', e);
    }
    setAddressState(null);
    setError(null);
  }, []);

  // Clear error message
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Compute derived values
  const shortAddress = address ? shortenAddress(address) : null;
  const isConnected = address !== null;

  // Prevent hydration mismatch by not rendering children until hydrated
  // We still render immediately but with null address until hydrated
  const value: AddressContextType = {
    address: isHydrated ? address : null,
    shortAddress: isHydrated ? shortAddress : null,
    isConnected: isHydrated ? isConnected : false,
    setAddress,
    clearAddress,
    error,
    clearError,
  };

  return (
    <AddressContext.Provider value={value}>{children}</AddressContext.Provider>
  );
};

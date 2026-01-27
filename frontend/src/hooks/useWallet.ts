'use client';

import { useAddressContext } from '@/contexts/AddressContext';

/**
 * Custom wallet hook
 * Provides simplified access to wallet address state
 *
 * This is a lightweight replacement for the Solana wallet adapter.
 * Users paste their address instead of connecting a wallet,
 * which improves security since no signing is ever needed.
 */
export function useWallet() {
  const {
    address,
    shortAddress,
    isConnected,
    setAddress,
    clearAddress,
    error,
    clearError,
  } = useAddressContext();

  return {
    // State
    address,
    shortAddress,
    connected: isConnected,
    isReady: isConnected,

    // Actions
    disconnect: clearAddress,
    setAddress,

    // Error handling
    error,
    clearError,
  };
}

/**
 * Hook to check if a wallet address is set
 * Returns just the connection status for simple checks
 */
export function useIsConnected(): boolean {
  const { isConnected } = useAddressContext();
  return isConnected;
}

/**
 * Hook to get just the wallet address
 * Returns null if not set
 */
export function useWalletAddress(): string | null {
  const { address } = useAddressContext();
  return address;
}

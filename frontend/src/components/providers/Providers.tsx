'use client';

import { FC, ReactNode } from 'react';
import { AddressProvider } from '@/contexts/AddressContext';
import { QueryProvider } from './QueryProvider';
import { SocketProvider } from './SocketProvider';
import { ErrorBoundary } from './ErrorBoundary';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Combined Providers
 * Wraps the application with all necessary context providers
 *
 * Provider order (outer to inner):
 * 1. ErrorBoundary - Catches runtime errors
 * 2. QueryProvider - Data fetching and caching
 * 3. AddressProvider - Wallet address storage (localStorage)
 * 4. SocketProvider - WebSocket connection (requires address state)
 */
export const Providers: FC<ProvidersProps> = ({ children }) => {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <AddressProvider>
          <SocketProvider>{children}</SocketProvider>
        </AddressProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
};

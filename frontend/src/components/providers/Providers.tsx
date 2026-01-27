'use client';

import { FC, ReactNode } from 'react';
import { AddressProvider } from '@/contexts/AddressContext';
import { QueryProvider } from './QueryProvider';
import { SocketProvider } from './SocketProvider';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Combined Providers
 * Wraps the application with all necessary context providers
 *
 * Provider order (outer to inner):
 * 1. QueryProvider - Data fetching and caching
 * 2. AddressProvider - Wallet address storage (localStorage)
 * 3. SocketProvider - WebSocket connection (requires address state)
 */
export const Providers: FC<ProvidersProps> = ({ children }) => {
  return (
    <QueryProvider>
      <AddressProvider>
        <SocketProvider>{children}</SocketProvider>
      </AddressProvider>
    </QueryProvider>
  );
};

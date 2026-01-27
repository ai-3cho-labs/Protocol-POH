'use client';

import { FC, ReactNode, useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

interface QueryProviderProps {
  children: ReactNode;
}

/**
 * TanStack Query Provider
 *
 * Configured for WebSocket-driven updates with localStorage persistence:
 * - Data cached indefinitely (staleTime: Infinity)
 * - No automatic refetching on mount or window focus
 * - WebSocket events invalidate queries when data changes
 * - Cache persisted to localStorage for instant load on tab restart
 */
export const QueryProvider: FC<QueryProviderProps> = ({ children }) => {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Never stale - WebSocket invalidates when data changes
            staleTime: Infinity,
            // Keep in memory cache for 24 hours
            gcTime: 24 * 60 * 60 * 1000,
            // Don't refetch on mount - use cached data
            refetchOnMount: false,
            // Don't refetch on focus - WebSocket keeps data fresh
            refetchOnWindowFocus: false,
            // Retry failed requests up to 3 times
            retry: 3,
            // Exponential backoff for retries
            retryDelay: (attemptIndex) =>
              Math.min(1000 * 2 ** attemptIndex, 30000),
          },
          mutations: {
            retry: 1,
          },
        },
      })
  );

  // Persist cache to localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const persister = createSyncStoragePersister({
      storage: window.localStorage,
      key: 'cpu-query-cache',
    });

    persistQueryClient({
      queryClient,
      persister,
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
    });
  }, [queryClient]);

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

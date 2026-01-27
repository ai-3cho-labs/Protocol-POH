'use client';

import { useQuery } from '@tanstack/react-query';
import { getGlobalStats } from '@/lib/api';
import type { GlobalStatsResponse } from '@/types/api';

/** Query key for global stats */
export const GLOBAL_STATS_QUERY_KEY = ['globalStats'] as const;

/**
 * Hook to fetch global statistics
 * WebSocket handles live updates via distribution:executed and snapshot:taken events
 */
export function useGlobalStats() {
  return useQuery<GlobalStatsResponse, Error>({
    queryKey: GLOBAL_STATS_QUERY_KEY,
    queryFn: getGlobalStats,
    staleTime: Infinity, // Never stale - WebSocket handles live updates
    refetchOnMount: false, // Use cache, WebSocket invalidates when needed
    refetchOnWindowFocus: false, // WebSocket keeps data fresh
  });
}

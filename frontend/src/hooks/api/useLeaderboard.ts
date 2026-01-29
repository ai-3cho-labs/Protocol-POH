'use client';

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { getLeaderboard } from '@/lib/api';
import type { LeaderboardEntry } from '@/types/api';
import type { LeaderboardUser } from '@/types/models';

/** Query key factory for leaderboard */
export const leaderboardQueryKey = (limit: number) =>
  ['leaderboard', limit] as const;

/**
 * Transform leaderboard entry to UI model
 */
function transformLeaderboardEntry(
  entry: LeaderboardEntry,
  currentWallet: string | null
): LeaderboardUser {
  return {
    rank: entry.rank,
    wallet: entry.wallet,
    walletShort: entry.wallet_short,
    totalEarned: entry.total_earned,
    isCurrentUser: currentWallet?.toLowerCase() === entry.wallet.toLowerCase(),
  };
}

/**
 * Hook to fetch leaderboard
 * @param limit - Number of entries to fetch (default: 10)
 * @param currentWallet - Current user's wallet address (for highlighting)
 */
export function useLeaderboard(limit = 10, currentWallet: string | null = null) {
  const query = useQuery<LeaderboardEntry[], Error>({
    queryKey: leaderboardQueryKey(limit),
    queryFn: () => getLeaderboard(limit),
    staleTime: 0, // Always refetch for fresh data
    refetchOnMount: 'always', // Force refetch every mount
    refetchOnWindowFocus: true, // Refetch when user returns
  });

  // Transform data with current user highlighting
  const data = useMemo(() => {
    if (!query.data) return null;
    return query.data.map((entry) =>
      transformLeaderboardEntry(entry, currentWallet)
    );
  }, [query.data, currentWallet]);

  return {
    ...query,
    data,
    rawData: query.data,
  };
}

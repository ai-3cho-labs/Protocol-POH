'use client';

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { getUserStats } from '@/lib/api';
import type { UserStatsResponse } from '@/types/api';
import type { UserMiningStats } from '@/types/models';

/** Query key factory for user stats */
export const userStatsQueryKey = (wallet: string) => ['userStats', wallet] as const;

/**
 * Transform API response to UI-friendly model
 */
function transformUserStats(data: UserStatsResponse): UserMiningStats {
  return {
    wallet: data.wallet,
    balance: data.balance,
    balanceRaw: data.balance_raw,
    rank: data.rank,
    pendingReward: data.pending_reward_estimate,
    poolSharePercent: data.pool_share_percent ?? 0,
    isNewHolder: data.is_new_holder ?? false,
  };
}

/**
 * Hook to fetch user mining statistics
 * @param wallet - Wallet address to fetch stats for
 */
export function useUserStats(wallet: string | null) {
  const query = useQuery<UserStatsResponse, Error>({
    queryKey: userStatsQueryKey(wallet || ''),
    queryFn: () => getUserStats(wallet!),
    enabled: !!wallet, // Only run if wallet is provided
    staleTime: 0, // Always consider stale, refetch on mount
    refetchOnMount: 'always', // Force refetch every mount
    refetchOnWindowFocus: true, // Refetch when user returns to tab
  });

  // Transform data for UI consumption
  const data = useMemo(() => {
    if (!query.data) return null;
    return transformUserStats(query.data);
  }, [query.data]);

  return {
    ...query,
    data,
    rawData: query.data,
  };
}

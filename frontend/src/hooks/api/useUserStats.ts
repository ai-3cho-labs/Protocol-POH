'use client';

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { getUserStats } from '@/lib/api';
import { calculateTierProgress } from '@/lib/utils';
import type { UserStatsResponse } from '@/types/api';
import type { UserMiningStats } from '@/types/models';

/** Query key factory for user stats */
export const userStatsQueryKey = (wallet: string) => ['userStats', wallet] as const;

/**
 * Transform API response to UI-friendly model
 */
function transformUserStats(data: UserStatsResponse): UserMiningStats {
  const streakDays = data.streak_hours / 24;
  const progressToNextTier = calculateTierProgress(
    data.tier.tier,
    data.streak_hours
  );

  return {
    wallet: data.wallet,
    balance: data.balance,
    balanceRaw: data.balance_raw,
    twab: data.twab,
    tier: data.tier,
    multiplier: data.multiplier,
    hashPower: data.hash_power,
    streakHours: data.streak_hours,
    streakDays,
    streakStart: data.streak_start ? new Date(data.streak_start) : null,
    nextTier: data.next_tier,
    hoursToNextTier: data.hours_to_next_tier,
    progressToNextTier,
    rank: data.rank,
    pendingReward: data.pending_reward_estimate,
    isNewHolder: data.is_new_holder ?? false,
    isProjected: data.is_projected ?? false,
    poolSharePercent: data.pool_share_percent ?? 0,
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
    staleTime: 5 * 60 * 1000, // 5 minutes - refetch periodically for tier updates
    refetchOnMount: true, // Always fetch fresh data on mount
    refetchOnWindowFocus: false, // WebSocket handles focus updates
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

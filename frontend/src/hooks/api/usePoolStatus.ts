'use client';

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { getPoolStatus } from '@/lib/api';
import type { PoolStatusResponse } from '@/types/api';
import type { PoolInfo } from '@/types/models';

/** Query key for pool status */
export const POOL_STATUS_QUERY_KEY = ['poolStatus'] as const;

/**
 * Transform API response to UI-friendly model
 */
function transformPoolStatus(data: PoolStatusResponse): PoolInfo {
  return {
    balance: data.balance,
    balanceRaw: data.balance_raw,
    valueUsd: data.value_usd,
    goldPriceUsd: data.gold_price_usd,
    lastPayout: data.last_distribution
      ? new Date(data.last_distribution)
      : null,
    hoursSinceLast: data.hours_since_last,
    readyToDistribute: data.ready_to_distribute,
  };
}

/**
 * Hook to fetch airdrop pool status
 */
export function usePoolStatus() {
  const query = useQuery<PoolStatusResponse, Error>({
    queryKey: POOL_STATUS_QUERY_KEY,
    queryFn: getPoolStatus,
    staleTime: 0, // Always refetch for fresh data
    refetchOnMount: 'always', // Force refetch every mount
    refetchOnWindowFocus: true, // Refetch when user returns
  });

  // Transform data for UI consumption
  const data = useMemo(() => {
    if (!query.data) return null;
    return transformPoolStatus(query.data);
  }, [query.data]);

  return {
    ...query,
    data,
    rawData: query.data,
  };
}

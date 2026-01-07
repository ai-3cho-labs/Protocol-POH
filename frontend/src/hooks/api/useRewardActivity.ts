'use client';

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import { getBuybacks } from '@/lib/api';
import { formatTimeAgo } from '@/lib/utils';
import type { BuybackItem } from '@/types/api';
import type { FormattedRewardActivity } from '@/types/models';

/** Query key factory for reward activity */
export const rewardActivityQueryKey = (limit: number) =>
  ['reward-activity', limit] as const;

/**
 * Transform activity item to UI-friendly format
 */
function transformActivity(item: BuybackItem): FormattedRewardActivity {
  const executedAt = new Date(item.executed_at);
  return {
    txSignature: item.tx_signature,
    solAmount: item.sol_amount,
    copperAmount: item.copper_amount,
    pricePerToken: item.price_per_token,
    executedAt,
    timeAgo: formatTimeAgo(executedAt),
  };
}

/**
 * Hook to fetch recent reward activity
 * @param limit - Number of items to fetch (default: 10)
 */
export function useRewardActivity(limit = 10) {
  const query = useQuery<BuybackItem[], Error>({
    queryKey: rewardActivityQueryKey(limit),
    queryFn: () => getBuybacks(limit),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // 1 minute
  });

  // Transform data for UI consumption
  const data = useMemo(() => {
    if (!query.data) return null;
    return query.data.map(transformActivity);
  }, [query.data]);

  return {
    ...query,
    data,
    rawData: query.data,
  };
}

'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import { cn } from '@/lib/cn';
import { formatTimeAgo } from '@/lib/utils';
import { useWalletAddress } from '@/hooks/useWallet';
import {
  useUserStats,
  usePoolStatus,
  useLeaderboard,
  useUserHistory,
} from '@/hooks/api';
import { MiningCard } from './MiningCard';
import { TierProgress } from './TierProgress';
import { PendingRewards } from './PendingRewards';
import { MiniLeaderboard } from './MiniLeaderboard';
import { RewardHistory } from './RewardHistory';
import type { RewardHistoryItem } from './RewardHistory';

interface DetailsModalProps {
  open: boolean;
  onClose: () => void;
}

type TabId = 'overview' | 'leaderboard' | 'history' | 'pool';

const TABS: { id: TabId; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'leaderboard', label: 'Leaderboard' },
  { id: 'history', label: 'History' },
  { id: 'pool', label: 'Pool' },
];

/**
 * Full-screen modal with detailed mining stats.
 * Desktop: centered modal with terminal styling
 * Mobile: full-screen slide-up sheet
 */
export function DetailsModal({ open, onClose }: DetailsModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const wallet = useWalletAddress();

  // Fetch all data
  const { data: stats, isLoading: statsLoading } = useUserStats(wallet);
  const { data: pool, isLoading: poolLoading } = usePoolStatus();
  const { data: leaderboard, isLoading: leaderboardLoading } = useLeaderboard(25, wallet);
  const { data: rawHistory, isLoading: historyLoading } = useUserHistory(wallet, 20);

  // Transform history data to RewardHistoryItem format
  const history: RewardHistoryItem[] | null = useMemo(() => {
    if (!rawHistory) return null;
    return rawHistory.map((item) => ({
      id: item.distribution_id,
      amount: item.amount_received,
      hashPower: item.hash_power,
      sharePercent: 0, // Not provided by API
      paidAt: new Date(item.executed_at),
      timeAgo: formatTimeAgo(item.executed_at),
      txSignature: item.tx_signature ?? undefined,
    }));
  }, [rawHistory]);

  // Handle escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  // Bind escape key and prevent body scroll
  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [open, handleKeyDown]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div
        className={cn(
          'absolute bg-bg-dark border border-gray-800 overflow-hidden flex flex-col',
          // Mobile: full-screen from bottom
          'inset-x-0 bottom-0 top-16 rounded-t-2xl',
          // Desktop: centered modal (reset mobile positioning)
          'lg:inset-auto lg:top-1/2 lg:left-1/2 lg:-translate-x-1/2 lg:-translate-y-1/2',
          'lg:w-full lg:max-w-2xl lg:h-[80vh] lg:rounded-lg'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <h2 className="text-lg font-mono text-white">Mining Details</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white transition-colors"
            aria-label="Close"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-800 px-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'px-4 py-2 text-sm font-mono transition-colors relative',
                activeTab === tab.id
                  ? 'text-white'
                  : 'text-gray-500 hover:text-gray-300'
              )}
            >
              {tab.label}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-white" />
              )}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <MiningCard data={stats ?? null} isLoading={statsLoading} />
              {stats && (
                <TierProgress
                  tier={stats.tier}
                  nextTier={stats.nextTier}
                  streakHours={stats.streakHours}
                  progress={stats.progressToNextTier}
                  hoursToNextTier={stats.hoursToNextTier}
                  isLoading={statsLoading}
                  showAllTiers
                />
              )}
            </div>
          )}

          {activeTab === 'leaderboard' && (
            <MiniLeaderboard
              entries={leaderboard ?? null}
              userRank={stats?.rank}
              userWallet={wallet}
              isLoading={leaderboardLoading}
              showViewAll={false}
              limit={25}
            />
          )}

          {activeTab === 'history' && (
            <RewardHistory
              history={history ?? null}
              isLoading={historyLoading}
              showViewAll={false}
              limit={20}
            />
          )}

          {activeTab === 'pool' && (
            <PendingRewards
              pendingReward={stats?.pendingReward ?? 0}
              pool={pool ?? null}
              isLoading={poolLoading || statsLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
}

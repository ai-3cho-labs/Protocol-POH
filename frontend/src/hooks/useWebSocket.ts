'use client';

/**
 * WebSocket hook for real-time updates
 *
 * Always connects for global stats (pool, distributions, leaderboard).
 * Subscribes to wallet-specific events when wallet is connected.
 * Updates React Query cache on WebSocket events.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWalletAddress, useIsConnected } from './useWallet';
import {
  getSocket,
  disconnectSocket,
  subscribeToWallet,
  unsubscribeFromWallet,
  subscribeToGlobal,
  type DistributionExecutedPayload,
  type PoolUpdatedPayload,
} from '@/lib/socket';
import {
  POOL_STATUS_QUERY_KEY,
  userStatsQueryKey,
} from './api';

// ============================================================================
// Types
// ============================================================================

export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

export interface UseWebSocketReturn {
  status: ConnectionStatus;
  forceReconnect: () => void;
}

// ============================================================================
// Helpers
// ============================================================================

/**
 * Check if running in browser (not SSR)
 */
function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

// ============================================================================
// Hook Implementation
// ============================================================================

export function useWebSocket(): UseWebSocketReturn {
  const queryClient = useQueryClient();
  const walletAddress = useWalletAddress();
  const isWalletConnected = useIsConnected();
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');

  // Use refs to avoid stale closures in event handlers
  const walletAddressRef = useRef<string | null>(walletAddress);
  const subscribedWalletRef = useRef<string | null>(null);

  // Keep ref in sync with current wallet address
  useEffect(() => {
    walletAddressRef.current = walletAddress;
  }, [walletAddress]);

  // ========================================================================
  // Event Handlers
  // ========================================================================

  /**
   * Handle pool:updated - update cache directly
   */
  const handlePoolUpdated = useCallback(
    (payload: PoolUpdatedPayload) => {
      queryClient.setQueryData(POOL_STATUS_QUERY_KEY, (old: unknown) => {
        if (!old) return old;
        return {
          ...(old as object),
          balance: payload.balance,
          value_usd: payload.value_usd,
          ready_to_distribute: payload.ready_to_distribute,
        };
      });
    },
    [queryClient]
  );

  /**
   * Handle distribution:executed - invalidate queries and show toast
   */
  const handleDistributionExecuted = useCallback(
    (payload: DistributionExecutedPayload) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: POOL_STATUS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ['distributions'] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
      queryClient.invalidateQueries({ queryKey: ['globalStats'] });

      // Invalidate user stats if wallet is connected (use ref for fresh value)
      const currentWallet = walletAddressRef.current;
      if (currentWallet) {
        queryClient.invalidateQueries({
          queryKey: userStatsQueryKey(currentWallet),
        });
      }

      // Log for now - could trigger a toast/modal in SocketProvider
      console.log(
        '[WebSocket] Distribution executed:',
        payload.recipient_count,
        'recipients'
      );
    },
    [queryClient]
  );

  /**
   * Handle leaderboard:updated - signal only, refetch
   */
  const handleLeaderboardUpdated = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
  }, [queryClient]);

  /**
   * Handle snapshot:taken - invalidate user stats
   */
  const handleSnapshotTaken = useCallback(() => {
    const currentWallet = walletAddressRef.current;
    if (currentWallet) {
      queryClient.invalidateQueries({
        queryKey: userStatsQueryKey(currentWallet),
      });
    }
    queryClient.invalidateQueries({ queryKey: ['globalStats'] });
  }, [queryClient]);

  // ========================================================================
  // Force Reconnect
  // ========================================================================

  const forceReconnect = useCallback(() => {
    if (!isBrowser()) return;

    try {
      const socket = getSocket();
      if (socket.connected) {
        socket.disconnect();
      }
      setStatus('connecting');
      socket.connect();
    } catch {
      // getSocket throws during SSR
    }
  }, []);

  // ========================================================================
  // Main Connection Effect (Always connects for global stats)
  // ========================================================================

  useEffect(() => {
    // Don't run during SSR
    if (!isBrowser()) return;

    let socket: ReturnType<typeof getSocket>;
    try {
      socket = getSocket();
    } catch {
      // getSocket throws during SSR
      return;
    }

    // Connection handlers
    const onConnect = () => {
      setStatus('connected');
      // Always subscribe to global updates (pool, distributions, leaderboard)
      subscribeToGlobal();
      // Subscribe to wallet room if wallet is connected
      const currentWallet = walletAddressRef.current;
      if (currentWallet) {
        subscribeToWallet(currentWallet);
        subscribedWalletRef.current = currentWallet;
      }
      console.log('[WebSocket] Connected (global stats)');
    };

    const onDisconnect = () => {
      setStatus('disconnected');
      console.log('[WebSocket] Disconnected');
    };

    const onConnectError = (error: Error) => {
      setStatus('disconnected');
      console.warn('[WebSocket] Connection error:', error.message);
    };

    const onReconnect = () => {
      console.log('[WebSocket] Reconnected');
      // Resubscribe to global updates
      subscribeToGlobal();
      // Resubscribe to wallet room if connected (use ref for fresh value)
      const currentWallet = walletAddressRef.current;
      if (currentWallet) {
        subscribeToWallet(currentWallet);
        // Invalidate user stats to fetch fresh data (may have missed events)
        queryClient.invalidateQueries({
          queryKey: userStatsQueryKey(currentWallet),
        });
      }
    };

    // Register event handlers
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('connect_error', onConnectError);
    socket.io.on('reconnect', onReconnect);

    // Register event listeners
    socket.on('pool:updated', handlePoolUpdated);
    socket.on('distribution:executed', handleDistributionExecuted);
    socket.on('leaderboard:updated', handleLeaderboardUpdated);
    socket.on('snapshot:taken', handleSnapshotTaken);

    // Connect immediately for global stats
    setStatus('connecting');
    socket.connect();

    // Cleanup
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('connect_error', onConnectError);
      socket.io.off('reconnect', onReconnect);

      socket.off('pool:updated', handlePoolUpdated);
      socket.off('distribution:executed', handleDistributionExecuted);
      socket.off('leaderboard:updated', handleLeaderboardUpdated);
      socket.off('snapshot:taken', handleSnapshotTaken);

      disconnectSocket();
    };
  }, [
    queryClient,
    handlePoolUpdated,
    handleDistributionExecuted,
    handleLeaderboardUpdated,
    handleSnapshotTaken,
  ]);

  // ========================================================================
  // Wallet Subscription Effect (Subscribe/unsubscribe on wallet change)
  // ========================================================================

  useEffect(() => {
    if (!isBrowser()) return;

    let socket: ReturnType<typeof getSocket>;
    try {
      socket = getSocket();
    } catch {
      return;
    }

    // Only manage subscriptions if socket is connected
    if (!socket.connected) return;

    const previousWallet = subscribedWalletRef.current;

    // Unsubscribe from previous wallet if different
    if (previousWallet && previousWallet !== walletAddress) {
      unsubscribeFromWallet(previousWallet);
      subscribedWalletRef.current = null;
    }

    // Subscribe to new wallet if connected
    if (isWalletConnected && walletAddress && walletAddress !== previousWallet) {
      subscribeToWallet(walletAddress);
      subscribedWalletRef.current = walletAddress;
      console.log('[WebSocket] Subscribed to wallet:', walletAddress);
    }

    // Unsubscribe if wallet disconnected
    if (!isWalletConnected && previousWallet) {
      unsubscribeFromWallet(previousWallet);
      subscribedWalletRef.current = null;
      console.log('[WebSocket] Unsubscribed from wallet');
    }
  }, [isWalletConnected, walletAddress]);

  return { status, forceReconnect };
}

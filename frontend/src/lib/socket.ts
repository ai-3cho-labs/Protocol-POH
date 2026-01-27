/**
 * Socket.IO Client
 * Real-time WebSocket connection management.
 */

import { io, Socket } from 'socket.io-client';
import { WS_URL, API_KEY } from './constants';

// ===========================================
// Types
// ===========================================

export interface SocketEvents {
  connect: () => void;
  disconnect: (reason: string) => void;
  connect_error: (error: Error) => void;
  distribution: (data: DistributionEvent) => void;
  balance_update: (data: BalanceUpdateEvent) => void;
  pool_update: (data: PoolUpdateEvent) => void;
}

export interface DistributionEvent {
  distribution_id: string;
  pool_amount: number;
  recipient_count: number;
  trigger_type: 'threshold' | 'time';
  executed_at: string;
}

export interface BalanceUpdateEvent {
  wallet: string;
  balance: number;
  twab: number;
  hash_power: number;
}

export interface PoolUpdateEvent {
  balance: number;
  value_usd: number;
  threshold_met: boolean;
}

// WebSocket payload types used by useWebSocket hook
export interface PoolUpdatedPayload {
  balance: number;
  value_usd: number;
  progress_to_threshold: number;
  threshold_met: boolean;
  hours_until_time_trigger: number | null;
}

export interface DistributionExecutedPayload {
  distribution_id: string;
  pool_amount: number;
  recipient_count: number;
  trigger_type: 'threshold' | 'time';
  executed_at: string;
}

export interface TierChangedPayload {
  wallet: string;
  old_tier: number;
  new_tier: number;
}

export interface SellDetectedPayload {
  wallet: string;
  amount: number;
}

// ===========================================
// Socket Instance
// ===========================================

let socket: Socket | null = null;

/**
 * Get or create the socket connection
 */
export function getSocket(): Socket {
  if (!socket) {
    // Connect to WebSocket server
    // Backend mounts Socket.IO at /ws with socketio_path=""
    // Uses default namespace / (no namespace needed in URL)
    socket = io(WS_URL, {
      path: '/ws/', // Path where Socket.IO is mounted
      autoConnect: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      transports: ['websocket', 'polling'],
      // Include API key in auth for authenticated connections
      auth: API_KEY ? { apiKey: API_KEY } : undefined,
    });
  }
  return socket;
}

/**
 * Connect the socket
 */
export function connectSocket(): void {
  const s = getSocket();
  if (!s.connected) {
    s.connect();
  }
}

/**
 * Disconnect the socket
 */
export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}

/**
 * Check if socket is connected
 */
export function isSocketConnected(): boolean {
  return socket?.connected ?? false;
}

// ===========================================
// Subscription Management
// ===========================================

/**
 * Subscribe to wallet-specific updates
 */
export function subscribeToWallet(wallet: string): void {
  const s = getSocket();
  if (s.connected) {
    s.emit('subscribe_wallet', { wallet });
  }
}

/**
 * Unsubscribe from wallet-specific updates
 */
export function unsubscribeFromWallet(wallet: string): void {
  const s = getSocket();
  if (s.connected) {
    s.emit('unsubscribe_wallet', { wallet });
  }
}

/**
 * Subscribe to global updates (distributions, pool status)
 */
export function subscribeToGlobal(): void {
  const s = getSocket();
  if (s.connected) {
    s.emit('subscribe_global');
  }
}

/**
 * Unsubscribe from global updates
 */
export function unsubscribeFromGlobal(): void {
  const s = getSocket();
  if (s.connected) {
    s.emit('unsubscribe_global');
  }
}

// ===========================================
// Event Listeners
// ===========================================

/**
 * Add an event listener
 */
export function onSocketEvent<K extends keyof SocketEvents>(
  event: K,
  callback: SocketEvents[K]
): void {
  const s = getSocket();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  s.on(event, callback as any);
}

/**
 * Remove an event listener
 */
export function offSocketEvent<K extends keyof SocketEvents>(
  event: K,
  callback?: SocketEvents[K]
): void {
  const s = getSocket();
  if (callback) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    s.off(event, callback as any);
  } else {
    s.off(event);
  }
}

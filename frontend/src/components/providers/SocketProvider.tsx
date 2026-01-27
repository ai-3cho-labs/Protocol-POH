'use client';

/**
 * Socket Provider
 *
 * Provides WebSocket connection status to the application.
 * Must be placed inside AddressProvider to access address state.
 */

import { createContext, useContext, FC, ReactNode } from 'react';
import { useWebSocket, type ConnectionStatus } from '@/hooks/useWebSocket';

// ============================================================================
// Context
// ============================================================================

interface SocketContextValue {
  /** Current connection status */
  status: ConnectionStatus;
  /** Force a reconnection attempt */
  forceReconnect: () => void;
}

const SocketContext = createContext<SocketContextValue>({
  status: 'disconnected',
  forceReconnect: () => {},
});

/**
 * Hook to access socket connection status
 */
export const useSocketContext = () => useContext(SocketContext);

// ============================================================================
// Provider
// ============================================================================

interface SocketProviderProps {
  children: ReactNode;
}

/**
 * Socket Provider Component
 *
 * Initializes WebSocket connection when address is set.
 * Provides connection status to descendant components.
 */
export const SocketProvider: FC<SocketProviderProps> = ({ children }) => {
  const { status, forceReconnect } = useWebSocket();

  return (
    <SocketContext.Provider value={{ status, forceReconnect }}>
      {children}
    </SocketContext.Provider>
  );
};

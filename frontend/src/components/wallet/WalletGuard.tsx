'use client';

import { useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useWallet } from '@/hooks/useWallet';
import { LoadingPage } from '@/components/ui/LoadingSpinner';
import { TerminalCard } from '@/components/ui/TerminalCard';
import { AddressInput } from './AddressInput';
import { isValidRedirectPath } from '@/lib/validators';

export interface WalletGuardProps {
  /** Children to render when wallet is connected */
  children: ReactNode;
  /** Redirect path when not connected (if set, redirects instead of showing message) */
  redirectTo?: string;
  /** Custom loading component */
  loadingComponent?: ReactNode;
  /** Custom not connected component */
  notConnectedComponent?: ReactNode;
}

/**
 * Wallet guard component
 * Protects routes that require a wallet address
 */
export function WalletGuard({
  children,
  redirectTo,
  loadingComponent,
  notConnectedComponent,
}: WalletGuardProps) {
  const router = useRouter();
  const { connected } = useWallet();

  // Handle redirect when not connected
  useEffect(() => {
    if (!connected && redirectTo && isValidRedirectPath(redirectTo)) {
      router.push(redirectTo);
    }
  }, [connected, redirectTo, router]);

  // Not connected - show message or redirect
  if (!connected) {
    // If redirect is set, show loading while redirecting
    if (redirectTo) {
      return (
        <>
          {loadingComponent || <LoadingPage text="Redirecting..." />}
        </>
      );
    }

    // Show not connected message
    return (
      <>
        {notConnectedComponent || <WalletNotConnected />}
      </>
    );
  }

  // Connected - render children
  return <>{children}</>;
}

/**
 * Default not connected component
 */
function WalletNotConnected() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center p-4">
      <TerminalCard
        title="Wallet Required"
        className="max-w-md w-full"
      >
        <div className="text-center py-6">
          {/* Title */}
          <h2 className="text-xl font-semibold text-zinc-200 mb-2">
            Enter Your Wallet Address
          </h2>

          {/* Description */}
          <p className="text-sm text-zinc-400 mb-6">
            Paste your Solana wallet address to view your mining dashboard and
            rewards. No wallet connection required.
          </p>

          {/* Address input */}
          <div className="max-w-sm mx-auto">
            <AddressInput size="lg" fullWidth />
          </div>

          {/* Security note */}
          <p className="text-xs text-zinc-500 mt-4">
            Your address is stored locally. No signing or permissions needed.
          </p>
        </div>
      </TerminalCard>
    </div>
  );
}

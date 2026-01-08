'use client';

import { useState } from 'react';
import { PageContainer } from '@/components/layout';
import { WalletGuard } from '@/components/wallet/WalletGuard';
import { ConnectWalletEmpty } from '@/components/ui';
import { MinerDisplay, DetailsModal } from '@/components/dashboard';

export default function DashboardPage() {
  return (
    <PageContainer>
      <WalletGuard
        notConnectedComponent={
          <div className="flex items-center justify-center min-h-[60vh]">
            <ConnectWalletEmpty />
          </div>
        }
      >
        <DashboardContent />
      </WalletGuard>
    </PageContainer>
  );
}

function DashboardContent() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <MinerDisplay onViewDetails={() => setModalOpen(true)} />
      <DetailsModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </>
  );
}

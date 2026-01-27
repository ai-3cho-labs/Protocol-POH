'use client';

import { PageContainer } from '@/components/layout/PageContainer';
import { Hero, LiveStatsBar, HowItWorks, TierExplainer, Roadmap, Footer, WebGLBackground } from '@/components/landing';
import { useGlobalStats, usePoolStatus } from '@/hooks/api';

export default function HomePage() {
  const globalStats = useGlobalStats();
  const poolStatus = usePoolStatus();

  return (
    <PageContainer>
      {/* WebGL Background (landing page only) */}
      <WebGLBackground />

      {/* Hero Section */}
      <Hero />

      {/* Live Stats Ticker */}
      <LiveStatsBar
        holders={globalStats.data?.total_holders ?? 0}
        totalDistributed={globalStats.data?.total_distributed ?? 0}
        poolValueUsd={poolStatus.data?.valueUsd ?? 0}
        poolBalance={poolStatus.data?.balance ?? 0}
        hoursUntilNext={poolStatus.data?.hoursUntilTrigger ?? null}
        isLoading={globalStats.isLoading || poolStatus.isLoading}
      />

      {/* How It Works */}
      <HowItWorks />

      {/* Tier System */}
      <TierExplainer />

      {/* Roadmap */}
      <Roadmap />

      {/* Footer */}
      <Footer />
    </PageContainer>
  );
}

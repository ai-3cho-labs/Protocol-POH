'use client';

import { PageContainer } from '@/components/layout';
import { TerminalCard } from '@/components/ui';
import { cn } from '@/lib/cn';

export default function DocsPage() {
  return (
    <PageContainer>
      <div className="space-y-8 max-w-4xl mx-auto">
        {/* Header */}
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-zinc-100 lg:font-mono">
            <span className="hidden lg:inline text-gray-500">&gt; </span>
            DOCUMENTATION
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            Everything you need to know about POH → $GOLD rewards
          </p>
        </div>

        {/* Table of Contents */}
        <TerminalCard title="CONTENTS">
          <nav className="space-y-2 text-sm">
            <TOCLink href="#overview" number="01">
              Overview
            </TOCLink>
            <TOCLink href="#how-it-works" number="02">
              How It Works
            </TOCLink>
            <TOCLink href="#distribution" number="03">
              Distribution Formula
            </TOCLink>
            <TOCLink href="#payouts" number="04">
              Payouts
            </TOCLink>
            <TOCLink href="#faq" number="05">
              FAQ
            </TOCLink>
            <TOCLink href="#roadmap" number="06">
              Roadmap
            </TOCLink>
          </nav>
        </TerminalCard>

        {/* Overview */}
        <Section id="overview" title="01. OVERVIEW">
          <p>
            POH is a Solana token where you earn $GOLD rewards through holding.
            Simply hold POH tokens in your wallet to receive proportional rewards.
          </p>
          <p>
            Revenue flows into the $GOLD reward pool, which is distributed to POH holders
            based on their balance.
          </p>
          <Highlight>
            Your Share = Your Balance / Total Supply
          </Highlight>
        </Section>

        {/* How It Works */}
        <Section id="how-it-works" title="02. HOW IT WORKS">
          <ol className="space-y-4 list-decimal list-inside">
            <li>
              <strong className="text-zinc-200">Buy & Hold POH</strong> - Purchase POH
              tokens and hold them in your wallet. No staking required.
            </li>
            <li>
              <strong className="text-zinc-200">Earn Proportional Rewards</strong> - Your
              share of each distribution is based on your current balance.
            </li>
            <li>
              <strong className="text-zinc-200">Receive $GOLD Automatically</strong> - When
              the reward pool has balance, $GOLD rewards are sent directly to your wallet.
            </li>
          </ol>
        </Section>

        {/* Distribution Formula */}
        <Section id="distribution" title="03. DISTRIBUTION FORMULA">
          <p>
            Each distribution divides the reward pool proportionally among all eligible
            holders based on their current balance at distribution time.
          </p>
          <CodeBlock>
            {`Your Reward = Pool Amount × (Your Balance / Total Supply)

Example:
- Pool: 100,000 $GOLD
- Your Balance: 100,000 POH
- Total Supply: 10,000,000 POH
- Your Reward: 100,000 × (100,000 / 10,000,000) = 1,000 $GOLD`}
          </CodeBlock>
          <p className="text-sm text-zinc-500">
            Excluded wallets (like liquidity pools and team wallets) are not counted
            in the total supply calculation.
          </p>
        </Section>

        {/* Payouts */}
        <Section id="payouts" title="04. PAYOUTS">
          <p>$GOLD rewards are distributed hourly whenever the pool has a balance:</p>
          <ul className="space-y-2 list-disc list-inside">
            <li>
              <strong className="text-white">Automatic:</strong> No threshold required -
              distributions happen when there are rewards to distribute
            </li>
            <li>
              <strong className="text-white">Hourly:</strong> Checked every hour
            </li>
            <li>
              <strong className="text-white">Direct:</strong> $GOLD sent directly to your wallet
            </li>
          </ul>
          <p className="mt-4">
            $GOLD rewards are automatically sent to your wallet. Note: $GOLD is a separate
            token from POH - you hold POH to earn, and receive $GOLD as rewards.
          </p>
        </Section>

        {/* FAQ */}
        <Section id="faq" title="05. FAQ">
          <div className="space-y-6">
            <FAQ question="Do I need to stake my POH tokens?">
              No! Just hold them in your wallet. There&apos;s no staking contract
              or lock-up period.
            </FAQ>
            <FAQ question="What happens if I buy more POH?">
              Your share of the next distribution increases proportionally to your
              new balance. There&apos;s no waiting period.
            </FAQ>
            <FAQ question="What happens if I sell some POH?">
              Your share of future distributions decreases proportionally. There
              are no penalties for selling.
            </FAQ>
            <FAQ question="Which wallets are excluded?">
              Creator wallets, liquidity pool addresses, CEX deposit addresses,
              and system wallets are excluded from rewards.
            </FAQ>
            <FAQ question="Where do the $GOLD rewards come from?">
              Revenue from trading fees and other sources flows into the $GOLD
              reward pool for distribution.
            </FAQ>
            <FAQ question="What&apos;s the difference between POH and $GOLD?">
              POH is what you buy and hold - it determines your reward share.
              $GOLD is what you earn as rewards - it&apos;s distributed from the pool
              based on your POH balance.
            </FAQ>
            <FAQ question="How can I see my distribution history?">
              Connect your wallet and visit the History page to see all past
              distributions you&apos;ve received.
            </FAQ>
          </div>
        </Section>

        {/* Roadmap */}
        <Section id="roadmap" title="06. ROADMAP">
          <div className="space-y-6">
            <RoadmapPhase
              phase="V1"
              title="Reward Distribution"
              status="live"
              items={[
                'Hold POH tokens to earn $GOLD rewards',
                'Simple balance-based distribution',
                'Automatic hourly distributions',
                'Real-time dashboard and reward tracking',
              ]}
            />
            <RoadmapPhase
              phase="V2"
              title="Enhanced Features"
              status="upcoming"
              items={[
                'Additional reward mechanisms',
                'Advanced analytics dashboard',
                'Historical data export',
                'Mobile app support',
              ]}
            />
            <RoadmapPhase
              phase="V3"
              title="Expansion"
              status="planned"
              items={[
                'Governance for POH holders',
                'Cross-chain expansion',
                'Additional token integrations',
                'Community features',
              ]}
            />
          </div>
        </Section>
      </div>
    </PageContainer>
  );
}

function TOCLink({
  href,
  number,
  children,
}: {
  href: string;
  number: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      className={cn(
        'flex items-center gap-3 py-1.5 px-2 -mx-2 rounded',
        'hover:bg-zinc-800/50 transition-colors',
        'text-zinc-300 hover:text-white'
      )}
    >
      <span className="text-gray-500 font-mono text-xs">{number}</span>
      <span>{children}</span>
    </a>
  );
}

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24">
      <TerminalCard title={title}>
        <div className="space-y-4 text-zinc-400">{children}</div>
      </TerminalCard>
    </section>
  );
}

function Highlight({ children }: { children: React.ReactNode }) {
  return (
    <div className="p-4 bg-white/10 border border-white/30 rounded font-mono text-white text-center">
      {children}
    </div>
  );
}

function CodeBlock({ children }: { children: string }) {
  return (
    <pre className="p-4 bg-terminal-bg border border-terminal-border rounded overflow-x-auto">
      <code className="text-sm font-mono text-zinc-300">{children}</code>
    </pre>
  );
}

function FAQ({
  question,
  children,
}: {
  question: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="text-zinc-200 font-medium mb-2 lg:font-mono">{question}</h3>
      <p className="text-sm text-zinc-400">{children}</p>
    </div>
  );
}

function RoadmapPhase({
  phase,
  title,
  status,
  items,
}: {
  phase: string;
  title: string;
  status: 'live' | 'upcoming' | 'planned';
  items: string[];
}) {
  const statusStyles = {
    live: 'bg-green-500/20 text-green-400 border-green-500/30',
    upcoming: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    planned: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  };

  const statusLabels = {
    live: 'LIVE',
    upcoming: 'COMING SOON',
    planned: 'PLANNED',
  };

  return (
    <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-white">{phase}</span>
          <span className="text-zinc-300 font-medium">{title}</span>
        </div>
        <span className={cn(
          'px-2 py-0.5 text-xs font-medium rounded border',
          statusStyles[status]
        )}>
          {statusLabels[status]}
        </span>
      </div>
      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2 text-sm text-zinc-400">
            <span className="text-zinc-600 mt-0.5">→</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

'use client';

import { cn } from '@/lib/cn';
import { Card } from '@/components/ui';

export interface RoadmapProps {
  /** Additional class names */
  className?: string;
}

interface Phase {
  id: string;
  title: string;
  status: 'live' | 'upcoming' | 'planned';
  items: string[];
}

const PHASES: Phase[] = [
  {
    id: 'V1',
    title: 'Mining Protocol',
    status: 'live',
    items: [
      'Hold CPU tokens to mine $GOLD rewards',
      'Tier system with up to 5x multiplier',
      'Automatic distributions every 24h or $250 threshold',
      'Real-time dashboard and reward tracking',
    ],
  },
  {
    id: 'V2',
    title: 'Algo Trading Bot',
    status: 'upcoming',
    items: [
      'Automated trading bot for precious metals (Gold, Silver)',
      'AI-powered algorithmic trading strategies',
      'CPU holders receive % of trading profits',
      'Profits distributed proportionally based on holdings',
    ],
  },
  {
    id: 'V3',
    title: 'Expansion',
    status: 'planned',
    items: [
      'Additional metal markets and trading pairs',
      'Advanced analytics dashboard',
      'Governance for CPU holders',
      'Cross-chain expansion',
    ],
  },
];

const STATUS_CONFIG = {
  live: {
    label: 'LIVE',
    className: 'bg-green-500/20 text-green-400 border-green-500/30',
    dotClassName: 'bg-green-400',
  },
  upcoming: {
    label: 'COMING SOON',
    className: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    dotClassName: 'bg-amber-400',
  },
  planned: {
    label: 'PLANNED',
    className: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
    dotClassName: 'bg-zinc-400',
  },
};

/**
 * Roadmap - Project roadmap with phases
 */
export function Roadmap({ className }: RoadmapProps) {
  return (
    <section id="roadmap" className={cn('py-12 lg:py-20', className)}>
      <div className="max-w-4xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-10">
          <h2 className="text-2xl lg:text-3xl font-bold text-text-primary mb-4 tracking-tight">
            ROADMAP
          </h2>
          <p className="text-body text-text-secondary max-w-lg mx-auto">
            From mining rewards to algorithmic trading. CPU holders benefit at every phase.
          </p>
        </div>

        {/* Desktop: Timeline */}
        <div className="hidden lg:block">
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-8 top-0 bottom-0 w-px bg-border" />

            <div className="space-y-6">
              {PHASES.map((phase, index) => (
                <PhaseCard key={phase.id} phase={phase} index={index} />
              ))}
            </div>
          </div>
        </div>

        {/* Mobile: Stack */}
        <div className="lg:hidden space-y-4">
          {PHASES.map((phase) => (
            <PhaseCardMobile key={phase.id} phase={phase} />
          ))}
        </div>
      </div>
    </section>
  );
}

function PhaseCard({ phase, index }: { phase: Phase; index: number }) {
  const status = STATUS_CONFIG[phase.status];

  return (
    <div className="relative pl-20">
      {/* Timeline dot */}
      <div className="absolute left-6 top-6 w-4 h-4 rounded-full border-2 border-bg-dark bg-bg-card flex items-center justify-center">
        <div className={cn('w-2 h-2 rounded-full', status.dotClassName)} />
      </div>

      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-white">{phase.id}</span>
            <span className="text-lg text-zinc-300 font-medium">{phase.title}</span>
          </div>
          <span
            className={cn(
              'px-3 py-1 text-xs font-medium rounded-full border',
              status.className
            )}
          >
            {status.label}
          </span>
        </div>
        <ul className="space-y-2">
          {phase.items.map((item, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-zinc-400">
              <span className="text-zinc-600 mt-0.5">-&gt;</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function PhaseCardMobile({ phase }: { phase: Phase }) {
  const status = STATUS_CONFIG[phase.status];

  return (
    <div className="p-4 rounded-lg border bg-bg-card border-border">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-white">{phase.id}</span>
          <span className="text-zinc-300 font-medium">{phase.title}</span>
        </div>
        <span
          className={cn(
            'px-2 py-0.5 text-xs font-medium rounded border',
            status.className
          )}
        >
          {status.label}
        </span>
      </div>
      <ul className="space-y-1.5">
        {phase.items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-zinc-400">
            <span className="text-zinc-600 mt-0.5">-&gt;</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

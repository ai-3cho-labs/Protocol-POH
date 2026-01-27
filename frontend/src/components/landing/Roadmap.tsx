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
    glowClassName: 'shadow-[0_0_10px_rgba(34,197,94,0.3)]',
    animated: true,
  },
  upcoming: {
    label: 'COMING SOON',
    className: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    dotClassName: 'bg-amber-400',
    glowClassName: '',
    animated: true,
  },
  planned: {
    label: 'PLANNED',
    className: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
    dotClassName: 'bg-zinc-400',
    glowClassName: '',
    animated: false,
  },
};

/**
 * Roadmap - Project roadmap with phases
 * Enhanced with timeline visualization and animated status badges
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

        {/* Desktop: Enhanced Timeline */}
        <div className="hidden lg:block">
          <div className="relative">
            {/* Vertical timeline line with gradient */}
            <div className="absolute left-8 top-0 bottom-0 w-px">
              <div className="absolute inset-0 bg-gradient-to-b from-green-500/50 via-amber-500/30 to-zinc-500/20" />
            </div>

            <div className="space-y-6">
              {PHASES.map((phase, index) => (
                <PhaseCard key={phase.id} phase={phase} index={index} />
              ))}
            </div>
          </div>
        </div>

        {/* Mobile: Enhanced Stack with connecting line */}
        <div className="lg:hidden relative">
          {/* Vertical connecting line */}
          <div className="absolute left-4 top-8 bottom-8 w-px bg-gradient-to-b from-green-500/50 via-amber-500/30 to-zinc-500/20" />

          <div className="space-y-4">
            {PHASES.map((phase) => (
              <PhaseCardMobile key={phase.id} phase={phase} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function PhaseCard({ phase, index: _index }: { phase: Phase; index: number }) {
  const status = STATUS_CONFIG[phase.status];
  const isLive = phase.status === 'live';

  return (
    <div className="relative pl-20 group">
      {/* Timeline dot with animation for live status */}
      <div
        className={cn(
          'absolute left-6 top-6 w-4 h-4 rounded-full border-2 border-bg-dark flex items-center justify-center',
          'transition-all duration-300',
          isLive && 'bg-green-500/20',
          status.glowClassName
        )}
      >
        <div className={cn('w-2 h-2 rounded-full', status.dotClassName)} />
        {isLive && (
          <div className="absolute w-4 h-4 rounded-full bg-green-400/30 animate-ping" />
        )}
      </div>

      <Card
        className={cn(
          'p-5 transition-all duration-300',
          'hover:-translate-y-0.5',
          isLive && 'border-green-500/20 shadow-[0_0_30px_rgba(34,197,94,0.1)]',
          phase.status === 'upcoming' && 'hover:border-amber-500/20'
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span
              className={cn(
                'text-2xl font-bold',
                isLive ? 'text-green-400' : phase.status === 'upcoming' ? 'text-amber-400' : 'text-white'
              )}
            >
              {phase.id}
            </span>
            <span className="text-lg text-zinc-300 font-medium">{phase.title}</span>
          </div>
          <StatusBadge status={phase.status} />
        </div>
        <ul className="space-y-2">
          {phase.items.map((item, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-zinc-400">
              <span
                className={cn(
                  'mt-0.5',
                  isLive ? 'text-green-500' : 'text-zinc-600'
                )}
              >
                {isLive ? '✓' : '→'}
              </span>
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
  const isLive = phase.status === 'live';

  return (
    <div className="relative pl-10">
      {/* Timeline dot */}
      <div
        className={cn(
          'absolute left-2 top-4 w-4 h-4 rounded-full border-2 border-bg-dark flex items-center justify-center z-10',
          isLive && 'bg-green-500/20'
        )}
      >
        <div className={cn('w-2 h-2 rounded-full', status.dotClassName)} />
        {isLive && (
          <div className="absolute w-4 h-4 rounded-full bg-green-400/30 animate-ping" />
        )}
      </div>

      <div
        className={cn(
          'p-4 rounded-lg border transition-all duration-300',
          isLive
            ? 'bg-gradient-to-r from-green-500/10 via-green-500/5 to-bg-card border-green-500/20'
            : 'bg-bg-card border-border'
        )}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'text-lg font-bold',
                isLive ? 'text-green-400' : phase.status === 'upcoming' ? 'text-amber-400' : 'text-white'
              )}
            >
              {phase.id}
            </span>
            <span className="text-zinc-300 font-medium">{phase.title}</span>
          </div>
          <StatusBadge status={phase.status} compact />
        </div>
        <ul className="space-y-1.5">
          {phase.items.map((item, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-zinc-400">
              <span
                className={cn(
                  'mt-0.5',
                  isLive ? 'text-green-500' : 'text-zinc-600'
                )}
              >
                {isLive ? '✓' : '→'}
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

/**
 * Status badge with optional animation
 */
function StatusBadge({
  status,
  compact = false,
}: {
  status: Phase['status'];
  compact?: boolean;
}) {
  const config = STATUS_CONFIG[status];
  const isLive = status === 'live';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium rounded-full border',
        compact ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-xs',
        config.className
      )}
    >
      {/* Animated dot for live/upcoming */}
      {config.animated && (
        <span className="relative flex h-2 w-2">
          <span
            className={cn(
              'absolute inline-flex h-full w-full rounded-full opacity-75',
              isLive ? 'bg-green-400 animate-ping' : 'bg-amber-400 animate-pulse'
            )}
          />
          <span
            className={cn(
              'relative inline-flex rounded-full h-2 w-2',
              isLive ? 'bg-green-400' : 'bg-amber-400'
            )}
          />
        </span>
      )}
      {config.label}
    </span>
  );
}

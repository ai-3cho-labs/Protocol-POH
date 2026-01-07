'use client';

import { cn } from '@/lib/cn';
import { Card, PixelIcon } from '@/components/ui';

export interface HowItWorksProps {
  /** Additional class names */
  className?: string;
}

const STEPS = [
  {
    number: '01',
    icon: 'chest' as const,
    title: 'Hold $COPPER',
    description:
      'Buy and hold $COPPER tokens. Your time-weighted average balance (TWAB) determines your mining power.',
    highlight: 'No staking required',
  },
  {
    number: '02',
    icon: 'lightning' as const,
    title: 'Earn Hash Power',
    description:
      'Build your streak by holding without selling. Longer streaks unlock higher multipliers up to 5x.',
    highlight: 'Up to 5x multiplier',
  },
  {
    number: '03',
    icon: 'coin' as const,
    title: 'Receive Rewards',
    description:
      'Trading fees fill the reward pool. When it hits $250 or 24h passes, mining rewards are paid out.',
    highlight: 'Automatic payouts',
  },
];

/**
 * HowItWorks - 3-step explanation of the system
 */
export function HowItWorks({ className }: HowItWorksProps) {
  return (
    <section id="how-it-works" className={cn('py-12 lg:py-20', className)}>
      <div className="max-w-6xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-2xl lg:text-3xl font-bold text-text-primary mb-4">
            HOW IT WORKS
          </h2>
          <p className="text-text-secondary max-w-lg mx-auto">
            Simulated mining rewards without hardware. Your tokens work for you
            24/7.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {STEPS.map((step, index) => (
            <StepCard key={step.number} step={step} index={index} />
          ))}
        </div>

        {/* Connection lines - Desktop only */}
        <div className="hidden lg:flex justify-center mt-8">
          <div className="flex items-center gap-4 text-gray-500 text-sm font-mono">
            <span>HOLD</span>
            <span className="text-white">→</span>
            <span>EARN</span>
            <span className="text-white">→</span>
            <span>MINE</span>
            <span className="text-white">→</span>
            <span className="text-white glow-white">REPEAT</span>
          </div>
        </div>
      </div>
    </section>
  );
}

/**
 * Individual step card
 * Monochrome design
 */
function StepCard({
  step,
}: {
  step: (typeof STEPS)[0];
  index: number;
}) {
  return (
    <Card className="relative">
      {/* Step number badge */}
      <div
        className={cn(
          'absolute -top-3 left-4',
          'px-2 py-0.5 text-xs font-bold rounded',
          'bg-white text-bg-dark'
        )}
      >
        {step.number}
      </div>

      <div className="pt-4">
        {/* Icon */}
        <div className="mb-4">
          <PixelIcon name={step.icon} size="xl" variant="default" />
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          {step.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-text-secondary mb-4">{step.description}</p>

        {/* Highlight */}
        <div
          className={cn(
            'inline-flex items-center gap-1.5',
            'px-2 py-1 rounded text-xs',
            'bg-white/10 text-white'
          )}
        >
          <PixelIcon name="star" size="sm" variant="accent" />
          <span>{step.highlight}</span>
        </div>
      </div>
    </Card>
  );
}

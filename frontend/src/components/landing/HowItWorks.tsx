'use client';

import { cn } from '@/lib/cn';
import { branding } from '@/config';
import { Card, PixelIcon } from '@/components/ui';

export interface HowItWorksProps {
  /** Additional class names */
  className?: string;
}

const STEPS = [
  {
    icon: 'chest' as const,
    title: `Hold ${branding.holdToken.symbol}`,
    description: `Buy ${branding.holdToken.symbol} tokens and hold them in your wallet. Your average balance over time determines your mining power.`,
  },
  {
    icon: 'lightning' as const,
    title: 'Build Your Streak',
    description: 'The longer you hold without selling, the higher your tier. Diamond Hands (30+ days) earn 5x rewards.',
  },
  {
    icon: 'coin' as const,
    title: `Collect $${branding.rewardToken.symbol}`,
    description: `$${branding.rewardToken.symbol} rewards are distributed to all miners automatically based on your hash power.`,
  },
];

/**
 * HowItWorks - 3-step explanation of the system
 * Enhanced with step numbers and visual connections
 */
export function HowItWorks({ className }: HowItWorksProps) {
  return (
    <section id="how-it-works" className={cn('py-10 lg:py-12', className)}>
      <div className="max-w-5xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-8">
          <h2 className="text-heading-1 font-bold text-text-primary mb-2 tracking-tight">
            HOW THE MINE WORKS
          </h2>
          <p className="text-body-sm text-text-secondary max-w-md mx-auto">
            Passive mining rewards, zero hardware. Your tokens work 24/7.
          </p>
        </div>

        {/* Steps Grid with Connection Lines */}
        <div className="relative">
          {/* Desktop Connection Lines */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 -translate-y-1/2 h-px">
            <div className="max-w-3xl mx-auto px-24 flex">
              <div className="flex-1 border-t-2 border-dashed border-white/20" />
              <div className="w-24" />
              <div className="flex-1 border-t-2 border-dashed border-white/20" />
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-3 sm:gap-4 lg:gap-6 relative">
            {STEPS.map((step, index) => (
              <StepCard key={step.title} step={step} index={index} />
            ))}
          </div>
        </div>

        {/* Mobile: Vertical timeline indicator */}
        <div className="lg:hidden flex justify-center mt-4">
          <div className="flex items-center gap-2 text-text-muted text-xs">
            <span className="w-2 h-2 rounded-full bg-white/40" />
            <span className="w-8 h-px bg-white/20" />
            <span className="w-2 h-2 rounded-full bg-white/40" />
            <span className="w-8 h-px bg-white/20" />
            <span className="w-2 h-2 rounded-full bg-white" />
          </div>
        </div>

        {/* Connection flow text - Desktop only */}
        <div className="hidden lg:flex justify-center mt-6">
          <div className="flex items-center gap-3 text-gray-500 text-xs font-mono">
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
 * Individual step card with step number overlay
 * Enhanced with hover effects and visual hierarchy
 */
function StepCard({
  step,
  index,
}: {
  step: (typeof STEPS)[0];
  index: number;
}) {
  const stepNumber = String(index + 1).padStart(2, '0');

  return (
    <Card
      className={cn(
        'p-3 sm:p-4 relative overflow-hidden group',
        'transition-all duration-300',
        'hover:-translate-y-1 hover:shadow-[0_0_30px_rgba(255,255,255,0.1)]',
        'hover:border-white/30'
      )}
    >
      {/* Step Number - Large background overlay */}
      <div
        className={cn(
          'absolute -top-4 -right-2 text-6xl sm:text-7xl font-bold',
          'text-white/5 select-none pointer-events-none',
          'transition-all duration-300',
          'group-hover:text-white/10'
        )}
      >
        {stepNumber}
      </div>

      {/* Step Number Badge */}
      <div
        className={cn(
          'absolute -top-1 -left-1 w-8 h-8 rounded-full',
          'bg-white/10 border border-white/20',
          'flex items-center justify-center',
          'transition-all duration-300',
          'group-hover:bg-white/20 group-hover:border-white/40'
        )}
      >
        <span className="text-xs font-bold text-white/60 group-hover:text-white/90 transition-colors">
          {stepNumber}
        </span>
      </div>

      {/* Icon with glow effect on hover */}
      <div className="mb-3 mt-4 relative">
        <div
          className={cn(
            'absolute inset-0 rounded-full bg-white/0 blur-xl',
            'transition-all duration-300',
            'group-hover:bg-white/10'
          )}
        />
        <PixelIcon name={step.icon} size="lg" variant="default" />
      </div>

      {/* Title */}
      <h3
        className={cn(
          'text-heading-3 font-semibold text-text-primary mb-2',
          'transition-colors duration-300',
          'group-hover:text-white'
        )}
      >
        {step.title}
      </h3>

      {/* Description */}
      <p className="text-body-sm text-text-secondary relative z-10">{step.description}</p>
    </Card>
  );
}

'use client';

import { cn } from '@/lib/cn';
import { AddressInput } from '@/components/wallet/AddressInput';

export interface HeroProps {
  /** Additional class names */
  className?: string;
}

/**
 * Hero - Main landing page hero section
 * Monochrome terminal aesthetic with entrance animations
 */
export function Hero({ className }: HeroProps) {
  return (
    <section className={cn('relative py-12 lg:py-20 overflow-hidden', className)}>
      <div className="relative max-w-4xl mx-auto text-center px-4">
        {/* Main Title - Word-by-word animated entrance */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
          <span className="block text-text-primary">
            <span className="inline-block animate-word-reveal [animation-delay:0ms]">THE</span>{' '}
            <span className="inline-block animate-word-reveal [animation-delay:100ms]">WORKING</span>{' '}
            <span className="inline-block animate-word-reveal [animation-delay:200ms]">MAN&apos;S</span>
          </span>
          <span className="block mt-2">
            <span
              className={cn(
                'inline-block animate-word-reveal [animation-delay:400ms]',
                'text-white animate-pulse-glow',
                'drop-shadow-[0_0_30px_rgba(255,255,255,0.5)]'
              )}
            >
              GOLD MINE
            </span>
          </span>
        </h1>

        {/* Tagline - Staggered entrance */}
        <p className="text-body lg:text-lg text-text-secondary mb-8 max-w-2xl mx-auto animate-fade-slide-in [animation-delay:600ms]">
          Hold CPU to mine $GOLD around the clock. Trading fees fund the rewards
          pool. Hold longer, earn up to 5x more.
        </p>

        {/* CTA - Visual hierarchy: Primary > Secondary > Tertiary */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10 animate-fade-slide-in [animation-delay:800ms]">
          {/* Primary CTA - Enter wallet address with glow */}
          <div className="relative group w-full sm:w-auto sm:min-w-[280px]">
            <div className="absolute -inset-1 bg-white/20 rounded-lg blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <AddressInput size="lg" fullWidth className="relative" />
          </div>

          {/* Secondary CTA - Buy CPU */}
          <a
            href="https://pump.fun"
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              'px-6 py-3 rounded-lg text-sm font-medium',
              'bg-white/5 hover:bg-white/15 text-white',
              'border border-white/20 hover:border-white/40',
              'transition-all duration-300',
              'hover:shadow-[0_0_20px_rgba(255,255,255,0.15)]'
            )}
          >
            Buy CPU
          </a>

          {/* Tertiary CTA - Text link */}
          <a
            href="#how-it-works"
            className={cn(
              'text-body-sm text-text-muted hover:text-white',
              'transition-colors duration-200',
              'underline-offset-4 hover:underline'
            )}
          >
            See how the mine works
          </a>
        </div>
      </div>
    </section>
  );
}

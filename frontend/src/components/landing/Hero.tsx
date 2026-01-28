'use client';

import { cn } from '@/lib/cn';
import { branding } from '@/config';
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
  // Split tagline for animated display (assumes format "THE WORKING MAN'S GOLD MINE" or similar)
  const taglineParts = branding.tagline.toUpperCase().split(' ');
  const lastTwoWords = taglineParts.slice(-2).join(' ');
  const firstWords = taglineParts.slice(0, -2);

  return (
    <section className={cn('relative py-12 lg:py-20 overflow-hidden', className)}>
      <div className="relative max-w-4xl mx-auto text-center px-4">
        {/* Main Title - Word-by-word animated entrance */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
          <span className="block text-text-primary">
            {firstWords.map((word, i) => (
              <span key={word + i}>
                <span
                  className="inline-block animate-word-reveal"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  {word === "MAN'S" ? "MAN'S" : word}
                </span>{' '}
              </span>
            ))}
          </span>
          <span className="block mt-2">
            <span
              className={cn(
                'inline-block animate-word-reveal',
                'text-white animate-pulse-glow',
                'drop-shadow-[0_0_30px_rgba(255,255,255,0.5)]'
              )}
              style={{ animationDelay: `${firstWords.length * 100 + 200}ms` }}
            >
              {lastTwoWords}
            </span>
          </span>
        </h1>

        {/* Tagline - Staggered entrance */}
        <p className="text-body lg:text-lg text-text-secondary mb-8 max-w-2xl mx-auto animate-fade-slide-in [animation-delay:600ms]">
          Hold {branding.holdToken.symbol} to mine ${branding.rewardToken.symbol} around the clock.
          Trading fees fund the rewards pool. Hold longer, earn up to 5x more.
        </p>

        {/* CTA - Visual hierarchy: Primary > Secondary > Tertiary */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10 animate-fade-slide-in [animation-delay:800ms]">
          {/* Primary CTA - Enter wallet address with glow */}
          <div className="relative group w-full sm:w-auto sm:min-w-[280px]">
            <div className="absolute -inset-1 bg-white/20 rounded-lg blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <AddressInput size="lg" fullWidth className="relative" />
          </div>

          {/* Secondary CTA - Buy token */}
          <a
            href={branding.buyTokenUrl}
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
            Buy {branding.holdToken.symbol}
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

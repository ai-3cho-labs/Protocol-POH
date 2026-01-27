'use client';

import { cn } from '@/lib/cn';
import { formatMultiplier, formatDuration } from '@/lib/utils';
import { TIER_CONFIG, type TierId, type TierStyle } from '@/types/models';
import { Card, PixelProgress } from '@/components/ui';

export interface TierExplainerProps {
  /** Currently highlighted tier (optional) */
  highlightTier?: TierId;
  /** Additional class names */
  className?: string;
}

/**
 * TierExplainer - Visual tier progression table
 * Enhanced with color-coded tier badges, visual hierarchy, and Diamond Hands special styling
 */
export function TierExplainer({ highlightTier, className }: TierExplainerProps) {
  const tiers = Object.entries(TIER_CONFIG) as [string, TierStyle][];

  return (
    <section className={cn('py-12 lg:py-20', className)}>
      <div className="max-w-4xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-10">
          <h2 className="text-2xl lg:text-3xl font-bold text-text-primary mb-4 tracking-tight">
            TIER PROGRESSION
          </h2>
          <p className="text-body text-text-secondary max-w-lg mx-auto">
            Hold longer, earn more. Each tier unlocks higher reward multipliers.
            Selling drops you one tier, so diamond hands wins.
          </p>
        </div>

        {/* Desktop: Enhanced Table */}
        <div className="hidden lg:block">
          <Card noPadding className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-text-muted bg-white/[0.02]">
                  <th className="text-left px-4 py-3 w-12"></th>
                  <th className="text-left px-4 py-3">TIER</th>
                  <th className="text-left px-4 py-3">NAME</th>
                  <th className="text-right px-4 py-3">MIN HOLD</th>
                  <th className="text-right px-4 py-3">MULTIPLIER</th>
                  <th className="text-right px-4 py-3 w-32">POWER</th>
                </tr>
              </thead>
              <tbody>
                {tiers.map(([id, config], index) => {
                  const tierId = parseInt(id) as TierId;
                  const isHighlighted = tierId === highlightTier;
                  const isDiamondHands = tierId === 6;
                  const progressToMax = (config.multiplier / 5) * 100;

                  return (
                    <tr
                      key={id}
                      className={cn(
                        'border-b border-border/50 transition-all duration-300',
                        // Alternating row backgrounds
                        index % 2 === 0 ? 'bg-transparent' : 'bg-white/[0.02]',
                        // Highlighted state
                        isHighlighted && 'bg-white/10',
                        // Diamond Hands special styling
                        isDiamondHands && [
                          'bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent',
                          'border-amber-500/20',
                          'shadow-[inset_0_0_30px_rgba(251,191,36,0.05)]',
                        ],
                        // Hover effect
                        'hover:bg-white/[0.05]'
                      )}
                    >
                      {/* Tier badge */}
                      <td className="px-4 py-3 text-center">
                        <div
                          className={cn(
                            'w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-bold',
                            config.bgColor,
                            config.color
                          )}
                        >
                          {config.label}
                        </div>
                      </td>
                      {/* Tier code */}
                      <td className="px-4 py-3">
                        <span className={cn(
                          'font-mono',
                          isDiamondHands ? 'text-amber-400' : 'text-gray-400'
                        )}>
                          [{config.name.toUpperCase().slice(0, 3)}]
                        </span>
                      </td>
                      {/* Name */}
                      <td className="px-4 py-3">
                        <span
                          className={cn(
                            'font-medium',
                            isHighlighted ? 'text-white' : 'text-text-primary',
                            isDiamondHands && 'text-amber-300'
                          )}
                        >
                          {config.name}
                          {isDiamondHands && (
                            <span className="ml-2 px-1.5 py-0.5 text-[10px] font-bold uppercase rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                              MAX
                            </span>
                          )}
                        </span>
                      </td>
                      {/* Min hold */}
                      <td className="px-4 py-3 text-right text-text-secondary">
                        {config.minHours === 0
                          ? 'Instant'
                          : formatDuration(config.minHours)}
                      </td>
                      {/* Multiplier */}
                      <td className="px-4 py-3 text-right">
                        <span
                          className={cn(
                            'font-semibold tabular-nums',
                            isHighlighted
                              ? 'text-white glow-white'
                              : isDiamondHands
                              ? 'text-amber-300'
                              : 'text-gray-200'
                          )}
                        >
                          {formatMultiplier(config.multiplier)}
                        </span>
                      </td>
                      {/* Visual power bar */}
                      <td className="px-4 py-3">
                        <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                          <div
                            className={cn(
                              'h-full rounded-full transition-all duration-500',
                              isDiamondHands
                                ? 'bg-gradient-to-r from-amber-500 to-amber-400'
                                : 'bg-white/40'
                            )}
                            style={{ width: `${progressToMax}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Card>
        </div>

        {/* Mobile: Enhanced Card Stack */}
        <div className="lg:hidden space-y-2 sm:space-y-3">
          {tiers.map(([id, config]) => {
            const tierId = parseInt(id) as TierId;
            const isHighlighted = tierId === highlightTier;
            const isDiamondHands = tierId === 6;
            const progressToMax = (config.multiplier / 5) * 100;

            return (
              <div
                key={id}
                className={cn(
                  'p-3 sm:p-4 rounded-lg border transition-all duration-300',
                  isHighlighted
                    ? 'bg-white/10 border-white/30'
                    : isDiamondHands
                    ? [
                        'bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-bg-card',
                        'border-amber-500/30',
                        'shadow-[0_0_20px_rgba(251,191,36,0.1)]',
                      ]
                    : 'bg-bg-card border-border'
                )}
              >
                <div className="flex items-center justify-between mb-1.5 sm:mb-2">
                  <div className="flex items-center gap-2 sm:gap-3">
                    {/* Tier badge */}
                    <div
                      className={cn(
                        'w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold',
                        config.bgColor,
                        config.color
                      )}
                    >
                      {config.label}
                    </div>
                    {/* Tier info */}
                    <div>
                      <div className={cn(
                        'font-medium flex items-center gap-2',
                        isDiamondHands ? 'text-amber-300' : 'text-text-primary'
                      )}>
                        {config.name}
                        {isDiamondHands && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                            MAX
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-text-muted">
                        {config.minHours === 0
                          ? 'Start here'
                          : `After ${formatDuration(config.minHours)}`}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div
                      className={cn(
                        'text-lg font-bold tabular-nums',
                        isHighlighted
                          ? 'text-white glow-white'
                          : isDiamondHands
                          ? 'text-amber-300'
                          : 'text-gray-200'
                      )}
                    >
                      {formatMultiplier(config.multiplier)}
                    </div>
                    <div className="text-xs text-text-muted">multiplier</div>
                  </div>
                </div>
                <PixelProgress
                  value={progressToMax}
                  variant={isDiamondHands ? 'gradient' : isHighlighted ? 'gradient' : 'default'}
                  size="sm"
                  segments={5}
                />
              </div>
            );
          })}
        </div>

        {/* Bottom Note - Enhanced */}
        <div className="mt-8 text-center">
          <p className="text-body-sm text-text-muted">
            Selling resets your streak by one tier level.{' '}
            <span className={cn(
              'font-semibold',
              'text-amber-300',
              'drop-shadow-[0_0_10px_rgba(251,191,36,0.5)]'
            )}>
              Diamond Hands
            </span>{' '}
            who hold 30+ days earn the maximum 5x multiplier.
          </p>
        </div>
      </div>
    </section>
  );
}

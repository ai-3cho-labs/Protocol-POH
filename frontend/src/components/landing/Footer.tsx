'use client';

import { cn } from '@/lib/cn';

export interface FooterProps {
  className?: string;
}

/**
 * Minimal footer with essential links and disclaimer
 */
export function Footer({ className }: FooterProps) {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className={cn(
        'border-t border-white/10 bg-black/20 backdrop-blur-sm',
        'py-8 mt-16',
        className
      )}
    >
      <div className="max-w-4xl mx-auto px-4">
        {/* Links Row */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-6">
          <a
            href="https://pump.fun"
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium',
              'bg-white/10 hover:bg-white/20 text-white',
              'border border-white/20 hover:border-white/40',
              'transition-all duration-200'
            )}
          >
            Buy $CPU on Pump.fun
          </a>
          <a
            href="https://solscan.io"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-zinc-400 hover:text-white transition-colors"
          >
            View Contract
          </a>
        </div>

        {/* Disclaimer */}
        <div className="text-center space-y-2">
          <p className="text-caption text-zinc-500 leading-relaxed">
            $CPU is a memecoin with no intrinsic value or expectation of financial return.
            Not financial advice. Trade at your own risk.
          </p>
          <p className="text-caption text-zinc-600">
            &copy; {currentYear} $CPU Mine. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

'use client';

import { cn } from '@/lib/cn';

export interface FooterProps {
  className?: string;
}

/**
 * Footer - Enhanced with link organization and hover effects
 */
export function Footer({ className }: FooterProps) {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className={cn(
        'relative border-t border-white/10',
        'py-8 mt-16',
        className
      )}
    >
      {/* Gradient fade from content */}
      <div className="absolute inset-x-0 -top-16 h-16 bg-gradient-to-t from-bg-dark/50 to-transparent pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4">
        {/* Links Grid */}
        <div className="flex flex-wrap items-center justify-center gap-6 mb-6">
          {/* Primary Action */}
          <a
            href="https://pump.fun"
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              'group relative px-4 py-2 rounded-lg text-sm font-medium',
              'bg-white/10 hover:bg-white/20 text-white',
              'border border-white/20 hover:border-white/40',
              'transition-all duration-300',
              'hover:shadow-[0_0_20px_rgba(255,255,255,0.15)]'
            )}
          >
            <span className="relative z-10">Buy CPU on Pump.fun</span>
          </a>

          {/* Divider */}
          <div className="hidden sm:block w-px h-4 bg-white/20" />

          {/* Links Group */}
          <div className="flex items-center gap-4">
            <FooterLink href="https://solscan.io" label="Contract" />
            <FooterLink href="https://x.com" label="Twitter" />
            <FooterLink href="https://t.me" label="Telegram" />
          </div>
        </div>

        {/* Disclaimer */}
        <div className="text-center space-y-3">
          <p className="text-caption text-zinc-500 leading-relaxed max-w-md mx-auto">
            CPU and $GOLD are memecoins with no intrinsic value or expectation of financial return.
            Not financial advice. Trade at your own risk.
          </p>

          {/* Copyright */}
          <div className="flex items-center justify-center gap-2 text-caption text-zinc-600">
            <span>&copy; {currentYear} CPU Mine</span>
            <span className="text-zinc-700">•</span>
            <span>All rights reserved</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

/**
 * Footer link with hover effect
 */
function FooterLink({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        'text-sm text-zinc-400',
        'transition-all duration-200',
        'hover:text-white',
        'relative',
        // Underline animation
        'after:absolute after:left-0 after:bottom-0 after:w-0 after:h-px',
        'after:bg-white/50 after:transition-all after:duration-200',
        'hover:after:w-full'
      )}
    >
      {label}
    </a>
  );
}

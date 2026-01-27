'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/cn';
import { AddressInput } from '@/components/wallet/AddressInput';

const NAV_LINKS = [
  { href: '/', label: 'Home' },
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/leaderboard', label: 'Leaderboard' },
] as const;

/**
 * Desktop header with navigation
 * Monochrome terminal aesthetic with frosted glass
 */
export function Header() {
  const pathname = usePathname();

  return (
    <header className="hidden lg:block border-b border-terminal-border bg-bg-dark/80 backdrop-blur-[4px] sticky top-0 z-40">
      <div className="container mx-auto px-6">
        <div className="relative flex items-center justify-between h-16">
          {/* Logo - Left */}
          <Link
            href="/"
            className="flex items-center gap-2 group"
          >
            <Image
              src="/logo.jpg"
              alt="CPU Logo"
              width={40}
              height={40}
              className="rounded"
              priority
            />
            <span className="text-2xl font-bold text-white glow-white group-hover:text-gray-200 transition-colors">
              CPU
            </span>
          </Link>

          {/* Navigation - Centered */}
          <nav className="absolute left-1/2 -translate-x-1/2 flex items-center gap-1">
            {NAV_LINKS.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'px-4 py-2 text-sm font-mono rounded transition-colors',
                    isActive
                      ? 'text-white bg-white/10'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
                  )}
                >
                  {isActive && <span className="text-gray-500 mr-1">&gt;</span>}
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Address Input - Right */}
          <AddressInput size="sm" />
        </div>
      </div>
    </header>
  );
}

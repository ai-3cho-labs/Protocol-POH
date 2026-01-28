'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/cn';
import { branding } from '@/config';
import { AddressInput } from '@/components/wallet/AddressInput';

const NAV_LINKS = [
  { href: '/', label: 'Home' },
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/leaderboard', label: 'Leaderboard' },
] as const;

/**
 * Desktop header with navigation
 * Light modern aesthetic
 */
export function Header() {
  const pathname = usePathname();

  return (
    <header className="hidden lg:block border-b border-gray-100 bg-white/80 backdrop-blur-[4px] sticky top-0 z-40">
      <div className="container mx-auto px-6">
        <div className="relative flex items-center justify-between h-16">
          {/* Logo - Left */}
          <Link href="/" prefetch={false} className="flex items-center group">
            <Image
              src="/branding/logo-small.jpg"
              alt={branding.holdToken.symbol}
              width={48}
              height={48}
              className="rounded group-hover:opacity-90 transition-opacity"
              priority
            />
          </Link>

          {/* Navigation - Centered */}
          <nav className="absolute left-1/2 -translate-x-1/2 flex items-center gap-1">
            {NAV_LINKS.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  prefetch={false}
                  className={cn(
                    'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'text-gray-900 bg-gray-100'
                      : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                  )}
                >
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

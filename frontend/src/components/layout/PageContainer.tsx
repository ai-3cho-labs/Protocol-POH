'use client';

import { cn } from '@/lib/cn';
import { Header } from './Header';
import { MobileNav } from './MobileNav';

export interface PageContainerProps {
  /** Page content */
  children: React.ReactNode;
  /** Show header */
  showHeader?: boolean;
  /** Show mobile nav */
  showMobileNav?: boolean;
  /** Max width constraint */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  /** Additional class names for content */
  className?: string;
  /** Full height mode */
  fullHeight?: boolean;
}

/**
 * Page container component
 * Light theme with clean white background
 */
export function PageContainer({
  children,
  showHeader = true,
  showMobileNav = true,
  maxWidth = 'xl',
  className,
  fullHeight = false,
}: PageContainerProps) {
  const maxWidthClasses = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    '2xl': 'max-w-screen-2xl',
    full: 'max-w-full',
  };

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Desktop Header */}
      {showHeader && <Header />}

      {/* Main Content */}
      <main
        className={cn(
          'flex-1 relative z-10',
          // Desktop: Container with padding
          'lg:container lg:mx-auto lg:px-6 lg:pt-12 lg:pb-8',
          // Mobile: Full width with bottom padding for nav
          'px-4 py-4',
          showMobileNav && 'pb-20 lg:pb-8',
          // Max width
          maxWidthClasses[maxWidth],
          // Full height for centered content
          fullHeight && 'flex flex-col',
          className
        )}
      >
        {children}
      </main>

      {/* Mobile Bottom Navigation */}
      {showMobileNav && <MobileNav />}
    </div>
  );
}

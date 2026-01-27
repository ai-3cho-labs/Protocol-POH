import type { Metadata, Viewport } from 'next';
import { Providers } from '@/components/providers/Providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'Copper Processing Unit',
  description:
    'Hold CPU tokens to mine $GOLD rewards. Trading fees fund the pool. Build streaks, get paid.',
  keywords: ['solana', 'memecoin', 'mining', 'crypto', 'rewards', 'defi', 'cpu', 'gold'],
  authors: [{ name: 'CPU Team' }],
  icons: {
    icon: '/icon.jpg',
    apple: '/icon.jpg',
  },
  openGraph: {
    title: 'Copper Processing Unit',
    description:
      'Hold CPU tokens to mine $GOLD rewards. Trading fees fund the pool. Build streaks, get paid.',
    type: 'website',
    locale: 'en_US',
    images: [
      {
        url: '/logo.jpg',
        width: 1024,
        height: 1024,
        alt: 'CPU Logo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Copper Processing Unit',
    description:
      'Hold CPU tokens to mine $GOLD rewards. Trading fees fund the pool. Build streaks, get paid.',
    images: ['/logo.jpg'],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#0a0a0a',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

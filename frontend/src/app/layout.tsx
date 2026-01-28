import type { Metadata, Viewport } from 'next';
import { Providers } from '@/components/providers/Providers';
import { branding, themeColors } from '@/config';
import './globals.css';

export const metadata: Metadata = {
  title: branding.appName,
  description: branding.seoDescription,
  keywords: branding.seoKeywords,
  authors: [{ name: `${branding.appShortName} Team` }],
  icons: {
    icon: '/branding/icon.jpg',
    apple: '/branding/icon.jpg',
  },
  openGraph: {
    title: branding.appName,
    description: branding.seoDescription,
    type: 'website',
    locale: 'en_US',
    images: [
      {
        url: '/branding/og-image.jpg',
        width: 1200,
        height: 630,
        alt: `${branding.appShortName} Logo`,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: branding.appName,
    description: branding.seoDescription,
    images: ['/branding/og-image.jpg'],
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
  themeColor: themeColors.themeColor,
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

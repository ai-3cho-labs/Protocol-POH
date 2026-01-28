/**
 * Theme Configuration
 *
 * Accent colors and theme settings for white-label deployments.
 * Override via environment variables for custom deployments.
 */

export const themeColors = {
  // Primary accent (gold/amber by default)
  accent: process.env.NEXT_PUBLIC_ACCENT_COLOR || '#f59e0b',
  accentLight: process.env.NEXT_PUBLIC_ACCENT_LIGHT || '#fbbf24',
  accentDark: process.env.NEXT_PUBLIC_ACCENT_DARK || '#d97706',

  // Background
  background: process.env.NEXT_PUBLIC_BG_COLOR || '#0a0a0a',

  // Theme color for mobile browser chrome
  themeColor: process.env.NEXT_PUBLIC_THEME_COLOR || '#0a0a0a',
} as const;

// Type for theme colors
export type ThemeColors = typeof themeColors;

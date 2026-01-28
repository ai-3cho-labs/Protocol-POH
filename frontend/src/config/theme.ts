/**
 * Theme Configuration
 *
 * Accent colors and theme settings for white-label deployments.
 * Override via environment variables for custom deployments.
 */

export const themeColors = {
  // Primary accent (dark gray/black for light theme)
  accent: process.env.NEXT_PUBLIC_ACCENT_COLOR || '#111827',
  accentLight: process.env.NEXT_PUBLIC_ACCENT_LIGHT || '#374151',
  accentDark: process.env.NEXT_PUBLIC_ACCENT_DARK || '#030712',

  // Background
  background: process.env.NEXT_PUBLIC_BG_COLOR || '#ffffff',

  // Theme color for mobile browser chrome
  themeColor: process.env.NEXT_PUBLIC_THEME_COLOR || '#ffffff',
} as const;

// Type for theme colors
export type ThemeColors = typeof themeColors;

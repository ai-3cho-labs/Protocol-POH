import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Light theme palette
        accent: '#111827',
        // Backgrounds - Light
        bg: {
          dark: '#ffffff',
          card: '#ffffff',
          surface: '#f9fafb',
        },
        // Neutrals
        border: '#e5e7eb',
        text: {
          primary: '#111827',
          secondary: '#6b7280',
          muted: '#9ca3af',
        },
        // Gray scale for UI elements
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
      },
      fontFamily: {
        mono: [
          'IBM Plex Mono',
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'sans-serif',
        ],
      },
      fontSize: {
        xxs: ['0.625rem', { lineHeight: '0.875rem' }],
        // Semantic typography scale
        'display': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display-sm': ['2.5rem', { lineHeight: '1.15', letterSpacing: '-0.01em' }],
        'heading-1': ['2rem', { lineHeight: '1.2' }],
        'heading-2': ['1.5rem', { lineHeight: '1.3' }],
        'heading-3': ['1.125rem', { lineHeight: '1.4' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'body-sm': ['0.875rem', { lineHeight: '1.5' }],
        'caption': ['0.75rem', { lineHeight: '1.4' }],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 2s linear infinite',
        blink: 'blink 1s step-end infinite',
        'float': 'float 3s ease-in-out infinite',
        'coin-collect': 'coinCollect 0.8s ease-out forwards',
        // Pixel miner pickaxe animation (8 frames at 56px each = 448px total)
        'mine': 'mine 0.8s steps(8) infinite',
        // Entrance animations (use 'both' to apply initial state during delay)
        'fade-slide-in': 'fadeSlideIn 0.4s ease-out both',
        'fade-in': 'fadeIn 0.5s ease-out both',
        'fade-out': 'fadeOut 0.2s ease-in forwards',
        'count-up': 'countUp 0.6s ease-out both',
        // Shimmer for skeletons
        'shimmer': 'shimmer 1.5s infinite',
        // Modal slide animations
        'slide-up': 'slideUp 0.3s ease-out both',
        'slide-down': 'slideDown 0.2s ease-in forwards',
        // Landing page enhancements
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'pulse-dot': 'pulseDot 2s ease-in-out infinite',
        'word-reveal': 'wordReveal 0.5s ease-out both',
        'scale-in': 'scaleIn 0.3s ease-out both',
        'draw-line': 'drawLine 1s ease-out both',
        'fade-in-right': 'fadeInRight 0.3s ease-out both',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
        coinCollect: {
          '0%': { transform: 'scale(1) translateY(0)', opacity: '1' },
          '50%': { transform: 'scale(1.2) translateY(-20px)', opacity: '1' },
          '100%': { transform: 'scale(0.5) translateY(-60px)', opacity: '0' },
        },
        // Sprite sheet animation - moves through 8 horizontal frames
        mine: {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '-448px 0' },
        },
        // Entrance animations
        fadeSlideIn: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        countUp: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        // Modal slide keyframes
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(0)', opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
        // Landing page enhancement keyframes
        pulseGlow: {
          '0%, 100%': { textShadow: '0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.3)' },
          '50%': { textShadow: '0 0 20px rgba(255, 255, 255, 0.8), 0 0 40px rgba(255, 255, 255, 0.4)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.5', transform: 'scale(0.8)' },
        },
        wordReveal: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        drawLine: {
          '0%': { strokeDashoffset: '100' },
          '100%': { strokeDashoffset: '0' },
        },
        fadeInRight: {
          '0%': { opacity: '0', transform: 'translateX(-10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      screens: {
        'xs': '375px',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
      },
      backgroundImage: {
        // Light theme - clean white
        'cave-gradient': 'linear-gradient(180deg, #ffffff 0%, #f9fafb 100%)',
        'mobile-gradient': 'linear-gradient(180deg, #ffffff 0%, #f9fafb 100%)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
};

export default config;

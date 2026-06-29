/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Base backgrounds (avoiding pure black/white)
        background: {
          dark: '#111113', // Rich Charcoal
          light: '#FDFCFB', // Warm Off White
          DEFAULT: '#111113', // Default to dark for this SaaS feel
        },
        surface: {
          DEFAULT: '#18181A',
          elevated: '#212124',
        },
        border: {
          DEFAULT: '#27272A',
          subtle: '#3F3F46',
        },
        foreground: {
          DEFAULT: '#FAFAFA',
          muted: '#A1A1AA',
        },
        muted: '#A1A1AA', // Added to support text-muted and bg-muted classes
        elevated: '#212124', // Added to support bg-elevated classes
        // Module Atmospheres
        atmosphere: {
          dashboard: {
            main: '#1E3A8A', // Deep Navy
            accent: '#3B82F6', // Electric Blue
            light: '#E0F2FE', // Ice
          },
          pipeline: {
            main: '#F97316', // Signal Orange
            accent: '#F59E0B', // Amber
            muted: '#3F3F46', // Graphite/Steel
          },
          replay: {
            main: '#10B981', // Emerald
            accent: '#34D399', // Mint
            muted: '#64748B', // Slate
          },
          provenance: {
            main: '#4338CA', // Indigo
            accent: '#8B5CF6', // Blue Violet
            muted: '#78716C', // Stone
          },
          evaluation: {
            main: '#6D28D9', // Royal Purple
            accent: '#A78BFA', // Lavender
            muted: '#737373', // Neutral
          },
          benchmark: {
            main: '#06B6D4', // Cyan
            accent: '#14B8A6', // Teal
            muted: '#334155', // Charcoal
          },
          operations: {
            main: '#E11D48', // Crimson
            accent: '#FB7185', // Coral
            muted: '#0F172A', // Dark Slate
          },
          failure: {
            main: '#9F1239', // Deep Crimson
            accent: '#EA580C', // Burnt Orange
            muted: '#3F3F46', // Graphite
          },
          docs: {
            main: '#B45309', // Ochre
            accent: '#FEF3C7', // Cream
            muted: '#451A03', // Walnut
          },
        },
        // Utilities
        accent: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          muted: 'rgba(59, 130, 246, 0.12)',
        },
        success: {
          DEFAULT: '#10B981',
          muted: 'rgba(16, 185, 129, 0.12)',
        },
        warning: {
          DEFAULT: '#F59E0B',
          muted: 'rgba(245, 158, 11, 0.12)',
        },
        danger: {
          DEFAULT: '#E11D48',
          muted: 'rgba(225, 29, 72, 0.12)',
        },
      },
      fontFamily: {
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      spacing: {
        18: '4.5rem',
        70: '17.5rem',
      },
      animation: {
        'pulse-subtle': 'pulse-subtle 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
      boxShadow: {
        panel: '0 0 0 1px rgba(39, 39, 42, 0.8), 0 4px 12px rgba(0, 0, 0, 0.3)',
        glow: '0 0 20px rgba(59, 130, 246, 0.15)',
        lift: '0 8px 30px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05)',
      },
    },
  },
  plugins: [],
}

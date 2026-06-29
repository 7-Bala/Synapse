/**
 * @module RadiusTokens
 * @description Defines the border-radius scale for the design system.
 * @version 1.0.0
 */
export const radius = {
  none: '0',
  sm: 'var(--radius-sm, 0.125rem)',
  md: 'var(--radius-md, 0.375rem)',
  lg: 'var(--radius-lg, 0.5rem)',
  xl: 'var(--radius-xl, 0.75rem)',
  full: '9999px',
} as const;

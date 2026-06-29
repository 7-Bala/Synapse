/**
 * @module FocusTokens
 * @description Standardized focus ring styles for accessibility.
 */
export const focus = {
  ring: 'var(--focus-ring, 2px solid var(--color-accent-default))',
  offset: 'var(--focus-offset, 2px)',
} as const;

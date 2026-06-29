/**
 * @module ShadowTokens
 * @description Semantic box-shadow definitions.
 */
export const shadow = {
  none: 'none',
  sm: 'var(--shadow-sm, 0 1px 2px 0 rgb(0 0 0 / 0.05))',
  panel: 'var(--shadow-panel, 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1))',
  modal: 'var(--shadow-modal, 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1))',
  glow: 'var(--shadow-glow, 0 0 20px rgba(59, 130, 246, 0.15))',
} as const;

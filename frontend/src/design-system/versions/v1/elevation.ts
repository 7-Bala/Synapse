/**
 * @module ElevationTokens
 * @description Z-axis elevation semantic levels for layering.
 */
export const elevation = {
  base: 'var(--elevation-base, 0)',
  raised: 'var(--elevation-raised, 10)',
  overlay: 'var(--elevation-overlay, 20)',
  sticky: 'var(--elevation-sticky, 30)',
  dropdown: 'var(--elevation-dropdown, 40)',
  modal: 'var(--elevation-modal, 50)',
  toast: 'var(--elevation-toast, 60)',
  tooltip: 'var(--elevation-tooltip, 70)',
} as const;

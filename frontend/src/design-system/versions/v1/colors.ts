/**
 * @module ColorTokens
 * @description Semantic color scale referencing CSS variables. No hardcoded hex values.
 */
export const colors = {
  background: {
    dark: 'var(--color-bg-dark)',
    light: 'var(--color-bg-light)',
    DEFAULT: 'var(--color-bg-default)',
  },
  surface: {
    DEFAULT: 'var(--color-surface-default)',
    elevated: 'var(--color-surface-elevated)',
  },
  border: {
    subtle: 'var(--color-border-subtle)',
    strong: 'var(--color-border-strong)',
  },
  text: {
    primary: 'var(--color-text-primary)',
    secondary: 'var(--color-text-secondary)',
    muted: 'var(--color-text-muted)',
  },
  status: {
    idle: 'var(--color-status-idle)',
    queued: 'var(--color-status-queued)',
    running: 'var(--color-status-running)',
    consensus: 'var(--color-status-consensus)',
    verified: 'var(--color-status-verified)',
    warning: 'var(--color-status-warning)',
    recovering: 'var(--color-status-recovering)',
    degraded: 'var(--color-status-degraded)',
    circuitOpen: 'var(--color-status-circuit-open)',
    circuitClosed: 'var(--color-status-circuit-closed)',
    replayReady: 'var(--color-status-replay-ready)',
    evidenceMissing: 'var(--color-status-evidence-missing)',
    validationFailed: 'var(--color-status-validation-failed)'
  }
} as const;

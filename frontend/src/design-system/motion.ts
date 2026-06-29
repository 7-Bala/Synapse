export const MotionConfig = {
  boot: {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4, ease: [0.23, 1, 0.32, 1] }
  },
  open: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    transition: { duration: 0.2, ease: 'easeOut' }
  },
  highlight: {
    animate: { backgroundColor: 'var(--color-surface-elevated)' },
    transition: { duration: 0.2 }
  }
} as const;

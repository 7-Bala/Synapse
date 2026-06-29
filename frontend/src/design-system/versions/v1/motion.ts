/**
 * @module MotionTokens
 * @description Centralized Framer Motion semantic presets for enterprise components.
 */
export const motion = {
  boot: { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.4, ease: [0.23, 1, 0.32, 1] } },
  enter: { initial: { opacity: 0, scale: 0.98 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.2, ease: 'easeOut' } },
  exit: { initial: { opacity: 1, scale: 1 }, animate: { opacity: 0, scale: 0.98 }, transition: { duration: 0.15, ease: 'easeIn' } },
  hover: { whileHover: { scale: 1.02, transition: { duration: 0.1 } } },
  press: { whileTap: { scale: 0.97 } },
  focus: { animate: { outline: 'var(--focus-ring)' } },
  selection: { animate: { backgroundColor: 'var(--color-surface-elevated)' } },
  expand: { initial: { height: 0, opacity: 0 }, animate: { height: 'auto', opacity: 1 }, transition: { duration: 0.3, ease: 'easeInOut' } },
  collapse: { initial: { height: 'auto', opacity: 1 }, animate: { height: 0, opacity: 0 }, transition: { duration: 0.2, ease: 'easeInOut' } },
  attention: { animate: { scale: [1, 1.05, 1], transition: { repeat: Infinity, duration: 2 } } },
  tooltip: { initial: { opacity: 0, y: 4 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.15 } },
  drawer: { initial: { x: '100%' }, animate: { x: 0 }, transition: { type: 'spring', damping: 25, stiffness: 200 } },
  panel: { initial: { opacity: 0, x: 20 }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.3 } },
  modal: { initial: { opacity: 0, scale: 0.95, y: 20 }, animate: { opacity: 1, scale: 1, y: 0 }, transition: { type: 'spring', damping: 25, stiffness: 300 } },
  toast: { initial: { opacity: 0, y: 50, scale: 0.9 }, animate: { opacity: 1, y: 0, scale: 1 }, transition: { type: 'spring', damping: 20, stiffness: 300 } },
  commandPalette: { initial: { opacity: 0, scale: 0.98 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.15 } },
  workspaceTransition: { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.4 } },
  inspectorOpen: { initial: { width: 0, opacity: 0 }, animate: { width: '320px', opacity: 1 }, transition: { type: 'spring', damping: 30, stiffness: 250 } },
  inspectorClose: { initial: { width: '320px', opacity: 1 }, animate: { width: 0, opacity: 0 }, transition: { duration: 0.2 } },
  reducedMotion: { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.1 } }
} as const;

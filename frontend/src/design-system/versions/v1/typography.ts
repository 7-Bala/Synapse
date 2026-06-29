export const typography = {
  family: {
    sans: ['Geist', 'system-ui', 'sans-serif'],
    mono: ['Geist Mono', 'ui-monospace', 'monospace'],
  },
  size: {
    hero: ['3rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
    display: ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
    pageTitle: ['1.875rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
    workspaceTitle: ['1.5rem', { lineHeight: '1.3' }],
    panelTitle: ['1.25rem', { lineHeight: '1.4' }],
    sectionTitle: ['1.125rem', { lineHeight: '1.5', fontWeight: '500' }],
    body: ['1rem', { lineHeight: '1.5' }],
    caption: ['0.875rem', { lineHeight: '1.5' }],
    label: ['0.75rem', { lineHeight: '1.5', letterSpacing: '0.05em', textTransform: 'uppercase' }],
    metric: ['2rem', { lineHeight: '1.1', fontFeatureSettings: '"tnum"' }],
    hash: ['0.875rem', { lineHeight: '1.5', fontFeatureSettings: '"tnum"' }],
    timestamp: ['0.75rem', { lineHeight: '1.5', fontFeatureSettings: '"tnum"' }],
  }
} as const;

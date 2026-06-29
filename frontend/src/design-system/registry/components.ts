/**
 * @module ComponentRegistry
 * @description The authoritative, machine-readable inventory of all design system exports.
 */
export type MaturityLevel = 'Alpha' | 'Beta' | 'Stable' | 'Deprecated' | 'Experimental';

export interface ComponentMetadata {
  id: string;
  version: string;
  category: 'Provider' | 'Primitive' | 'Component' | 'DataDisplay' | 'Layout' | 'Utility';
  maturity: MaturityLevel;
  owner: string;
  dependencies: string[];
  accessibilityStatus: 'Pass' | 'Fail' | 'Pending';
  documentationStatus: 'Complete' | 'Missing';
  testCoverage: number;
  replacement?: string;
  renderingStrategy?: 'CSR' | 'SSR' | 'Static';
  description: string;
}

export const ComponentRegistry: Record<string, ComponentMetadata> = {
  ThemeProvider: {
    id: 'ThemeProvider',
    version: '1.0.0',
    category: 'Provider',
    maturity: 'Stable',
    owner: 'Platform Team',
    dependencies: [],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'Manages application-wide theme state and CSS variable injection.'
  },
  DesignSystemProvider: {
    id: 'DesignSystemProvider',
    version: '1.0.0',
    category: 'Provider',
    maturity: 'Stable',
    owner: 'Platform Team',
    dependencies: ['ThemeProvider'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'Composes all underlying context providers for the Synapse app.'
  },
  Surface: {
    id: 'Surface',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'The foundational layer for structural components.'
  },
  Panel: {
    id: 'Panel',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['Surface', 'style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A fundamental container block with built-in padding, surface, and border.'
  },
  Stack: {
    id: 'Stack',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'Flexbox layout primitive for organizing items in a 1D axis.'
  },
  Grid: {
    id: 'Grid',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'CSS Grid layout primitive.'
  },
  Divider: {
    id: 'Divider',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A visual separator for layouts.'
  },
  Toolbar: {
    id: 'Toolbar',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['Surface', 'style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A flex container specifically designed for action bars.'
  },
  Section: {
    id: 'Section',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A semantic container for grouped content.'
  },
  ScrollableArea: {
    id: 'ScrollableArea',
    version: '1.0.0',
    category: 'Primitive',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A container that manages its own scroll state.'
  },
  SplitView: {
    id: 'SplitView',
    version: '1.0.0',
    category: 'Layout',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A structural layout that divides space equally or proportionally.'
  },
  PanelGroup: {
    id: 'PanelGroup',
    version: '1.0.0',
    category: 'Layout',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['Stack', 'style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A layout primitive that hosts multiple panels with a shared gap.'
  },
  InspectorLayout: {
    id: 'InspectorLayout',
    version: '1.0.0',
    category: 'Layout',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['Surface', 'Divider', 'style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'An enterprise layout featuring a main content area and a collapsible right-side inspector.'
  },
  ResizablePanel: {
    id: 'ResizablePanel',
    version: '1.0.0',
    category: 'Layout',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A primitive that allows a panel to be resized via a drag handle.'
  },
  WorkspaceGrid: {
    id: 'WorkspaceGrid',
    version: '1.0.0',
    category: 'Layout',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A rigid 2D grid used as the canvas for topological workspaces.'
  },
  DockLayout: {
    id: 'DockLayout',
    version: '1.0.0',
    category: 'Layout',
    maturity: 'Beta',
    owner: 'Platform Team',
    dependencies: ['Surface', 'Divider', 'style.ts'],
    accessibilityStatus: 'Pass',
    documentationStatus: 'Complete',
    testCoverage: 100,
    renderingStrategy: 'CSR',
    description: 'A layout featuring a main stage and a bottom-aligned dock.'
  },
};

/**
 * @module DesignSystemShowcase
 * @description The canonical engineering dashboard for the Synapse Design System.
 */
import { useTheme } from '@/design-system/providers/ThemeProvider';
import { ComponentRegistry } from '@/design-system/registry/components';
import * as formatters from '@/design-system/utils/formatters';

import { Surface } from '@/design-system/primitives/Surface';
import { Panel } from '@/design-system/primitives/Panel';
import { Stack } from '@/design-system/primitives/Stack';
import { Grid } from '@/design-system/primitives/Grid';
import { Divider } from '@/design-system/primitives/Divider';
import { Toolbar } from '@/design-system/primitives/Toolbar';
import { Section } from '@/design-system/primitives/Section';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { SplitView } from '@/design-system/layout/SplitView';
import { InspectorLayout } from '@/design-system/layout/InspectorLayout';
import { WorkspaceGrid } from '@/design-system/layout/WorkspaceGrid';
import { DockLayout } from '@/design-system/layout/DockLayout';


export function DesignSystemShowcase() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground p-8" style={{ backgroundColor: 'var(--color-bg-default)' }}>
      <header className="mb-12 border-b border-border pb-6 flex justify-between items-center" style={{ borderColor: 'var(--color-border-subtle)' }}>
        <div>
          <h1 className="text-3xl font-bold mb-2">Design System Showcase</h1>
          <p className="text-muted" style={{ color: 'var(--color-text-muted)' }}>Canonical visual reference for Synapse enterprise primitives.</p>
        </div>
        <select 
          value={theme}
          onChange={(e) => setTheme(e.target.value as any)}
          className="bg-surface-elevated border border-border rounded px-4 py-2"
          style={{ backgroundColor: 'var(--color-surface-elevated)', color: 'var(--color-text-primary)' }}
        >
          <option value="enterprise-dark">Enterprise Dark</option>
          <option value="enterprise-light">Enterprise Light</option>
          <option value="high-contrast">High Contrast</option>
          <option value="presentation">Presentation</option>
        </select>
      </header>

      <div className="grid gap-12">
        {/* Component Registry */}
        <section>
          <h2 className="text-xl font-semibold mb-4 border-b border-border pb-2">Registry Contents</h2>
          <div className="grid grid-cols-2 gap-4">
            {Object.values(ComponentRegistry).map(comp => (
              <div key={comp.id} className="p-4 rounded border" style={{ borderColor: 'var(--color-border-subtle)', backgroundColor: 'var(--color-surface-default)' }}>
                <h3 className="font-bold">{comp.id} <span className="text-xs px-2 py-1 bg-accent/20 rounded ml-2">{comp.maturity}</span></h3>
                <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary)' }}>{comp.description}</p>
                <div className="text-xs mt-4 flex gap-4">
                  <span>Version: {comp.version}</span>
                  <span>A11y: {comp.accessibilityStatus}</span>
                  <span>Coverage: {comp.testCoverage}%</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Formatting Utilities */}
        <section>
          <h2 className="text-xl font-semibold mb-4 border-b border-border pb-2">Formatting Utilities</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="p-2 border rounded">Bytes: {formatters.formatBytes(1500000)}</div>
            <div className="p-2 border rounded">Latency: {formatters.formatLatency(250)}</div>
            <div className="p-2 border rounded">Duration: {formatters.formatDuration(3665)}</div>
            <div className="p-2 border rounded">CPU: {formatters.formatCPU(4.25)}</div>
            <div className="p-2 border rounded">Cost: {formatters.formatCost(1500.25)}</div>
            <div className="p-2 border rounded">Large Num: {formatters.formatLargeNumber(1500000)}</div>
          </div>
        </section>

      
        {/* Wave B Structural Primitives */}
        <section>
          <h2 className="text-xl font-semibold mb-4 border-b border-border pb-2">Core Structural Primitives (Wave B)</h2>
          <Stack gap={8}>
            
            <Section title="Surface & Panel">
              <Grid cols={2} gap={4}>
                <Surface variant="panel" border="subtle" radius="md" className="p-4">
                  <p className="text-sm">Default Surface</p>
                </Surface>
                <Panel elevated padding="lg">
                  <p className="text-sm">Elevated Panel with lg padding</p>
                </Panel>
              </Grid>
            </Section>

            <Section title="Stack & Divider">
              <Panel>
                <Stack direction="row" gap={4} align="center">
                  <div className="w-8 h-8 bg-accent/20 rounded" />
                  <Divider orientation="vertical" className="h-8" />
                  <div className="w-8 h-8 bg-accent/20 rounded" />
                  <Divider orientation="vertical" className="h-8" />
                  <div className="w-8 h-8 bg-accent/20 rounded" />
                </Stack>
              </Panel>
            </Section>

            <Section title="Toolbar">
              <Toolbar padding="sm" className="bg-surface-elevated rounded">
                <span className="text-sm">Tool 1</span>
                <span className="text-sm">Tool 2</span>
                <span className="text-sm">Tool 3</span>
              </Toolbar>
            </Section>

            <Section title="Layout Engines (Miniature Demos)">
              <Grid cols={2} gap={6}>
                
                <Panel className="h-48 overflow-hidden">
                  <SplitView proportions={[1, 2]}>
                    <div className="h-full bg-accent/10 border-r border-border-subtle p-2 text-xs">Left (1x)</div>
                    <div className="h-full bg-accent/5 p-2 text-xs">Right (2x)</div>
                  </SplitView>
                </Panel>
                
                <Panel className="h-48 overflow-hidden p-0">
                  <InspectorLayout 
                    inspector={<div className="p-2 text-xs h-full bg-surface-elevated">Inspector Content</div>}
                    inspectorWidth={150}
                  >
                    <WorkspaceGrid gridSize={20}>
                      <div className="absolute inset-4 bg-accent/10 flex items-center justify-center text-xs border border-accent/20">
                        WorkspaceGrid Canvas
                      </div>
                    </WorkspaceGrid>
                  </InspectorLayout>
                </Panel>

                <Panel className="h-48 overflow-hidden p-0 col-span-2">
                  <DockLayout
                    dock={<div className="p-2 text-xs h-full bg-surface-elevated">Dock Logs</div>}
                    dockHeight={60}
                  >
                    <ScrollableArea className="h-full p-4">
                      <Stack gap={4}>
                        <div className="h-10 bg-accent/5 border border-border-subtle rounded" />
                        <div className="h-10 bg-accent/5 border border-border-subtle rounded" />
                        <div className="h-10 bg-accent/5 border border-border-subtle rounded" />
                        <div className="h-10 bg-accent/5 border border-border-subtle rounded" />
                        <div className="h-10 bg-accent/5 border border-border-subtle rounded" />
                      </Stack>
                    </ScrollableArea>
                  </DockLayout>
                </Panel>

              </Grid>
            </Section>

          </Stack>
        </section>

      </div>
    </div>
  );
}

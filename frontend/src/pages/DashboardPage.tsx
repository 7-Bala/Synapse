import { Surface } from '@/design-system/primitives/Surface';
import { Panel } from '@/design-system/primitives/Panel';
import { Stack } from '@/design-system/primitives/Stack';
import { Section } from '@/design-system/primitives/Section';
import { DockLayout } from '@/design-system/layout/DockLayout';
import { WorkspaceGrid } from '@/design-system/layout/WorkspaceGrid';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { AlertCircle, PlayCircle, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';
import { cn, formatNumber } from '@/lib/utils';

function ExecutionNode({ label, status, x, y }: { label: string, status: 'running' | 'idle' | 'blocked', x: number, y: number }) {
  return (
    <div 
      className={cn(
        "absolute flex items-center justify-center p-2 bg-surface-elevated border rounded-[8px] shadow-panel hover:z-10 cursor-pointer transition-colors",
        status === 'running' ? 'border-accent shadow-glow' : 
        status === 'blocked' ? 'border-warning shadow-glow-warning' : 'border-border-subtle'
      )}
      style={{ left: x, top: y }}
    >
      <div className="flex flex-col items-center gap-1.5">
        <div className={cn("size-2 rounded-full", 
          status === 'running' ? 'bg-accent animate-pulse' : 
          status === 'blocked' ? 'bg-warning animate-pulse' : 'bg-muted')} 
        />
        <span className="text-2xs font-mono text-muted uppercase hover:text-foreground transition-colors">{label}</span>
      </div>
    </div>
  );
}

export function DashboardPage() {
  return (
    <div className="flex w-full h-full">
      {/* LEFT: Operations Rail */}
      <Surface variant="panel" border="strong" className="w-[300px] shrink-0 border-y-0 border-l-0 flex flex-col h-full bg-surface-elevated z-10">
        <ScrollableArea className="flex-1 p-4">
          <Stack gap={6}>
            <Section title="Quick Actions">
              <Stack gap={2}>
                <button className="flex items-center gap-2 w-full p-2 text-xs text-foreground hover:bg-accent/10 border border-border-subtle hover:border-accent/50 rounded transition-colors text-left font-medium">
                  <PlayCircle className="size-3.5 text-accent" />
                  Deploy New Workload
                </button>
                <button className="flex items-center gap-2 w-full p-2 text-xs text-foreground hover:bg-danger/10 border border-border-subtle hover:border-danger/50 rounded transition-colors text-left font-medium">
                  <AlertTriangle className="size-3.5 text-danger" />
                  Emergency Stop All
                </button>
              </Stack>
            </Section>

            <Section title="Active Swarms">
              <Stack gap={2}>
                {[1, 2, 3].map(i => (
                  <Panel key={i} padding="sm" className="group cursor-pointer hover:border-border-strong transition-colors">
                    <Stack gap={1}>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium">Swarm_Alpha_{i}</span>
                        <span className="text-2xs font-mono text-success uppercase tracking-wider">Running</span>
                      </div>
                      <span className="text-2xs text-muted font-mono">Uptime: 04:12:3{i}</span>
                    </Stack>
                  </Panel>
                ))}
              </Stack>
            </Section>

            <Section title="Human Intervention Required">
              <Panel padding="sm" className="border-warning/50 bg-warning/5 cursor-pointer hover:bg-warning/10 transition-colors">
                <Stack gap={2}>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="size-3.5 text-warning" />
                    <span className="text-xs font-medium text-warning">Swarm_Beta blocked</span>
                  </div>
                  <span className="text-2xs text-muted leading-relaxed">
                    Agent [CodeExecutor] requested permission to run arbitrary bash script on infrastructure.
                  </span>
                  <div className="flex items-center gap-2 mt-1">
                    <button className="text-2xs text-accent hover:underline font-medium">Review Call</button>
                  </div>
                </Stack>
              </Panel>
            </Section>
          </Stack>
        </ScrollableArea>
      </Surface>

      {/* MIDDLE: Command Canvas */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        <DockLayout 
          dockHeight={200}
          dock={
            <div className="flex flex-col h-full">
              <div className="px-4 py-2 border-b border-border-subtle bg-surface flex justify-between items-center shrink-0">
                <span className="text-xs font-mono uppercase tracking-wider font-semibold text-muted">Live Event Stream</span>
                <span className="text-2xs text-muted flex items-center gap-2">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
                  </span>
                  Streaming
                </span>
              </div>
              <ScrollableArea className="flex-1 p-4 bg-background font-mono text-2xs leading-relaxed">
                <Stack gap={1}>
                  <div className="flex gap-4 hover:bg-surface-elevated px-2 py-0.5 rounded transition-colors"><span className="text-muted w-20">10:14:22.1</span><span className="text-accent w-24">[Swarm_Alpha]</span><span className="text-foreground">LLM Request fired (gpt-4-turbo)</span></div>
                  <div className="flex gap-4 hover:bg-surface-elevated px-2 py-0.5 rounded transition-colors"><span className="text-muted w-20">10:14:23.4</span><span className="text-accent w-24">[Swarm_Alpha]</span><span className="text-foreground">Tool call requested: query_database</span></div>
                  <div className="flex gap-4 hover:bg-surface-elevated px-2 py-0.5 rounded transition-colors"><span className="text-muted w-20">10:14:23.5</span><span className="text-success w-24">[Validator]</span><span className="text-foreground">SQL injection check passed. Payload safe.</span></div>
                  <div className="flex gap-4 hover:bg-surface-elevated px-2 py-0.5 rounded transition-colors"><span className="text-muted w-20">10:14:24.0</span><span className="text-warning w-24">[Swarm_Beta]</span><span className="text-foreground">Code execution requested. Pausing for human review.</span></div>
                  <div className="flex gap-4 hover:bg-surface-elevated px-2 py-0.5 rounded transition-colors"><span className="text-muted w-20">10:14:25.1</span><span className="text-accent w-24">[Swarm_Alpha]</span><span className="text-foreground">Blackboard state updated.</span></div>
                </Stack>
              </ScrollableArea>
            </div>
          }
        >
          <WorkspaceGrid gridSize={30}>
            {/* Global Topology Heatmap Overlay */}
            <div className="absolute inset-0 p-6 pointer-events-none z-10 flex justify-between items-start">
              <Stack gap={1}>
                <h2 className="text-lg font-sans font-semibold tracking-tight text-foreground drop-shadow-md">Global Topology Heatmap</h2>
                <span className="text-xs font-mono text-muted uppercase tracking-wider">3 Active Swarms · 12 Nodes · 1 Blocked</span>
              </Stack>
            </div>

            {/* Simulated Nodes */}
            <ExecutionNode label="Gateway" status="running" x={150} y={150} />
            <ExecutionNode label="Validator" status="idle" x={450} y={80} />
            <ExecutionNode label="Code_Executor" status="blocked" x={450} y={220} />
            <ExecutionNode label="Consensus" status="running" x={750} y={150} />

            {/* Connecting Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))' }}>
              <path d="M 150 150 C 300 150, 300 80, 450 80" fill="none" stroke="#3F3F46" strokeWidth="1" />
              <path d="M 150 150 C 300 150, 300 220, 450 220" fill="none" stroke="#F59E0B" strokeWidth="1.5" strokeDasharray="4 4" className="animate-pulse" />
              <path d="M 450 80 C 600 80, 600 150, 750 150" fill="none" stroke="#3B82F6" strokeWidth="1.5" strokeDasharray="4 8" className="animate-[dash_2s_linear_infinite]" />
            </svg>
          </WorkspaceGrid>
        </DockLayout>
      </div>

      {/* RIGHT: Intelligence Rail */}
      <Surface variant="panel" border="strong" className="w-[320px] shrink-0 border-y-0 border-r-0 flex flex-col h-full bg-surface-elevated z-10">
        <ScrollableArea className="flex-1 p-4">
          <Stack gap={6}>
            <Section title="AI System Insights">
              <Stack gap={2}>
                <Panel padding="sm" className="border-border-subtle hover:border-border-strong cursor-default transition-colors">
                  <Stack gap={2}>
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="size-3.5 text-success" />
                      <span className="text-xs font-medium">Consensus Alignment</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-mono">94.2%</span>
                      <span className="text-2xs text-muted">Last 1h</span>
                    </div>
                    <span className="text-2xs text-muted">Agreement rate across all multi-agent committees is stable.</span>
                  </Stack>
                </Panel>

                <Panel padding="sm" className="border-border-subtle hover:border-border-strong cursor-default transition-colors">
                  <Stack gap={2}>
                    <div className="flex items-center gap-2">
                      <Activity className="size-3.5 text-accent" />
                      <span className="text-xs font-medium">Hallucination Rejection</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-mono">{formatNumber(142)}</span>
                      <span className="text-2xs text-muted">Last 1h</span>
                    </div>
                    <span className="text-2xs text-muted">Validators successfully caught and rejected 142 outputs.</span>
                  </Stack>
                </Panel>
              </Stack>
            </Section>

            <Section title="Token Spend Velocity">
              <Panel padding="sm" className="border-border-subtle">
                <Stack gap={4}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted">Current Rate</span>
                    <span className="text-xs font-mono text-foreground">{formatNumber(450)} tk/s</span>
                  </div>
                  {/* CSS-based Sparkline stub for visual density */}
                  <div className="h-12 w-full flex items-end gap-0.5 opacity-80">
                    {[3,5,2,8,4,9,5,7,4,6,8,5,10,7,5,4].map((v, i) => (
                      <div key={i} className="flex-1 bg-accent rounded-t-[1px]" style={{ height: `${v * 10}%` }} />
                    ))}
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-border-subtle">
                    <span className="text-2xs text-muted">1h Total</span>
                    <span className="text-2xs font-mono text-foreground">{formatNumber(1620000)} tokens</span>
                  </div>
                </Stack>
              </Panel>
            </Section>

          </Stack>
        </ScrollableArea>
      </Surface>
    </div>
  );
}

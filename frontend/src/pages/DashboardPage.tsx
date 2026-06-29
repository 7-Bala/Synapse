import { useEffect } from 'react';
import { Surface } from '@/design-system/primitives/Surface';
import { Panel } from '@/design-system/primitives/Panel';
import { Stack } from '@/design-system/primitives/Stack';
import { Section } from '@/design-system/primitives/Section';
import { DockLayout } from '@/design-system/layout/DockLayout';
import { WorkspaceGrid } from '@/design-system/layout/WorkspaceGrid';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { PlayCircle, Terminal } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useExecutionStore } from '@/stores/executionStore';

function ExecutionNodeComponent({ 
  label, 
  status, 
  x, 
  y, 
  selected, 
  onClick 
}: { 
  id: string, 
  label: string, 
  status: 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED' | 'BLOCKED', 
  x: number, 
  y: number,
  selected: boolean,
  onClick: () => void 
}) {
  return (
    <div 
      onClick={onClick}
      className={cn(
        "absolute flex items-center justify-center p-2 bg-surface-elevated border rounded-[8px] shadow-panel hover:z-10 cursor-pointer transition-colors",
        status === 'RUNNING' ? 'border-accent shadow-glow' : 
        status === 'FAILED' ? 'border-danger shadow-glow-danger' : 
        status === 'COMPLETE' ? 'border-success' : 
        status === 'BLOCKED' ? 'border-warning shadow-glow-warning' : 'border-border-subtle',
        selected && 'ring-2 ring-accent/50'
      )}
      style={{ left: x, top: y }}
    >
      <div className="flex flex-col items-center gap-1.5 min-w-[80px]">
        <div className={cn("size-2 rounded-full", 
          status === 'RUNNING' ? 'bg-accent animate-pulse' : 
          status === 'FAILED' ? 'bg-danger' : 
          status === 'COMPLETE' ? 'bg-success' : 
          status === 'BLOCKED' ? 'bg-warning animate-pulse' : 'bg-muted')} 
        />
        <span className="text-2xs font-mono text-muted uppercase hover:text-foreground transition-colors">{label}</span>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { 
    connectionStatus, 
    executionStatus, 
    executionGraph, 
    events, 
    connect, 
    selectedNode, 
    selectNode 
  } = useExecutionStore();

  useEffect(() => {
    connect();
  }, [connect]);

  const triggerDemo = async () => {
    try {
      await fetch('http://localhost:8000/demo/start', { method: 'POST' });
    } catch (e) {
      console.error('Failed to trigger demo', e);
    }
  };

  const selectedNodeData = executionGraph?.nodes.find(n => n.id === selectedNode);

  return (
    <div className="flex w-full h-full">
      {/* LEFT: Operations Rail */}
      <Surface variant="panel" border="strong" className="w-[300px] shrink-0 border-y-0 border-l-0 flex flex-col h-full bg-surface-elevated z-10">
        <ScrollableArea className="flex-1 p-4">
          <Stack gap={6}>
            <Section title="Quick Actions">
              <Stack gap={2}>
                <button 
                  onClick={triggerDemo}
                  className="flex items-center gap-2 w-full p-2 text-xs text-foreground hover:bg-accent/10 border border-border-subtle hover:border-accent/50 rounded transition-colors text-left font-medium"
                >
                  <PlayCircle className="size-3.5 text-accent" />
                  Start Demo Execution
                </button>
              </Stack>
            </Section>

            <Section title="Connection Status">
              <Panel padding="sm">
                <Stack gap={1}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium">Backend</span>
                    <span className={cn(
                      "text-2xs font-mono uppercase tracking-wider",
                      connectionStatus === 'connected' ? 'text-success' : 'text-danger'
                    )}>
                      {connectionStatus === 'connected' ? 'Orchestrator Connected' : 'Orchestrator Offline'}
                    </span>
                  </div>
                </Stack>
              </Panel>
            </Section>

            <Section title="Execution Status">
              <Panel padding="sm">
                <Stack gap={1}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium">Status</span>
                    <span className="text-2xs font-mono uppercase tracking-wider text-accent">
                      {executionStatus}
                    </span>
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
                {connectionStatus === 'connected' && (
                  <span className="text-2xs text-muted flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
                    </span>
                    Streaming
                  </span>
                )}
              </div>
              <ScrollableArea className="flex-1 p-4 bg-background font-mono text-2xs leading-relaxed">
                <Stack gap={1}>
                  {events.map((evt, idx) => (
                    <div key={idx} className="flex gap-4 hover:bg-surface-elevated px-2 py-0.5 rounded transition-colors">
                      <span className="text-muted w-24 shrink-0 truncate">{evt.timestamp.split('T')[1]?.slice(0,12) || evt.timestamp}</span>
                      <span className="text-accent w-32 shrink-0 truncate">[{evt.type}]</span>
                      <span className="text-foreground truncate">{JSON.stringify(evt.payload)}</span>
                    </div>
                  ))}
                  {events.length === 0 && (
                    <div className="text-muted italic">No events yet...</div>
                  )}
                </Stack>
              </ScrollableArea>
            </div>
          }
        >
          <WorkspaceGrid gridSize={30}>
            {/* Global Topology Heatmap Overlay */}
            <div className="absolute inset-0 p-6 pointer-events-none z-10 flex justify-between items-start">
              <Stack gap={1}>
                <h2 className="text-lg font-sans font-semibold tracking-tight text-foreground drop-shadow-md">Execution Topology</h2>
                {!executionGraph && (
                  <span className="text-xs font-mono text-muted uppercase tracking-wider">No Active Execution</span>
                )}
              </Stack>
            </div>

            {/* Simulated Nodes & Dynamic Graph */}
            {!executionGraph && (
              <div className="absolute inset-0 flex items-center justify-center">
                <Stack gap={4} className="items-center">
                  <Terminal className="size-12 text-muted" />
                  <div className="text-muted text-sm uppercase tracking-widest font-mono">Connect to an Orchestrator or Start a New Execution</div>
                  <button onClick={triggerDemo} className="px-4 py-2 border border-accent text-accent rounded hover:bg-accent/10 transition-colors text-xs font-mono uppercase tracking-widest">Start Demo Execution</button>
                </Stack>
              </div>
            )}

            {executionGraph && executionGraph.nodes.map((node, index) => {
              // Basic linear layout for demo purposes
              const x = 100 + (index * 200);
              const y = 150;
              return (
                <ExecutionNodeComponent 
                  key={node.id}
                  id={node.id}
                  label={node.agentName || node.id}
                  status={node.status}
                  x={x}
                  y={y}
                  selected={selectedNode === node.id}
                  onClick={() => selectNode(node.id)}
                />
              );
            })}
            
            {/* Connecting Lines for sequential nodes */}
            {executionGraph && executionGraph.nodes.map((_, index) => {
              if (index === executionGraph.nodes.length - 1) return null;
              const x1 = 100 + (index * 200) + 100;
              const y1 = 150 + 20;
              const x2 = 100 + ((index + 1) * 200);
              
              const isRunning = executionGraph.nodes[index + 1].status === 'RUNNING';
              
              return (
                <svg key={`edge-${index}`} className="absolute inset-0 w-full h-full pointer-events-none">
                  <path 
                    d={`M ${x1} ${y1} L ${x2} ${y1}`} 
                    fill="none" 
                    stroke={isRunning ? "#3B82F6" : "#3F3F46"} 
                    strokeWidth={isRunning ? "1.5" : "1"} 
                    strokeDasharray={isRunning ? "4 8" : "none"} 
                    className={isRunning ? "animate-[dash_2s_linear_infinite]" : ""}
                  />
                </svg>
              );
            })}
          </WorkspaceGrid>
        </DockLayout>
      </div>

      {/* RIGHT: Execution Inspector */}
      <Surface variant="panel" border="strong" className="w-[320px] shrink-0 border-y-0 border-r-0 flex flex-col h-full bg-surface-elevated z-10">
        <ScrollableArea className="flex-1 p-4">
          <Stack gap={6}>
            <Section title="Execution Inspector">
              {selectedNodeData ? (
                <Stack gap={4}>
                  <Panel padding="sm" className="border-border-subtle">
                    <Stack gap={2}>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted">Agent Name</span>
                        <span className="text-xs font-mono font-medium text-foreground">{selectedNodeData.agentName}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted">Status</span>
                        <span className="text-xs font-mono font-medium text-accent">{selectedNodeData.status}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted">Latency</span>
                        <span className="text-xs font-mono text-muted">-- ms</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted">Token Usage</span>
                        <span className="text-xs font-mono text-muted">--</span>
                      </div>
                    </Stack>
                  </Panel>

                  <Panel padding="sm" className="border-border-subtle">
                    <Stack gap={2}>
                      <span className="text-xs text-muted">Reasoning</span>
                      <span className="text-2xs text-foreground/80 italic font-mono">
                        (Reasoning trace not yet available for this node)
                      </span>
                    </Stack>
                  </Panel>

                  <Panel padding="sm" className="border-border-subtle">
                    <Stack gap={2}>
                      <span className="text-xs text-muted">Prompt</span>
                      <span className="text-2xs text-foreground/80 italic font-mono">
                        (Prompt data placeholder)
                      </span>
                    </Stack>
                  </Panel>
                  
                  <Panel padding="sm" className="border-border-subtle">
                    <Stack gap={2}>
                      <span className="text-xs text-muted">Evidence References</span>
                      <span className="text-2xs text-foreground/80 italic font-mono">
                        (No evidence attached)
                      </span>
                    </Stack>
                  </Panel>
                </Stack>
              ) : (
                <div className="text-2xs text-muted italic p-4 text-center">
                  Select a node to inspect its execution trace.
                </div>
              )}
            </Section>
          </Stack>
        </ScrollableArea>
      </Surface>
    </div>
  );
}

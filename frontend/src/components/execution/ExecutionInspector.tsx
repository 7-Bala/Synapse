import { Surface } from '@/design-system/primitives/Surface';
import { Panel } from '@/design-system/primitives/Panel';
import { Stack } from '@/design-system/primitives/Stack';
import { Section } from '@/design-system/primitives/Section';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { useExecutionStore } from '@/stores/executionStore';

export function ExecutionInspector() {
  const { executionGraph, selectedNode } = useExecutionStore();
  const selectedNodeData = executionGraph?.nodes.find(n => n.id === selectedNode);

  return (
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
                      <span className="text-xs font-mono text-muted">Waiting for Runtime Telemetry.</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted">Tokens</span>
                      <span className="text-xs font-mono text-muted">Waiting for Telemetry Stream.</span>
                    </div>
                  </Stack>
                </Panel>

                <Panel padding="sm" className="border-border-subtle">
                  <Stack gap={2}>
                    <span className="text-xs text-muted">Reasoning</span>
                    <span className="text-2xs text-muted font-mono italic">
                      Waiting for Agent Reasoning Stream.
                    </span>
                  </Stack>
                </Panel>

                <Panel padding="sm" className="border-border-subtle">
                  <Stack gap={2}>
                    <span className="text-xs text-muted">Prompt</span>
                    <span className="text-2xs text-muted font-mono italic">
                      Waiting for Prompt Telemetry Pipeline.
                    </span>
                  </Stack>
                </Panel>
                
                <Panel padding="sm" className="border-border-subtle">
                  <Stack gap={2}>
                    <span className="text-xs text-muted">Evidence References</span>
                    <span className="text-2xs text-muted font-mono italic">
                      Waiting for Evidence Pipeline.
                    </span>
                  </Stack>
                </Panel>
              </Stack>
            ) : (
              <div className="flex flex-col items-center justify-center h-48 text-center text-muted">
                <p className="text-sm">No node selected.</p>
                <p className="text-xs mt-1">Select an agent node in the topology to inspect its runtime state.</p>
              </div>
            )}
          </Section>
        </Stack>
      </ScrollableArea>
    </Surface>
  );
}

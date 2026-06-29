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
  );
}

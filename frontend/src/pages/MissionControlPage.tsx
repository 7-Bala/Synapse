import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { Stack } from '@/design-system/primitives/Stack';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { LiveEventStream } from '@/components/mission-control/LiveEventStream';
import { OperationsPanel } from '@/components/mission-control/OperationsPanel';
import { ConnectionStatusPanel } from '@/components/mission-control/ConnectionStatusPanel';
import { useExecutionStore } from '@/stores/executionStore';

export function MissionControlPage() {
  const { isConnected, events } = useExecutionStore();

  return (
    <WorkspaceLayout
      title="Mission Control"
      description="What is happening right now?"
      state={isConnected ? 'ready' : 'disconnected'}
    >
      <div className="flex flex-col w-full h-full p-6 gap-6 bg-background-dark">
        {/* TOP ROW */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 shrink-0">
          <Surface variant="panel" border="strong" className="bg-surface-elevated overflow-visible">
            <ConnectionStatusPanel />
          </Surface>
          
          <Surface variant="panel" border="strong" className="bg-surface-elevated col-span-1 lg:col-span-2">
             <div className="p-4 flex flex-col h-full justify-between">
                <span className="text-sm font-medium text-foreground tracking-tight">Active Execution</span>
                <div className="text-xs text-muted mt-2">
                   {events.length > 0 ? "Tracking live runtime metrics." : "No orchestrations currently active. Ready for instructions."}
                </div>
             </div>
          </Surface>

          <Surface variant="panel" border="strong" className="bg-surface-elevated">
            <div className="p-4 h-full">
               <OperationsPanel />
            </div>
          </Surface>
        </div>

        {/* MIDDLE ROW */}
        <div className="flex-1 min-h-[300px] border border-border-strong rounded-lg overflow-hidden">
          <LiveEventStream />
        </div>

        {/* BOTTOM ROW */}
        <Surface variant="panel" border="strong" className="shrink-0 h-[200px] bg-surface-elevated">
           <div className="p-4 flex flex-col h-full">
              <span className="text-sm font-medium text-foreground tracking-tight mb-4">Recent Runtime Activity</span>
              <ScrollableArea className="flex-1">
                 {events.length > 0 ? (
                   <Stack gap={2}>
                     {events.slice(-5).reverse().map((e, i) => (
                       <div key={i} className="flex justify-between items-center px-3 py-2 bg-surface border border-border-subtle rounded text-xs">
                          <span className="text-muted font-mono">{e.timestamp.split('T')[1]?.slice(0,8)}</span>
                          <span className="font-medium text-foreground">{e.type}</span>
                       </div>
                     ))}
                   </Stack>
                 ) : (
                   <div className="flex items-center justify-center h-full text-xs text-muted italic">
                      Awaiting telemetry from the runtime...
                   </div>
                 )}
              </ScrollableArea>
           </div>
        </Surface>
      </div>
    </WorkspaceLayout>
  );
}

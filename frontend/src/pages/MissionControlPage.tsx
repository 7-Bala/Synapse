import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { Stack } from '@/design-system/primitives/Stack';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { LiveEventStream } from '@/components/mission-control/LiveEventStream';
import { OperationsPanel } from '@/components/mission-control/OperationsPanel';
import { ConnectionStatusPanel } from '@/components/mission-control/ConnectionStatusPanel';
import { useExecutionStore } from '@/stores/executionStore';

export function MissionControlPage() {
  const { isConnected } = useExecutionStore();

  return (
    <WorkspaceLayout
      title="Mission Control"
      description="What is happening right now?"
      state={isConnected ? 'ready' : 'disconnected'}
    >
      <div className="flex w-full h-full">
        {/* LEFT: Operations Rail */}
        <Surface variant="panel" border="strong" className="w-[300px] shrink-0 border-y-0 border-l-0 flex flex-col h-full bg-surface-elevated z-10">
          <ScrollableArea className="flex-1 p-4">
            <Stack gap={6}>
              <OperationsPanel />
              <ConnectionStatusPanel />
            </Stack>
          </ScrollableArea>
        </Surface>

        {/* RIGHT: Live Event Stream */}
        <div className="flex-1 p-6 h-full">
          <LiveEventStream />
        </div>
      </div>
    </WorkspaceLayout>
  );
}

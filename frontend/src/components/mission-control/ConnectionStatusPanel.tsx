import { Panel } from '@/design-system/primitives/Panel';
import { Stack } from '@/design-system/primitives/Stack';
import { Section } from '@/design-system/primitives/Section';
import { cn } from '@/lib/utils';
import { useExecutionStore } from '@/stores/executionStore';

export function ConnectionStatusPanel() {
  const { connectionStatus, executionStatus } = useExecutionStore();

  return (
    <Section title="Connection Status">
      <Panel padding="sm">
        <Stack gap={1}>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted">Orchestrator</span>
            <span className={cn(
              "text-xs font-mono font-medium",
              connectionStatus === 'connected' ? "text-success" :
              connectionStatus === 'connecting' ? "text-warning animate-pulse" :
              "text-danger"
            )}>
              {connectionStatus.toUpperCase()}
            </span>
          </div>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-border-subtle">
            <span className="text-xs text-muted">Execution Engine</span>
            <span className={cn(
              "text-xs font-mono font-medium",
              executionStatus === 'RUNNING' ? "text-accent animate-pulse" :
              executionStatus === 'FINISHED' ? "text-success" :
              executionStatus === 'FAILED' ? "text-danger" :
              "text-muted"
            )}>
              {executionStatus}
            </span>
          </div>
        </Stack>
      </Panel>
    </Section>
  );
}

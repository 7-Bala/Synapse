import { Stack } from '@/design-system/primitives/Stack';
import { Section } from '@/design-system/primitives/Section';
import { PlayCircle, RefreshCw, Trash2 } from 'lucide-react';
import { useExecutionStore } from '@/stores/executionStore';

export function OperationsPanel() {
  const { connect } = useExecutionStore();

  const triggerDemo = async () => {
    try {
      await fetch('http://localhost:8000/demo/start', { method: 'POST' });
    } catch (e) {
      console.error('Failed to trigger demo', e);
    }
  };

  const handleReconnect = () => {
    connect();
  };

  const handleClearEvents = () => {
    useExecutionStore.setState({ events: [], executionGraph: null, executionStatus: 'IDLE', selectedNode: null });
  };

  return (
    <Section title="Operations">
      <Stack gap={2}>
        <button 
          onClick={triggerDemo}
          className="flex items-center justify-between w-full p-2.5 text-xs text-foreground bg-surface border border-border-subtle hover:border-accent/50 hover:bg-accent/5 rounded transition-colors font-medium group"
        >
          <div className="flex items-center gap-2">
            <PlayCircle className="size-4 text-accent" />
            Start Demo Execution
          </div>
        </button>

        <button 
          onClick={handleReconnect}
          className="flex items-center justify-between w-full p-2.5 text-xs text-foreground bg-surface border border-border-subtle hover:border-accent/50 hover:bg-accent/5 rounded transition-colors font-medium group"
        >
          <div className="flex items-center gap-2">
            <RefreshCw className="size-4 text-muted group-hover:text-accent transition-colors" />
            Reconnect Runtime
          </div>
        </button>

        <button 
          onClick={handleClearEvents}
          className="flex items-center justify-between w-full p-2.5 text-xs text-foreground bg-surface border border-border-subtle hover:border-danger/50 hover:bg-danger/5 rounded transition-colors font-medium group"
        >
          <div className="flex items-center gap-2">
            <Trash2 className="size-4 text-muted group-hover:text-danger transition-colors" />
            Clear Local State
          </div>
        </button>
      </Stack>
    </Section>
  );
}

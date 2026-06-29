import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { Stack } from '@/design-system/primitives/Stack';
import { useExecutionStore } from '@/stores/executionStore';

export function LiveEventStream() {
  const { connectionStatus, events } = useExecutionStore();

  return (
    <div className="flex flex-col h-full bg-surface-elevated rounded-md border border-border-subtle overflow-hidden">
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
  );
}

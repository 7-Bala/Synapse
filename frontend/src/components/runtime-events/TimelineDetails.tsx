import { useTimelineStore } from '@/stores/timelineStore';
import { Copy, X } from 'lucide-react';
import { getEventSeverity } from '@/lib/events/severity';
import { cn } from '@/lib/utils';
import { Section } from '@/design-system/primitives/Section';
import { Panel } from '@/design-system/primitives/Panel';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';

export function TimelineDetails({ eventId }: { eventId: string }) {
  const { events, selectEvent } = useTimelineStore();
  const event = events.find(e => e.id === eventId);

  if (!event) return null;

  const severity = getEventSeverity(event.type);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-surface">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-foreground tracking-tight">{event.type}</span>
          <span className={cn(
             "px-1.5 py-0.5 rounded text-2xs font-mono uppercase tracking-wider",
             severity === 'INFO' && "bg-surface border border-border-subtle text-foreground",
             severity === 'SUCCESS' && "bg-success/10 text-success border border-success/20",
             severity === 'WARNING' && "bg-warning/10 text-warning border border-warning/20",
             severity === 'ERROR' && "bg-danger/10 text-danger border border-danger/20",
             severity === 'UNKNOWN' && "bg-surface border border-border-subtle text-muted"
          )}>
            {severity}
          </span>
        </div>
        <button 
          onClick={() => selectEvent(null)}
          className="p-1 rounded text-muted hover:text-foreground hover:bg-surface-elevated transition-colors"
        >
          <X className="size-4" />
        </button>
      </div>

      <ScrollableArea className="flex-1 p-4">
        <Section title="Event Metadata" className="mb-6">
          <Panel padding="sm" className="border-border-subtle">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted">Event ID</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono truncate max-w-[150px]">{event.id}</span>
                  <button onClick={() => copyToClipboard(event.id)} className="text-muted hover:text-accent"><Copy className="size-3" /></button>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted">Timestamp</span>
                <span className="text-xs font-mono">{event.timestamp}</span>
              </div>
              {event.executionId && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted">Execution</span>
                  <span className="text-xs font-mono">{event.executionId}</span>
                </div>
              )}
            </div>
          </Panel>
        </Section>

        <Section title="Raw Payload" className="mb-6">
           <Panel padding="sm" className="bg-background-dark border-border-subtle relative group">
              <button 
                onClick={() => copyToClipboard(JSON.stringify(event.payload, null, 2))}
                className="absolute top-2 right-2 p-1.5 bg-surface border border-border-subtle rounded text-muted hover:text-accent opacity-0 group-hover:opacity-100 transition-opacity z-10"
                title="Copy JSON"
              >
                <Copy className="size-3" />
              </button>
              <pre className="text-2xs font-mono text-muted overflow-x-auto">
                 {JSON.stringify(event.payload || {}, null, 2)}
              </pre>
           </Panel>
        </Section>
      </ScrollableArea>
    </div>
  );
}

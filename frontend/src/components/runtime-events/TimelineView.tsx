import { useEffect, useRef, useMemo } from 'react';
import { useTimelineStore } from '@/stores/timelineStore';
import { TimelineEmptyState } from './TimelineEmptyState';
import { TimelineGroup } from './TimelineGroup';
import type { EventEnvelope } from '@/types/events';

interface TimelineViewProps {
  compact?: boolean;
}

export function TimelineView({ compact: _compact }: TimelineViewProps) {
  const { 
    events, 
    selectedEventId, 
    pinnedEventIds, 
    searchQuery, 
    autoScroll,
    selectEvent,
    togglePin
  } = useTimelineStore();
  
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logic
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events.length, autoScroll]);

  // Derived state: Filter & Search
  const filteredEvents = useMemo(() => {
    if (!searchQuery) return events;
    const query = searchQuery.toLowerCase();
    return events.filter(e => {
      if (e.type.toLowerCase().includes(query)) return true;
      if (e.id.toLowerCase().includes(query)) return true;
      if (e.executionId?.toLowerCase().includes(query)) return true;
      if (e.payload) {
         try {
           return JSON.stringify(e.payload).toLowerCase().includes(query);
         } catch {
           return false;
         }
      }
      return false;
    });
  }, [events, searchQuery]);

  // Derived state: Grouping (Execution -> Tick -> Agent)
  const groupedEvents = useMemo(() => {
    // For compact mode or when searching, just flat list might be better, 
    // but the spec says automatically group. We will do a simplistic grouping 
    // for this sprint, grouping by Execution.
    const byExecution: Record<string, EventEnvelope<any>[]> = {};
    const fallbackExecId = 'execution-unknown';

    filteredEvents.forEach(e => {
      const execId = e.executionId || fallbackExecId;
      if (!byExecution[execId]) byExecution[execId] = [];
      byExecution[execId].push(e);
    });

    return byExecution;
  }, [filteredEvents]);

  if (filteredEvents.length === 0) {
    return <TimelineEmptyState />;
  }

  return (
    <div 
      ref={scrollRef}
      className="flex-1 overflow-y-auto overflow-x-hidden p-4 relative scroll-smooth"
    >
      <div className="absolute left-[116px] top-4 bottom-4 w-px bg-border-subtle pointer-events-none" />
      
      <div className="flex flex-col gap-6">
        {Object.entries(groupedEvents).map(([execId, execEvents]) => (
          <div key={execId} className="flex flex-col relative z-0">
             {/* Simple grouped display by execution */}
             <TimelineGroup 
                label={`Execution: ${execId}`}
                type="execution"
                events={execEvents}
                selectedEventId={selectedEventId}
                pinnedEventIds={pinnedEventIds}
                onSelectEvent={selectEvent}
                onTogglePin={togglePin}
             />
          </div>
        ))}
      </div>
    </div>
  );
}

import { useState } from 'react';
import { TimelineView } from '@/components/runtime-events/TimelineView';
import { useTimelineStore } from '@/stores/timelineStore';
import { TimelineDetails } from '@/components/runtime-events/TimelineDetails';
import { TimelineToolbar, type RuntimeEventView } from '@/components/runtime-events/TimelineToolbar';

export interface RuntimeEventExplorerProps {
  compact?: boolean;
}
export function RuntimeEventExplorer({ compact = false }: RuntimeEventExplorerProps) {
  const [view, setView] = useState<RuntimeEventView>('timeline');
  const { selectedEventId } = useTimelineStore();

  return (
    <div className="flex flex-col w-full h-full bg-background-dark border border-border-strong rounded-lg overflow-hidden">
      <TimelineToolbar currentView={view} onViewChange={setView} compact={compact} />
      
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 min-w-0 flex flex-col relative">
          {view === 'timeline' && <TimelineView compact={compact} />}
          {/* Other views will go here in future sprints */}
        </div>
        
        {selectedEventId && !compact && (
          <div className="w-[400px] shrink-0 border-l border-border-subtle bg-surface-elevated flex flex-col">
            <TimelineDetails eventId={selectedEventId} />
          </div>
        )}
      </div>
    </div>
  );
}

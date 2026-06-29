import { Play, Pause, ArrowDownToLine, Trash2 } from 'lucide-react';
import { useTimelineStore } from '@/stores/timelineStore';
import { TimelineSearch } from './TimelineSearch';
import { TimelineFilters } from './TimelineFilters';
import { cn } from '@/lib/utils';

export type RuntimeEventView = 'timeline' | 'tree' | 'json' | 'agent' | 'tick';

interface TimelineToolbarProps {
  currentView: RuntimeEventView;
  onViewChange: (view: RuntimeEventView) => void;
  compact?: boolean;
}

export function TimelineToolbar({ currentView, onViewChange, compact }: TimelineToolbarProps) {
  const { paused, togglePause, autoScroll, toggleAutoScroll, clearEvents } = useTimelineStore();

  return (
    <div className="flex flex-none items-center justify-between px-4 py-2 border-b border-border-subtle bg-surface z-10 sticky top-0">
      <div className="flex items-center gap-4">
        {!compact && (
          <div className="flex items-center gap-1 bg-background-dark p-1 rounded-md border border-border-subtle">
            <button
              className={cn("px-3 py-1 text-xs font-medium rounded transition-colors", currentView === 'timeline' ? "bg-surface-elevated text-foreground shadow-sm" : "text-muted hover:text-foreground")}
              onClick={() => onViewChange('timeline')}
            >
              Timeline
            </button>
            <button
              className={cn("px-3 py-1 text-xs font-medium rounded transition-colors", currentView === 'tree' ? "bg-surface-elevated text-foreground shadow-sm" : "text-muted hover:text-foreground opacity-50 cursor-not-allowed")}
            >
              Tree
            </button>
          </div>
        )}
        <TimelineSearch />
        <TimelineFilters />
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleAutoScroll}
          className={cn("p-1.5 rounded transition-colors border", autoScroll ? "bg-accent/10 text-accent border-accent/20" : "text-muted border-transparent hover:bg-surface-elevated")}
          title="Auto-scroll"
        >
          <ArrowDownToLine className="size-4" />
        </button>

        <button
          onClick={togglePause}
          className={cn("p-1.5 rounded transition-colors border", paused ? "bg-warning/10 text-warning border-warning/20" : "text-muted border-transparent hover:bg-surface-elevated")}
          title={paused ? "Resume Live Updates" : "Pause Live Updates"}
        >
          {paused ? <Play className="size-4" /> : <Pause className="size-4" />}
        </button>

        {!compact && (
          <button
            onClick={clearEvents}
            className="p-1.5 rounded transition-colors border border-transparent text-muted hover:text-danger hover:bg-danger/10"
            title="Clear Local Timeline"
          >
            <Trash2 className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
}

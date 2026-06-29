import { Filter } from 'lucide-react';
import { useTimelineStore } from '@/stores/timelineStore';

export function TimelineFilters() {
  const { filters } = useTimelineStore();

  // For Sprint 6, we keep it as a placeholder trigger, as a full robust filtering dropdown
  // is complex. We show the active filter count.
  const activeCount = filters.types.length + filters.agents.length + filters.ticks.length + filters.severities.length;

  return (
    <button className="flex items-center gap-1.5 px-3 py-1 h-7 text-xs font-medium bg-surface border border-border-subtle rounded text-foreground hover:bg-surface-elevated transition-colors">
      <Filter className="size-3.5 text-muted" />
      <span>Filter</span>
      {activeCount > 0 && (
        <span className="flex items-center justify-center h-4 w-4 rounded-full bg-accent text-accent-foreground text-[10px] ml-1">
          {activeCount}
        </span>
      )}
    </button>
  );
}

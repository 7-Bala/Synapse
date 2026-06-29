import { memo } from 'react';
import { cn } from '@/lib/utils';
import { getEventSeverity } from '@/lib/events/severity';
import type { EventEnvelope } from '@/types/events';
import { motion } from 'framer-motion';
import { Pin } from 'lucide-react';

interface TimelineItemProps {
  event: EventEnvelope<any>;
  isSelected: boolean;
  isPinned: boolean;
  onSelect: (id: string) => void;
  onTogglePin: (id: string) => void;
}

export const TimelineItem = memo(function TimelineItem({
  event,
  isSelected,
  isPinned,
  onSelect,
  onTogglePin
}: TimelineItemProps) {
  const severity = getEventSeverity(event.type);
  const time = event.timestamp.split('T')[1]?.slice(0, 8) || event.timestamp;

  const severityStyles = {
    INFO: 'bg-surface border-border-subtle hover:border-border text-foreground',
    SUCCESS: 'bg-success/5 border-success/20 hover:border-success/40 text-success',
    WARNING: 'bg-warning/5 border-warning/20 hover:border-warning/40 text-warning',
    ERROR: 'bg-danger/5 border-danger/20 hover:border-danger/40 text-danger',
    UNKNOWN: 'bg-surface border-border-subtle hover:border-border text-muted',
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative flex items-stretch group/item"
    >
      <div className="w-[100px] shrink-0 pr-4 flex flex-col justify-center text-right border-r border-border-subtle">
        <span className="text-2xs font-mono text-muted">{time}</span>
      </div>
      
      {/* Node connector dot */}
      <div className="absolute left-[100px] top-1/2 -translate-x-1/2 -translate-y-1/2 size-2 rounded-full bg-border-strong border-2 border-background-dark z-10" />

      <div className="flex-1 pl-6 py-1.5">
        <button
          onClick={() => onSelect(event.id)}
          className={cn(
            "w-full text-left flex items-center justify-between px-3 py-2 rounded text-xs font-mono border transition-all cursor-pointer relative",
            severityStyles[severity],
            isSelected ? 'ring-1 ring-accent ring-offset-1 ring-offset-background-dark shadow-sm' : ''
          )}
        >
          <div className="flex items-center gap-3 truncate">
            <span className="font-semibold truncate">{event.type}</span>
          </div>

          <div className="flex items-center gap-2 opacity-0 group-hover/item:opacity-100 transition-opacity">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onTogglePin(event.id);
              }}
              className={cn(
                "p-1 rounded hover:bg-surface-elevated transition-colors",
                isPinned ? "text-accent opacity-100" : "text-muted"
              )}
            >
              <Pin className="size-3" />
            </button>
          </div>
          
          {isPinned && !isSelected && (
            <div className="absolute top-1.5 right-1.5 opacity-100 lg:hidden">
              <Pin className="size-3 text-accent" />
            </div>
          )}
        </button>
      </div>
    </motion.div>
  );
});

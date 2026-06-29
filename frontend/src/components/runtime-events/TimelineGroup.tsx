import { memo, useState } from 'react';
import { ChevronDown, ChevronRight, User } from 'lucide-react';
import { TimelineItem } from './TimelineItem';
import { motion, AnimatePresence } from 'framer-motion';
import type { EventEnvelope } from '@/types/events';

interface TimelineGroupProps {
  label: string;
  type: 'execution' | 'tick' | 'agent';
  events: EventEnvelope<any>[];
  selectedEventId: string | null;
  pinnedEventIds: Set<string>;
  onSelectEvent: (id: string) => void;
  onTogglePin: (id: string) => void;
}

export const TimelineGroup = memo(function TimelineGroup({
  label,
  type,
  events,
  selectedEventId,
  pinnedEventIds,
  onSelectEvent,
  onTogglePin
}: TimelineGroupProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const getLabelStyles = () => {
    switch(type) {
      case 'execution': return 'text-accent font-semibold text-xs tracking-wider uppercase';
      case 'tick': return 'text-foreground font-medium text-xs';
      case 'agent': return 'text-muted font-medium text-xs flex items-center gap-1.5';
    }
  };

  const getLeftPadding = () => {
    switch(type) {
      case 'execution': return 'pl-0';
      case 'tick': return 'pl-2';
      case 'agent': return 'pl-4';
    }
  };

  return (
    <div className={getLeftPadding()}>
      <div 
        className="flex items-center gap-2 py-2 cursor-pointer sticky top-0 bg-background-dark z-20 hover:bg-surface/50 rounded pr-2"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <button className="p-0.5 text-muted hover:text-foreground rounded transition-colors">
          {isCollapsed ? <ChevronRight className="size-3.5" /> : <ChevronDown className="size-3.5" />}
        </button>
        <span className={getLabelStyles()}>
          {type === 'agent' && <User className="size-3.5" />}
          {label}
        </span>
        <span className="text-2xs text-muted font-mono ml-auto bg-surface px-1.5 py-0.5 rounded">
          {events.length}
        </span>
      </div>
      
      <AnimatePresence initial={false}>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col relative"
          >
            {events.map(event => (
              <TimelineItem
                key={event.id}
                event={event}
                isSelected={selectedEventId === event.id}
                isPinned={pinnedEventIds.has(event.id)}
                onSelect={onSelectEvent}
                onTogglePin={onTogglePin}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

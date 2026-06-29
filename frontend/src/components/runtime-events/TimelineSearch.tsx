import { Search } from 'lucide-react';
import { useTimelineStore } from '@/stores/timelineStore';
import { useState, useEffect } from 'react';

export function TimelineSearch() {
  const { searchQuery, setSearchQuery } = useTimelineStore();
  const [localQuery, setLocalQuery] = useState(searchQuery);

  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(localQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [localQuery, setSearchQuery]);

  return (
    <div className="relative">
      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-muted" />
      <input 
        type="text" 
        placeholder="Search events..."
        value={localQuery}
        onChange={(e) => setLocalQuery(e.target.value)}
        className="h-7 w-[200px] pl-8 pr-3 text-xs bg-surface border border-border-subtle rounded text-foreground placeholder:text-muted focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/50 transition-all"
      />
    </div>
  );
}

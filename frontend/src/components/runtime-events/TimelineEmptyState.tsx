import { Inbox } from 'lucide-react';

export function TimelineEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-muted p-8">
      <Inbox className="size-8 mb-4 opacity-50" />
      <h3 className="text-sm font-medium text-foreground mb-1">No Events Found</h3>
      <p className="text-xs text-center max-w-[250px]">
        The runtime event stream is currently empty or no events match your filters.
      </p>
    </div>
  );
}

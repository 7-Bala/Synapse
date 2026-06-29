import { Circle, Wifi } from 'lucide-react';
import { Surface } from '@/design-system/primitives/Surface';

export function BottomUtilities() {
  return (
    <Surface variant="default" border="subtle" className="h-8 shrink-0 flex items-center justify-between px-4 z-50">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-success">
          <Circle className="size-2 fill-current" />
          <span className="text-2xs font-mono uppercase tracking-widest">Sys: Healthy</span>
        </div>
        <div className="flex items-center gap-2 text-muted">
          <span className="text-2xs font-mono">Latency: 12ms</span>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-muted">
          <Wifi className="size-3" />
          <span className="text-2xs font-mono uppercase tracking-widest">WS: Connected</span>
        </div>
        <div className="flex items-center gap-2 text-muted">
          <span className="text-2xs font-mono">v2.0.0-rc.1</span>
        </div>
      </div>
    </Surface>
  );
}

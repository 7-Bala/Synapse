import { cn } from '@/lib/utils';

interface ExecutionNodeProps {
  id: string;
  label: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED' | 'BLOCKED';
  x: number;
  y: number;
  selected: boolean;
  onClick: () => void;
}

export function ExecutionNodeComponent({ 
  label, 
  status, 
  x, 
  y, 
  selected, 
  onClick 
}: ExecutionNodeProps) {
  return (
    <div 
      onClick={onClick}
      className={cn(
        "absolute flex items-center justify-center p-2 bg-surface-elevated border rounded-[8px] shadow-panel hover:z-10 cursor-pointer transition-colors",
        status === 'RUNNING' ? 'border-accent shadow-glow' : 
        status === 'FAILED' ? 'border-danger shadow-glow-danger' : 
        status === 'COMPLETE' ? 'border-success' : 
        status === 'BLOCKED' ? 'border-warning shadow-glow-warning' : 'border-border-subtle',
        selected && 'ring-2 ring-accent/50'
      )}
      style={{ left: x, top: y }}
    >
      <div className="flex flex-col items-center gap-1.5 min-w-[80px]">
        <div className={cn("size-2 rounded-full", 
          status === 'RUNNING' ? 'bg-accent animate-pulse' : 
          status === 'FAILED' ? 'bg-danger' : 
          status === 'COMPLETE' ? 'bg-success' : 
          status === 'BLOCKED' ? 'bg-warning animate-pulse' : 'bg-muted')} 
        />
        <span className="text-2xs font-mono text-muted uppercase hover:text-foreground transition-colors">{label}</span>
      </div>
    </div>
  );
}

import type { ReactNode } from 'react';
import { Surface } from '@/design-system/primitives/Surface';
import { Stack } from '@/design-system/primitives/Stack';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { AlertCircle, WifiOff, Inbox, Activity } from 'lucide-react';
import { useExecutionStore } from '@/stores/executionStore';
import { cn } from '@/lib/utils';

export type WorkspaceState = 'loading' | 'empty' | 'disconnected' | 'error' | 'ready';

interface WorkspaceLayoutProps {
  title: string;
  description: string;
  toolbar?: ReactNode;
  state: WorkspaceState;
  children?: ReactNode;
  errorMessage?: string;
  emptyMessage?: string;
  sprintStatus?: string;
}

export function WorkspaceLayout({
  title,
  description,
  toolbar,
  state,
  children,
  errorMessage = 'An error occurred while loading this workspace.',
  emptyMessage = 'No data available in this workspace.',
  sprintStatus = 'Sprint 5.5',
}: WorkspaceLayoutProps) {
  const { connectionStatus, executionStatus } = useExecutionStore();

  const renderStateContent = () => {
    switch (state) {
      case 'loading':
        return (
          <div className="flex flex-col items-center justify-center h-full text-muted">
            <img src="/logo.png" alt="Synapse Logo" className="size-12 object-contain mix-blend-screen mb-4 animate-pulse" />
            <p className="text-sm font-medium text-foreground tracking-tight">Loading workspace...</p>
          </div>
        );
      case 'disconnected':
        return (
          <div className="flex flex-col items-center justify-center h-full text-muted">
            <WifiOff className="size-8 mb-4 opacity-50" />
            <p className="text-sm">Disconnected from orchestrator.</p>
          </div>
        );
      case 'error':
        return (
          <div className="flex flex-col items-center justify-center h-full text-destructive">
            <AlertCircle className="size-8 mb-4 opacity-50" />
            <p className="text-sm">{errorMessage}</p>
          </div>
        );
      case 'empty':
        return (
          <div className="flex flex-col items-center justify-center h-full text-muted">
            <Inbox className="size-8 mb-4 opacity-50" />
            <p className="text-sm">{emptyMessage}</p>
          </div>
        );
      case 'ready':
        return children;
    }
  };

  return (
    <Surface className="flex flex-col h-full overflow-hidden">
      <header className="flex-none px-6 py-4 border-b border-border-subtle bg-surface-elevated flex items-center justify-between">
        <Stack gap={2}>
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-medium text-foreground tracking-tight">{title}</h1>
            <span className="text-2xs font-mono px-2 py-0.5 rounded-full bg-accent/10 text-accent uppercase tracking-widest border border-accent/20">
              {sprintStatus}
            </span>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-border-subtle bg-surface text-2xs font-mono uppercase tracking-widest">
              <span className={cn(
                "relative flex size-1.5 rounded-full",
                connectionStatus === 'connected' ? 'bg-success' :
                connectionStatus === 'connecting' ? 'bg-warning animate-pulse' : 'bg-danger'
              )}>
                {connectionStatus === 'connected' && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                )}
              </span>
              <span className="text-muted">{connectionStatus}</span>
            </div>
            {connectionStatus === 'connected' && (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-border-subtle bg-surface text-2xs font-mono uppercase tracking-widest">
                <Activity className="size-3 text-muted" />
                <span className={cn(
                  "font-medium",
                  executionStatus === 'RUNNING' ? 'text-accent animate-pulse' :
                  executionStatus === 'FINISHED' ? 'text-success' :
                  executionStatus === 'FAILED' ? 'text-danger' : 'text-muted'
                )}>{executionStatus}</span>
              </div>
            )}
          </div>
          <p className="text-sm text-muted">{description}</p>
        </Stack>
        {toolbar && (
          <div className="flex items-center gap-3">
            {toolbar}
          </div>
        )}
      </header>

      <ScrollableArea className="flex-1 relative">
        <div className="absolute inset-0">
          {renderStateContent()}
        </div>
      </ScrollableArea>
    </Surface>
  );
}

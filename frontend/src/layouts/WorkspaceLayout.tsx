import type { ReactNode } from 'react';
import { Surface } from '@/design-system/primitives/Surface';
import { Stack } from '@/design-system/primitives/Stack';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { AlertCircle, Loader2, WifiOff, Inbox } from 'lucide-react';

export type WorkspaceState = 'loading' | 'empty' | 'disconnected' | 'error' | 'ready';

interface WorkspaceLayoutProps {
  title: string;
  description: string;
  toolbar?: ReactNode;
  state: WorkspaceState;
  children?: ReactNode;
  errorMessage?: string;
  emptyMessage?: string;
}

export function WorkspaceLayout({
  title,
  description,
  toolbar,
  state,
  children,
  errorMessage = 'An error occurred while loading this workspace.',
  emptyMessage = 'No data available in this workspace.',
}: WorkspaceLayoutProps) {
  
  const renderStateContent = () => {
    switch (state) {
      case 'loading':
        return (
          <div className="flex flex-col items-center justify-center h-full text-muted">
            <Loader2 className="size-8 animate-spin mb-4 text-accent" />
            <p className="text-sm">Loading workspace...</p>
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
        <Stack gap={1}>
          <h1 className="text-lg font-medium text-foreground tracking-tight">{title}</h1>
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

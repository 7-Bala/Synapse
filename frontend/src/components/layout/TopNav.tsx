import { Search, Globe, ChevronRight } from 'lucide-react';

interface WorkspaceHeaderProps {
  onOpenCommandPalette: () => void;
}

export function WorkspaceHeader({ onOpenCommandPalette }: WorkspaceHeaderProps) {
  return (
    <header className="h-12 border-b border-border bg-surface flex items-center justify-between px-4 shrink-0 z-40">
      {/* Context Area */}
      <div className="flex items-center gap-3 text-sm font-sans">
        <div className="flex items-center gap-1.5 px-2 py-1 bg-surface-elevated border border-border-subtle rounded text-foreground-muted cursor-pointer hover:text-foreground transition-colors">
          <Globe className="size-3.5" strokeWidth={1.5} />
          <span className="text-2xs font-mono uppercase tracking-wider">Production</span>
        </div>
        
        <ChevronRight className="size-3 text-border-subtle" />
        
        <div className="flex items-center gap-2">
          <span className="text-foreground font-medium">Mission Control Workspace</span>
        </div>
      </div>

      {/* Global Actions */}
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted hover:text-foreground bg-background-dark border border-border rounded transition-colors group"
        >
          <Search className="size-3.5 group-hover:text-accent transition-colors" strokeWidth={1.5} />
          <span>Quick Search...</span>
          <div className="flex items-center gap-0.5 ml-4">
            <kbd className="kbd border-transparent bg-surface">⌘</kbd>
            <kbd className="kbd border-transparent bg-surface">K</kbd>
          </div>
        </button>
      </div>
    </header>
  );
}

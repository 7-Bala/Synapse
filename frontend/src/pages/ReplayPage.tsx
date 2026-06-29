import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';

export function ReplayPage() {
  return (
    <WorkspaceLayout
      title="Replay"
      description="Time-travel debugging and execution playback."
      state="ready"
    >
      <div className="flex flex-col items-center justify-center h-full max-w-xl mx-auto p-8">
        <div className="bg-surface-elevated border border-border-subtle rounded-lg p-6 w-full shadow-sm text-left">
          <h3 className="text-sm font-semibold text-foreground mb-4 uppercase tracking-wider">Current Capability</h3>
          <ul className="list-disc pl-5 space-y-2 text-sm text-muted mb-8">
            <li>Workspace architecture complete.</li>
            <li>Navigation integrated.</li>
            <li>Waiting for Replay Archive backend.</li>
          </ul>

          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border-subtle">
            <div>
              <div className="text-2xs font-mono text-muted uppercase tracking-wider mb-1">Backend Dependency</div>
              <div className="text-xs text-foreground font-medium">Replay Archive API</div>
            </div>
            <div>
              <div className="text-2xs font-mono text-muted uppercase tracking-wider mb-1">Future Capability</div>
              <div className="text-xs text-foreground font-medium">Global timeline controlling every workspace.</div>
            </div>
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}

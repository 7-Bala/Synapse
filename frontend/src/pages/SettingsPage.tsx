import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';

export function SettingsPage() {
  return (
    <WorkspaceLayout
      title="Settings"
      description="System configuration and preferences."
      state="ready"
    >
      <div className="flex flex-col items-center justify-center h-full text-center max-w-lg mx-auto p-8">
        <h2 className="text-xl font-medium text-foreground mb-4">System Settings</h2>
        <div className="bg-surface-elevated border border-border-subtle rounded-lg p-6 w-full">
          <div className="flex justify-between items-center mb-4 pb-4 border-b border-border-subtle">
            <span className="text-sm font-medium text-muted">Current Sprint</span>
            <span className="text-sm font-mono text-accent">5 (Architecture)</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-muted">Target Sprint</span>
            <span className="text-sm font-mono text-foreground">Future Capability</span>
          </div>
          <div className="mt-6 text-sm text-muted text-left">
            <p className="mb-2">This workspace will eventually provide:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>API Key management for LLM providers.</li>
              <li>Global system defaults.</li>
              <li>UI preferences and workspace customization.</li>
            </ul>
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}

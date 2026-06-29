import { useState } from 'react';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { ExecutionGraph } from '@/components/execution/ExecutionGraph';
import { ExecutionInspector } from '@/components/execution/ExecutionInspector';
import { RuntimeEventExplorer } from '@/components/runtime-events/RuntimeEventExplorer';
import { useExecutionStore } from '@/stores/executionStore';
import { PlayCircle } from 'lucide-react';

type Tab = 'events' | 'blackboard' | 'evidence' | 'consensus' | 'logs';

function ProfessionalEmptyState({ purpose, owner, truth, sprint }: { purpose: string, owner: string, truth: string, sprint: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full max-w-xl mx-auto text-left">
      <div className="bg-surface-elevated border border-border-subtle rounded-lg p-6 w-full shadow-sm">
        <h3 className="text-sm font-semibold text-foreground mb-4 uppercase tracking-wider">{purpose}</h3>
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div>
            <div className="text-2xs font-mono text-muted uppercase tracking-wider mb-1">Owner</div>
            <div className="text-xs text-foreground font-medium">{owner}</div>
          </div>
          <div>
            <div className="text-2xs font-mono text-muted uppercase tracking-wider mb-1">Source of Truth</div>
            <div className="text-xs text-foreground font-medium">{truth}</div>
          </div>
          <div>
            <div className="text-2xs font-mono text-muted uppercase tracking-wider mb-1">Target Sprint</div>
            <div className="text-xs text-accent font-medium">{sprint}</div>
          </div>
        </div>
        <p className="text-sm text-muted">
          This UI surface is currently structurally integrated into the routing layer but awaits backend pipeline finalization.
        </p>
      </div>
    </div>
  );
}

export function ExecutionsPage() {
  const { isConnected } = useExecutionStore();
  const [activeTab, setActiveTab] = useState<Tab>('events');

  const tabs: { id: Tab; label: string }[] = [
    { id: 'events', label: 'Events' },
    { id: 'blackboard', label: 'Blackboard' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'consensus', label: 'Consensus' },
    { id: 'logs', label: 'Logs' },
  ];

  const triggerDemo = async () => {
    try {
      await fetch('http://localhost:8000/demo/start', { method: 'POST' });
    } catch (e) {
      console.error('Failed to trigger demo', e);
    }
  };

  const toolbar = (
    <button 
      onClick={triggerDemo}
      className="flex items-center gap-2 px-3 py-1.5 text-xs text-foreground bg-accent/10 border border-accent/50 hover:bg-accent/20 rounded transition-colors font-medium"
    >
      <PlayCircle className="size-3.5 text-accent" />
      Start Execution
    </button>
  );

  return (
    <WorkspaceLayout
      title="Executions"
      description="Inspect and control active orchestrations."
      toolbar={toolbar}
      state={isConnected ? 'ready' : 'disconnected'}
    >
      <div className="flex flex-col w-full h-full">
        {/* TOP: Execution Graph & Inspector */}
        <div className="flex-1 flex min-h-0 border-b border-border-subtle">
          <ExecutionGraph />
          <ExecutionInspector />
        </div>

        {/* BOTTOM: Workspace Tabs */}
        <div className="h-[300px] flex flex-col bg-surface-elevated shrink-0">
          {/* Tab Header */}
          <div className="flex border-b border-border-subtle bg-surface px-4">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === tab.id 
                    ? 'border-accent text-foreground' 
                    : 'border-transparent text-muted hover:text-foreground'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden p-4">
            {activeTab === 'events' && (
              <div className="h-full w-full">
                <RuntimeEventExplorer />
              </div>
            )}
            
            {activeTab === 'blackboard' && (
              <ProfessionalEmptyState 
                purpose="Global memory and shared state visualization"
                owner="Orchestrator Memory Manager"
                truth="ExecutionStore (Zustand) -> Redis Backend"
                sprint="Future Sprint"
              />
            )}

            {activeTab === 'evidence' && (
              <ProfessionalEmptyState 
                purpose="Artifact inspection and generated outputs"
                owner="Evidence Pipeline"
                truth="Artifact Storage / S3"
                sprint="Future Sprint"
              />
            )}

            {activeTab === 'consensus' && (
              <ProfessionalEmptyState 
                purpose="Agent voting and conflict resolution traces"
                owner="Consensus Engine"
                truth="Voting Telemetry Stream"
                sprint="Future Sprint"
              />
            )}

            {activeTab === 'logs' && (
              <ProfessionalEmptyState 
                purpose="Raw stdout/stderr and diagnostics"
                owner="Instrumentation Layer"
                truth="Elasticsearch / Loki"
                sprint="Future Sprint"
              />
            )}
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}

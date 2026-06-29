import { useState } from 'react';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { ExecutionGraph } from '@/components/execution/ExecutionGraph';
import { ExecutionInspector } from '@/components/execution/ExecutionInspector';
import { LiveEventStream } from '@/components/mission-control/LiveEventStream';
import { useExecutionStore } from '@/stores/executionStore';
import { PlayCircle } from 'lucide-react';

type Tab = 'events' | 'blackboard' | 'evidence' | 'consensus' | 'logs';

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
        <div className="h-[300px] flex flex-col bg-surface-elevated">
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
                <LiveEventStream />
              </div>
            )}
            
            {activeTab === 'blackboard' && (
              <div className="flex flex-col items-center justify-center h-full text-muted">
                <h3 className="text-sm font-medium text-foreground mb-1">Blackboard State</h3>
                <p className="text-xs max-w-sm text-center">Will display the global, shared memory state of the execution in future sprints.</p>
              </div>
            )}

            {activeTab === 'evidence' && (
              <div className="flex flex-col items-center justify-center h-full text-muted">
                <h3 className="text-sm font-medium text-foreground mb-1">Execution Evidence</h3>
                <p className="text-xs max-w-sm text-center">Will display files, tool call outputs, and generated artifacts in future sprints.</p>
              </div>
            )}

            {activeTab === 'consensus' && (
              <div className="flex flex-col items-center justify-center h-full text-muted">
                <h3 className="text-sm font-medium text-foreground mb-1">Agent Consensus</h3>
                <p className="text-xs max-w-sm text-center">Will display committee voting, conflict resolution, and decision traces in future sprints.</p>
              </div>
            )}

            {activeTab === 'logs' && (
              <div className="flex flex-col items-center justify-center h-full text-muted">
                <h3 className="text-sm font-medium text-foreground mb-1">System Logs</h3>
                <p className="text-xs max-w-sm text-center">Will display raw stdout/stderr and system-level diagnostics in future sprints.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}

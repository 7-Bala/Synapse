import { useState, useEffect } from 'react';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { ExecutionGraph } from '@/components/execution/ExecutionGraph';
import { ExecutionInspector } from '@/components/execution/ExecutionInspector';
import { RuntimeEventExplorer } from '@/components/runtime-events/RuntimeEventExplorer';
import { useExecutionStore } from '@/stores/executionStore';
import {
  PlayCircle, StopCircle, RefreshCw, Cpu, Activity, Coins, Sparkles,
  Terminal, CheckCircle2, XCircle, Loader2, Clock
} from 'lucide-react';
import type { ExecutionState, TimelineEntry } from '@/types/execution';

type Tab = 'events' | 'timeline' | 'blackboard' | 'evidence' | 'consensus' | 'logs';

function ProfessionalEmptyState({ purpose, owner, truth, sprint }: { purpose: string, owner: string, truth: string, sprint: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full max-w-xl mx-auto text-left py-8">
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

function getStatusColor(status: ExecutionState): string {
  switch (status) {
    case 'QUEUED': return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    case 'INITIALIZING': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20 animate-pulse';
    case 'PLANNING': return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    case 'RUNNING': return 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse';
    case 'VALIDATING': return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    case 'COMPLETED': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'FAILED': return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'CANCELLED': return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
    default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
  }
}

function getTimelineIcon(event: string) {
  if (event.includes('failed') || event === 'FAILED') return <XCircle className="size-3 text-red-400 shrink-0 mt-0.5" />;
  if (event.includes('completed') || event === 'COMPLETED') return <CheckCircle2 className="size-3 text-emerald-400 shrink-0 mt-0.5" />;
  if (event.includes('started') || event === 'RUNNING') return <Loader2 className="size-3 text-blue-400 shrink-0 mt-0.5 animate-spin" />;
  if (event === 'VALIDATING') return <CheckCircle2 className="size-3 text-cyan-400 shrink-0 mt-0.5" />;
  if (event === 'PLANNING') return <Sparkles className="size-3 text-purple-400 shrink-0 mt-0.5" />;
  return <Clock className="size-3 text-muted shrink-0 mt-0.5" />;
}

function TimelinePanel({ timeline }: { timeline: TimelineEntry[] }) {
  if (timeline.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-xs text-muted font-mono italic">
        Waiting for execution to begin...
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto px-2 py-1 space-y-0.5 font-mono">
      {timeline.map((entry, idx) => (
        <div key={idx} className="flex items-start gap-2.5 py-1 px-2 rounded hover:bg-surface-elevated transition-colors group">
          {getTimelineIcon(entry.event)}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-2xs font-semibold text-foreground">{entry.event}</span>
              {entry.agent && (
                <span className="text-3xs px-1.5 py-0.5 rounded bg-accent/10 text-accent border border-accent/20">
                  {entry.agent}
                </span>
              )}
            </div>
            {entry.detail && (
              <p className="text-3xs text-muted mt-0.5 truncate">{entry.detail}</p>
            )}
          </div>
          <span className="text-3xs text-muted/60 shrink-0 group-hover:text-muted transition-colors">
            {new Date(entry.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>
      ))}
    </div>
  );
}

const TERMINAL_STATES: ExecutionState[] = ['COMPLETED', 'FAILED', 'CANCELLED'];

export function ExecutionsPage() {
  const {
    isConnected,
    executions,
    activeExecution,
    activeEvents,
    activeTimeline,
    loadExecutions,
    selectExecution,
    triggerExecution,
    cancelExecution,
    isLoading
  } = useExecutionStore();

  const [activeTab, setActiveTab] = useState<Tab>('timeline');
  const [promptText, setPromptText] = useState('');
  const [execMode, setExecMode] = useState<'LIVE' | 'SIMULATION'>('LIVE');

  useEffect(() => {
    loadExecutions();
    useExecutionStore.getState().connect();
    return () => {
      useExecutionStore.getState().disconnect();
    };
  }, [loadExecutions]);

  // Auto-switch to timeline tab when a new active execution is selected
  useEffect(() => {
    if (activeExecution && !TERMINAL_STATES.includes(activeExecution.status)) {
      setActiveTab('timeline');
    }
  }, [activeExecution?.id]);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptText.trim()) return;
    await triggerExecution(promptText, execMode);
    setPromptText('');
  };

  const tabs: { id: Tab; label: string }[] = [
    { id: 'timeline', label: 'Timeline' },
    { id: 'events', label: 'Events' },
    { id: 'blackboard', label: 'Blackboard' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'consensus', label: 'Consensus' },
    { id: 'logs', label: 'Terminal Logs' },
  ];

  const isActiveRunning = activeExecution && !TERMINAL_STATES.includes(activeExecution.status);
  const progress = activeExecution?.progress ?? 0;

  return (
    <WorkspaceLayout
      title="Execution Center"
      description="Inspect, replay, and manage multi-agent execution lifecycles."
      state={isConnected ? 'ready' : 'idle'}
      sprintStatus="Sprint 6.0"
    >
      <div className="flex h-full w-full min-h-0 bg-background text-foreground overflow-hidden">
        {/* Left Panel: Run History Sidebar */}
        <div className="w-80 border-r border-border-subtle flex flex-col min-h-0 bg-surface">
          {/* Trigger Prompt */}
          <div className="p-4 border-b border-border-subtle bg-surface-elevated">
            <form onSubmit={handleStart} className="space-y-3">
              <div className="flex flex-col gap-1.5">
                <label className="text-2xs font-mono text-muted uppercase tracking-wider">New Agent Prompt</label>
                <textarea
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  placeholder="e.g. Investigate scheduler latency spikes..."
                  className="w-full h-20 text-xs p-2 rounded bg-surface border border-border-subtle focus:border-accent outline-none resize-none placeholder-muted/60"
                />
              </div>

              <div className="flex items-center justify-between gap-2">
                <select
                  value={execMode}
                  onChange={(e) => setExecMode(e.target.value as any)}
                  className="bg-surface text-2xs p-1.5 rounded border border-border-subtle text-foreground font-mono outline-none"
                >
                  <option value="LIVE">LIVE RUN</option>
                  <option value="SIMULATION">SIMULATION</option>
                </select>

                <button
                  type="submit"
                  disabled={!promptText.trim() || isLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-2xs text-white bg-accent hover:bg-accent-hover disabled:bg-accent/30 rounded transition-colors font-medium cursor-pointer"
                >
                  <PlayCircle className="size-3.5" />
                  Run OS
                </button>
              </div>
            </form>
          </div>

          {/* Execution List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            <div className="flex items-center justify-between px-2 py-1">
              <span className="text-2xs font-mono text-muted uppercase tracking-wider">Executions ({executions.length})</span>
              <button
                onClick={() => loadExecutions()}
                disabled={isLoading}
                className="text-muted hover:text-foreground transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`size-3 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {executions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center px-4 gap-2">
                <p className="text-xs font-semibold font-mono text-muted">Execution history is empty.</p>
                <p className="text-3xs text-muted/60 font-mono leading-relaxed">
                  Run your first execution to begin<br />capturing runtime telemetry.
                </p>
              </div>
            ) : (
              executions.map((exec) => {
                const isActive = activeExecution?.id === exec.id;
                const isRunning = !TERMINAL_STATES.includes(exec.status) && exec.status !== 'QUEUED';
                return (
                  <button
                    key={exec.id}
                    onClick={() => selectExecution(exec.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-all flex flex-col gap-2 ${
                      isActive
                        ? 'bg-accent/5 border-accent shadow-sm'
                        : 'bg-surface-elevated/40 border-border-subtle hover:bg-surface-elevated/80'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 w-full">
                      <span className="text-xs font-mono font-semibold text-foreground truncate max-w-[140px]">
                        {exec.id.substring(0, 12)}
                      </span>
                      <span className={`text-3xs font-mono px-2 py-0.5 rounded-full border ${getStatusColor(exec.status)}`}>
                        {exec.status}
                      </span>
                    </div>

                    <p className="text-xs text-muted truncate line-clamp-1 w-full text-left">
                      {exec.userPrompt}
                    </p>

                    {/* Mini progress bar for running executions */}
                    {isRunning && (
                      <div className="w-full h-0.5 bg-border-subtle rounded-full overflow-hidden">
                        <div
                          className="h-full bg-accent transition-all duration-500 ease-out"
                          style={{ width: `${(exec.progress ?? 0) * 100}%` }}
                        />
                      </div>
                    )}

                    <div className="flex items-center justify-between text-3xs font-mono text-muted/80">
                      <span>{exec.executionMode}</span>
                      <span>{new Date(exec.createdAt * 1000).toLocaleTimeString()}</span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right Panel: Detail View */}
        <div className="flex-1 flex flex-col min-w-0 bg-background overflow-hidden">
          {activeExecution ? (
            <div className="flex-1 flex flex-col min-h-0">
              {/* Header */}
              <div className="p-4 border-b border-border-subtle bg-surface-elevated flex items-center justify-between shrink-0">
                <div className="space-y-1 flex-1 min-w-0 mr-4">
                  <div className="flex items-center gap-3">
                    <h2 className="text-sm font-semibold font-mono text-foreground">{activeExecution.id}</h2>
                    <span className={`text-2xs font-mono px-2 py-0.5 rounded-full border ${getStatusColor(activeExecution.status)}`}>
                      {activeExecution.status}
                    </span>
                    <span className="text-2xs font-mono text-muted bg-surface/50 border border-border-subtle px-1.5 py-0.5 rounded">
                      {activeExecution.executionMode}
                    </span>
                  </div>
                  <p className="text-xs text-muted truncate">{activeExecution.userPrompt}</p>

                  {/* Progress bar */}
                  {isActiveRunning && (
                    <div className="flex items-center gap-2 pt-1">
                      <div className="flex-1 h-1 bg-border-subtle rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-accent to-accent/70 rounded-full transition-all duration-700 ease-out"
                          style={{ width: `${progress * 100}%` }}
                        />
                      </div>
                      <span className="text-3xs font-mono text-muted shrink-0">{Math.round(progress * 100)}%</span>
                    </div>
                  )}
                </div>

                {(activeExecution.status === 'QUEUED' ||
                  activeExecution.status === 'INITIALIZING' ||
                  activeExecution.status === 'PLANNING' ||
                  activeExecution.status === 'RUNNING') && (
                  <button
                    onClick={() => cancelExecution(activeExecution.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-2xs text-red-400 hover:text-red-300 border border-red-500/20 hover:border-red-500/40 bg-red-500/5 hover:bg-red-500/10 rounded transition-colors font-medium cursor-pointer shrink-0"
                  >
                    <StopCircle className="size-3.5" />
                    Cancel
                  </button>
                )}
              </div>

              {/* Metrics cards */}
              <div className="grid grid-cols-5 gap-3 p-4 border-b border-border-subtle bg-surface/30 shrink-0">
                <div className={`bg-surface-elevated border border-border-subtle p-3 rounded-lg flex items-center gap-3 ${isActiveRunning ? 'border-blue-500/20' : ''}`}>
                  <div className="p-2 rounded bg-blue-500/10 text-blue-400">
                    <Activity className="size-4" />
                  </div>
                  <div>
                    <div className="text-3xs font-mono text-muted uppercase">Latency</div>
                    <div className="text-sm font-semibold font-mono">{(activeExecution.totalLatency / 1000).toFixed(2)}s</div>
                  </div>
                </div>

                <div className="bg-surface-elevated border border-border-subtle p-3 rounded-lg flex items-center gap-3">
                  <div className="p-2 rounded bg-purple-500/10 text-purple-400">
                    <Cpu className="size-4" />
                  </div>
                  <div>
                    <div className="text-3xs font-mono text-muted uppercase">Tokens</div>
                    <div className="text-sm font-semibold font-mono">{activeExecution.totalTokens.toLocaleString()}</div>
                  </div>
                </div>

                <div className="bg-surface-elevated border border-border-subtle p-3 rounded-lg flex items-center gap-3">
                  <div className="p-2 rounded bg-emerald-500/10 text-emerald-400">
                    <Coins className="size-4" />
                  </div>
                  <div>
                    <div className="text-3xs font-mono text-muted uppercase">Est. Cost</div>
                    <div className="text-sm font-semibold font-mono">${activeExecution.estimatedCost.toFixed(5)}</div>
                  </div>
                </div>

                <div className="bg-surface-elevated border border-border-subtle p-3 rounded-lg flex items-center gap-3">
                  <div className="p-2 rounded bg-emerald-500/10 text-emerald-400">
                    <CheckCircle2 className="size-4" />
                  </div>
                  <div>
                    <div className="text-3xs font-mono text-muted uppercase">Agents Done</div>
                    <div className="text-sm font-semibold font-mono">
                      <span className="text-emerald-400">{activeExecution.completedAgentCount}</span>
                      {activeExecution.failedAgentCount > 0 && (
                        <span className="text-red-400 ml-1">/ {activeExecution.failedAgentCount}✗</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className={`bg-surface-elevated border border-border-subtle p-3 rounded-lg flex items-center gap-3 ${isActiveRunning ? 'border-accent/30' : ''}`}>
                  <div className={`p-2 rounded bg-purple-500/10 text-purple-400 ${isActiveRunning ? 'animate-pulse' : ''}`}>
                    <Sparkles className="size-4" />
                  </div>
                  <div>
                    <div className="text-3xs font-mono text-muted uppercase">Active Agent</div>
                    <div className="text-sm font-semibold font-mono truncate max-w-[100px]">
                      {activeExecution.currentAgent || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Main graph panel */}
              <div className="flex-1 flex min-h-0 border-b border-border-subtle">
                <ExecutionGraph />
                <ExecutionInspector />
              </div>

              {/* Bottom panel: Timeline, Events, Logs */}
              <div className="h-[280px] flex flex-col bg-surface-elevated shrink-0">
                <div className="flex border-b border-border-subtle bg-surface px-4">
                  {tabs.map((tab) => (
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
                      {tab.id === 'timeline' && activeTimeline.length > 0 && (
                        <span className="ml-1.5 text-3xs bg-accent/15 text-accent px-1.5 py-0.5 rounded-full font-mono">
                          {activeTimeline.length}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                <div className="flex-1 overflow-hidden p-4">
                  {activeTab === 'timeline' && (
                    <TimelinePanel timeline={activeTimeline} />
                  )}

                  {activeTab === 'events' && (
                    <div className="h-full w-full">
                      <RuntimeEventExplorer />
                    </div>
                  )}

                  {activeTab === 'blackboard' && (
                    <ProfessionalEmptyState
                      purpose="Global memory and shared state visualization"
                      owner="Orchestrator Memory Manager"
                      truth="ExecutionStore (Zustand) → Redis Backend"
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
                    <div className="h-full w-full bg-surface border border-border-subtle rounded-lg flex flex-col overflow-hidden">
                      <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-elevated border-b border-border-subtle text-3xs font-mono text-muted uppercase">
                        <Terminal className="size-3 text-accent" />
                        OS Execution Logger
                      </div>
                      <div className="flex-1 overflow-y-auto p-3 font-mono text-2xs space-y-1.5 bg-surface-elevated/40">
                        {activeEvents && activeEvents.length > 0 ? (
                          activeEvents.map((evt, idx) => (
                            <div key={idx} className="flex gap-4 hover:bg-surface-elevated p-1 rounded transition-colors">
                              <span className="text-muted/60 select-none">
                                {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                              </span>
                              <span className="text-accent font-semibold">{evt.type || evt.event_type || 'Event'}</span>
                              <span className="text-foreground truncate">{JSON.stringify(evt.payload || evt.data || evt)}</span>
                            </div>
                          ))
                        ) : (
                          <div className="text-muted italic py-4 text-center">No terminal logs captured yet.</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 space-y-4">
              <div className="w-12 h-12 rounded-full bg-accent/5 border border-accent/20 flex items-center justify-center text-accent">
                <Sparkles className="size-6" />
              </div>
              <div className="space-y-1 max-w-sm">
                <h3 className="text-sm font-semibold text-foreground">Select an Execution</h3>
                <p className="text-xs text-muted">
                  Choose a run from the history sidebar or prompt the Synapse OS to start a new multi-agent orchestrator.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </WorkspaceLayout>
  );
}

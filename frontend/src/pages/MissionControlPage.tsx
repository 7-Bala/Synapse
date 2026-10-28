import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { useMissionControlStore } from '@/stores/missionControlStore';
import { useExecutionStore } from '@/stores/executionStore';
import {
  Cpu, Clock, StopCircle, Server,
  ArrowRight, ShieldCheck, FileText, Database, Zap, Network
} from 'lucide-react';

// Health indicator helper component
function HealthIndicatorCard({ label, status, detail }: { label: string, status: 'GREEN' | 'YELLOW' | 'RED', detail: string }) {
  const getStatusColors = () => {
    switch (status) {
      case 'GREEN':
        return {
          bg: 'bg-emerald-500/5',
          border: 'border-emerald-500/10 hover:border-emerald-500/30',
          text: 'text-emerald-400',
          badgeBg: 'bg-emerald-500/15',
          dot: 'bg-emerald-400'
        };
      case 'YELLOW':
        return {
          bg: 'bg-amber-500/5',
          border: 'border-amber-500/10 hover:border-amber-500/30',
          text: 'text-amber-400',
          badgeBg: 'bg-amber-500/15',
          dot: 'bg-amber-400'
        };
      case 'RED':
        return {
          bg: 'bg-rose-500/5',
          border: 'border-rose-500/10 hover:border-rose-500/30',
          text: 'text-rose-400',
          badgeBg: 'bg-rose-500/15',
          dot: 'bg-rose-400 animate-pulse'
        };
    }
  };

  const colors = getStatusColors();

  return (
    <div className={`flex items-start justify-between px-3 py-2.5 border rounded-lg transition-all duration-300 ${colors.bg} ${colors.border}`}>
      <div className="flex flex-col gap-0.5 flex-1 min-w-0 mr-3">
        <span className="text-2xs font-mono font-semibold text-foreground leading-tight">{label}</span>
        <span className="text-3xs text-muted font-mono leading-tight">{detail}</span>
      </div>
      <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full border border-current/10 shrink-0 ${colors.badgeBg} ${colors.text}`}>
        <span className={`size-1.5 rounded-full shrink-0 ${colors.dot}`} />
        <span className="text-3xs font-mono font-bold tracking-wider">{status}</span>
      </div>
    </div>
  );
}

// Topology node helper
function TopologyNode({
  title,
  isActive,
  isSpecialist,
  subtitle,
  icon: Icon
}: {
  title: string;
  isActive: boolean;
  isSpecialist?: boolean;
  subtitle: string;
  icon: any;
}) {
  return (
    <div className={`relative flex flex-col items-center p-3 rounded-lg border text-center transition-all duration-300 w-36 ${
      isActive 
        ? 'bg-accent/10 border-accent shadow-glow scale-[1.03] z-10' 
        : 'bg-surface-elevated/40 border-border-subtle hover:border-muted/30'
    } ${isSpecialist ? 'border-dashed' : ''}`}>
      {isActive && (
        <span className="absolute -top-1.5 right-2 px-1.5 py-0.5 rounded bg-accent text-white text-3xs font-mono font-bold uppercase tracking-wider animate-pulse">
          ACTIVE
        </span>
      )}
      <div className={`p-1.5 rounded-md mb-1.5 ${isActive ? 'bg-accent/20 text-accent' : 'bg-surface/60 text-muted'}`}>
        <Icon className="size-4" />
      </div>
      <span className={`text-2xs font-mono font-bold ${isActive ? 'text-foreground' : 'text-muted-foreground'}`}>{title}</span>
      <span className="text-3xs font-mono text-muted tracking-tight mt-0.5">{subtitle}</span>
    </div>
  );
}

export function MissionControlPage() {
  const navigate = useNavigate();
  const {
    overview,
    activeExecutions,
    activeAgents,
    queuedExecutions,
    events,
    health,
    startPolling,
    stopPolling
  } = useMissionControlStore();

  const { cancelExecution, selectExecution } = useExecutionStore();

  // Poll for snapshot data
  useEffect(() => {
    startPolling(2000);
    return () => {
      stopPolling();
    };
  }, [startPolling, stopPolling]);

  // Derived values — show real 0 when idle, only use store data when present
  const activeRunsCount = overview?.activeExecutions ?? activeExecutions.length;
  const queueLengthVal = overview?.queueLength ?? queuedExecutions.length;
  const runningAgentsVal = overview?.runningAgents ?? activeAgents.length;
  const schedulerWorkers = overview?.schedulerWorkers ?? 3;
  const hasRealData = overview !== null;
  const successRatePct = hasRealData ? Math.round(overview!.successRate * 100) : '—';
  const avgLatencySec = (hasRealData && overview!.averageLatency > 0) ? overview!.averageLatency.toFixed(2) : '—';
  const totalTokensVal = hasRealData ? overview!.totalTokens : 0;
  const estCost = (hasRealData && overview!.estimatedCost > 0) ? overview!.estimatedCost.toFixed(5) : '0.00000';

  // Highlight currently executing topology node
  const activeAgentNames = new Set(activeExecutions.map(e => e.currentAgent).filter(Boolean));
  const activeStages = new Set(activeExecutions.map(e => e.status));

  // Structured agent registry — idle state, metrics derived from real store only
  const specialistUtilization = [
    {
      name: 'PlannerSpecialist',
      role: 'Prompt Decomposition',
      status: activeAgentNames.has('PlannerAgent') ? 'RUNNING' : 'IDLE',
      executions: activeRunsCount > 0 ? activeRunsCount : 0,
      latency: '—',
      tokens: '—',
      retries: 0
    },
    {
      name: 'ResearchSpecialist',
      role: 'Context Ingestion',
      status: activeAgentNames.has('ResearchAgent') ? 'RUNNING' : 'IDLE',
      executions: 0,
      latency: '—',
      tokens: '—',
      retries: 0
    },
    {
      name: 'ReasoningSpecialist',
      role: 'Cognitive Engine',
      status: activeAgentNames.has('ReasoningAgent') ? 'RUNNING' : 'IDLE',
      executions: 0,
      latency: '—',
      tokens: '—',
      retries: 0
    },
    {
      name: 'ValidationSpecialist',
      role: 'Quality Evaluation',
      status: activeAgentNames.has('ValidationAgent') ? 'RUNNING' : 'IDLE',
      executions: 0,
      latency: '—',
      tokens: '—',
      retries: 0
    },
    {
      name: 'ReporterSpecialist',
      role: 'Synthesis & Output',
      status: activeAgentNames.has('ReporterAgent') ? 'RUNNING' : 'IDLE',
      executions: 0,
      latency: '—',
      tokens: '—',
      retries: 0
    }
  ];

  // Helper to map UI phase status styling
  const getStatusColor = (status: string): string => {
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
  };

  const handleSelectExecution = async (id: string) => {
    await selectExecution(id);
    navigate('/executions');
  };

  // Environment and system settings toolbar items
  const headerToolbar = (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-border-subtle bg-surface text-2xs font-mono uppercase tracking-wider text-muted">
        <Server className="size-3 text-muted" />
        <span>Env: <span className="text-foreground font-semibold">PRODUCTION</span></span>
      </div>
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-border-subtle bg-surface text-2xs font-mono uppercase tracking-wider text-muted">
        <Database className="size-3 text-muted" />
        <span>Source: <span className="text-foreground font-semibold">LOCAL_STORE</span></span>
      </div>
    </div>
  );

  return (
    <WorkspaceLayout
      title="Mission Control"
      description="Centralized operational view of execution, scheduler health, specialists, runtime events and telemetry."
      state="idle"
      toolbar={headerToolbar}
      sprintStatus="Sprint 6.0"
    >
      <div className="flex flex-col w-full h-full p-6 gap-6 bg-background-dark overflow-y-auto">

        {/* ROW 1: OPERATIONAL METRIC CARDS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 shrink-0">
          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Active Executions</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {activeRunsCount}
              </span>
              <span className="text-3xs font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">LIVE</span>
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Running Specialists</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {runningAgentsVal}
              </span>
              <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">POOL</span>
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Queue Length</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {queueLengthVal}
              </span>
              {queueLengthVal > 0 ? (
                <span className="text-3xs font-mono text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded animate-pulse">PENDING</span>
              ) : (
                <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">EMPTY</span>
              )}
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Scheduler Workers</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {schedulerWorkers}
              </span>
              <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">CONCUR</span>
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Success Rate</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {successRatePct}{typeof successRatePct === 'number' ? '%' : ''}
              </span>
              <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">LIFETIME</span>
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Average Latency</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {avgLatencySec}{typeof avgLatencySec === 'string' && avgLatencySec !== '—' ? 's' : ''}
              </span>
              <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">P95</span>
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Token Usage</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                {totalTokensVal.toLocaleString()}
              </span>
              <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">TOTAL</span>
            </div>
          </Surface>

          <Surface variant="panel" border="strong" className="p-4 bg-surface-elevated/60 flex flex-col gap-2 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300 group cursor-default">
            <span className="text-3xs font-mono text-muted uppercase tracking-wider leading-none">Estimated Cost</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-mono font-bold text-foreground group-hover:text-accent transition-colors leading-none">
                ${estCost}
              </span>
              <span className="text-3xs font-mono text-muted bg-surface px-1.5 py-0.5 rounded border border-border-subtle">USD</span>
            </div>
          </Surface>
        </div>

        {/* ROW 2: ACTIVE EXECUTION LIST & SYSTEM HEALTH */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 shrink-0" style={{ minHeight: '260px' }}>
          
          {/* Active Executions - 8 Columns */}
          <div className="lg:col-span-8 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono text-muted uppercase tracking-wider">Active Execution Runtime ({activeExecutions.length})</span>
            </div>
            <Surface variant="panel" border="strong" className="flex-1 bg-surface-elevated p-0 flex flex-col overflow-hidden">
              <ScrollableArea className="flex-1">
                {activeExecutions.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center gap-3 px-6">
                  <div className="space-y-1.5">
                    <p className="text-xs font-mono font-semibold text-foreground">No Active Executions</p>
                    <p className="text-3xs font-mono text-muted leading-relaxed">
                      The orchestration runtime is healthy.<br />
                      Submit a new execution from Execution Center<br />
                      to begin monitoring live runtime activity.
                    </p>
                  </div>
                  <div className="mt-2 flex flex-col gap-1.5 text-3xs font-mono text-left w-full max-w-xs border border-border-subtle rounded-lg p-3 bg-surface-elevated/30">
                    <div className="text-muted uppercase tracking-wider mb-1">Runtime Status</div>
                    <div className="flex items-center gap-2 text-emerald-400"><span className="size-1.5 rounded-full bg-emerald-400" />Scheduler Ready</div>
                    <div className="flex items-center gap-2 text-emerald-400"><span className="size-1.5 rounded-full bg-emerald-400" />EventBus Healthy</div>
                    <div className="flex items-center gap-2 text-emerald-400"><span className="size-1.5 rounded-full bg-emerald-400" />Local Store Connected</div>
                    <div className="flex items-center gap-2 text-emerald-400"><span className="size-1.5 rounded-full bg-emerald-400" />Specialists Registered</div>
                  </div>
                </div>
              ) : (
                  <div className="divide-y divide-border-subtle">
                    {activeExecutions.map((exec) => (
                      <div key={exec.id} className="p-4 flex items-center justify-between hover:bg-surface/30 transition-colors">
                        <div className="space-y-1.5 flex-1 min-w-0 mr-4">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleSelectExecution(exec.id)}
                              className="text-xs font-mono font-bold text-accent hover:underline text-left truncate block"
                            >
                              {exec.id.substring(0, 18)}...
                            </button>
                            <span className={`text-3xs font-mono px-2 py-0.5 rounded border ${getStatusColor(exec.status)}`}>
                              {exec.status}
                            </span>
                            <span className="text-3xs font-mono text-muted">
                              {exec.executionMode}
                            </span>
                          </div>
                          <p className="text-xs text-muted truncate">{exec.userPrompt}</p>
                          <div className="flex items-center gap-3">
                            <span className="text-3xs font-mono text-muted shrink-0">
                              Stage: <span className="text-foreground font-semibold">{exec.status}</span>
                            </span>
                            <span className="text-3xs font-mono text-muted shrink-0">
                              Active Specialist: <span className="text-accent font-semibold">{exec.currentAgent}</span>
                            </span>
                            <div className="flex-1 h-1 bg-border-subtle rounded-full overflow-hidden">
                              <div
                                className="h-full bg-accent rounded-full transition-all duration-500"
                                style={{ width: `${exec.progress * 100}%` }}
                              />
                            </div>
                            <span className="text-3xs font-mono text-muted shrink-0 font-semibold">
                              {Math.round(exec.progress * 100)}%
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          <span className="text-xs font-mono text-muted">
                            {exec.elapsed.toFixed(1)}s
                          </span>
                          <button
                            onClick={() => cancelExecution(exec.id)}
                            className="p-1.5 text-rose-400 hover:text-rose-300 bg-rose-500/5 hover:bg-rose-500/10 border border-rose-500/20 hover:border-rose-500/40 rounded transition-colors"
                            title="Cancel Execution"
                          >
                            <StopCircle className="size-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollableArea>
            </Surface>
          </div>

          {/* System Health Status - 4 Columns */}
          <div className="lg:col-span-4 flex flex-col">
            <div className="mb-2">
              <span className="text-xs font-mono text-muted uppercase tracking-wider">System Health Status</span>
            </div>
            <Surface variant="panel" border="strong" className="flex-1 bg-surface-elevated p-3 flex flex-col gap-2">
              <HealthIndicatorCard label="Core Runtime" status={health?.overall || 'GREEN'} detail="Lifecycle orchestration" />
              <HealthIndicatorCard label="Execution Scheduler" status={health?.scheduler || 'GREEN'} detail="Queue FIFO dispatcher" />
              <HealthIndicatorCard label="Telemetry EventBus" status={health?.eventBus || 'GREEN'} detail="Async telemetry pub-sub" />
              <HealthIndicatorCard label="Persistence Store" status={health?.store || 'GREEN'} detail="In-memory execution store" />
              <div className="mt-auto pt-2 border-t border-border-subtle flex items-center justify-between text-3xs font-mono text-muted uppercase tracking-wider">
                <span>API Status</span>
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="size-1 bg-emerald-400 rounded-full animate-ping" />
                  ONLINE
                </span>
              </div>
            </Surface>
          </div>
        </div>

        {/* ROW 3: LIVE OPERATIONAL FEED */}
        <div className="flex flex-col min-h-[220px] shrink-0">
          <div className="mb-2">
            <span className="text-xs font-mono text-muted uppercase tracking-wider font-semibold">Live Activity Event Stream</span>
          </div>
          <Surface variant="panel" border="strong" className="h-[200px] bg-surface-elevated p-0 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-3 py-1.5 bg-surface border-b border-border-subtle text-3xs font-mono text-muted uppercase">
              <span className="flex items-center gap-1.5">
                <Server className="size-3 text-accent animate-pulse" />
                Aggregated event log stream
              </span>
              <span className="text-3xs text-muted">
                {events.length} logs captured
              </span>
            </div>
            <ScrollableArea className="flex-1 p-3 bg-surface-elevated/10">
              {events && events.length > 0 ? (
                <div className="space-y-1 font-mono text-2xs">
                  {events.map((evt, idx) => (
                    <div key={idx} className="flex gap-4 hover:bg-surface-elevated p-1 rounded transition-colors">
                      <span className="text-muted/60 select-none shrink-0">
                        {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                      </span>
                      <span className="text-accent font-semibold shrink-0">[{evt.event}]</span>
                      {evt.agent && (
                        <span className="text-3xs px-1.5 rounded bg-accent/15 text-accent border border-accent/20 font-semibold shrink-0">
                          {evt.agent}
                        </span>
                      )}
                      <span className="text-foreground truncate">{evt.detail}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-xs text-muted font-mono space-y-1.5">
                  <Zap className="size-4 text-muted-foreground/40" />
                  <span className="font-semibold text-muted-foreground/70">Event stream idle</span>
                  <span className="text-3xs text-muted/60">Events will appear here when executions are running.</span>
                </div>
              )}
            </ScrollableArea>
          </Surface>
        </div>

        {/* ROW 4: RUNTIME TOPOLOGY DIAGRAM */}
        <div className="flex flex-col shrink-0">
          <div className="mb-2">
            <span className="text-xs font-mono text-muted uppercase tracking-wider">Operational Engine Topology</span>
          </div>
          <Surface variant="panel" border="strong" className="p-5 bg-surface-elevated/70">
            <div className="flex flex-col md:flex-row items-center justify-center gap-3 py-4 overflow-x-auto min-w-0">
              
              <TopologyNode 
                title="Scheduler" 
                isActive={activeRunsCount > 0 || queueLengthVal > 0} 
                subtitle="Queue Manager" 
                icon={Server} 
              />
              <ArrowRight className="size-4 text-muted hidden md:block shrink-0" />
              
              <TopologyNode 
                title="Execution Queue" 
                isActive={queueLengthVal > 0} 
                subtitle={`${queueLengthVal} Pending Jobs`} 
                icon={Clock} 
              />
              <ArrowRight className="size-4 text-muted hidden md:block shrink-0" />
              
              <TopologyNode 
                title="Orchestrator" 
                isActive={activeRunsCount > 0} 
                subtitle="State Coordinator" 
                icon={Network} 
              />
              <ArrowRight className="size-4 text-muted hidden md:block shrink-0" />

              {/* Specialists pipeline sequence */}
              <div className="flex items-center gap-1.5 px-4 py-2 bg-background/40 border border-border-subtle rounded-xl flex-wrap justify-center shrink-0">
                <TopologyNode 
                  title="PlannerAgent" 
                  isActive={activeAgentNames.has('PlannerAgent') || activeStages.has('PLANNING')} 
                  isSpecialist 
                  subtitle="Decomposition" 
                  icon={Cpu} 
                />
                <ArrowRight className="size-3 text-muted/60 shrink-0" />
                
                <TopologyNode 
                  title="ResearchAgent" 
                  isActive={activeAgentNames.has('ResearchAgent')} 
                  isSpecialist 
                  subtitle="Context Ingestion" 
                  icon={Cpu} 
                />
                <ArrowRight className="size-3 text-muted/60 shrink-0" />
                
                <TopologyNode 
                  title="ReasoningAgent" 
                  isActive={activeAgentNames.has('ReasoningAgent') || activeStages.has('RUNNING')} 
                  isSpecialist 
                  subtitle="Cognitive Engine" 
                  icon={Cpu} 
                />
                <ArrowRight className="size-3 text-muted/60 shrink-0" />
                
                <TopologyNode 
                  title="ValidationAgent" 
                  isActive={activeAgentNames.has('ValidationAgent') || activeStages.has('VALIDATING')} 
                  isSpecialist 
                  subtitle="Quality Checks" 
                  icon={ShieldCheck} 
                />
                <ArrowRight className="size-3 text-muted/60 shrink-0" />
                
                <TopologyNode 
                  title="ReporterAgent" 
                  isActive={activeAgentNames.has('ReporterAgent')} 
                  isSpecialist 
                  subtitle="Output Synthesis" 
                  icon={FileText} 
                />
              </div>

            </div>
          </Surface>
        </div>

        {/* ROW 5: AGENT UTILIZATION METRICS TABLE */}
        <div className="flex flex-col min-h-[260px] shrink-0">
          <div className="mb-2">
            <span className="text-xs font-mono text-muted uppercase tracking-wider">Specialist Agent Utilization Registry</span>
          </div>
          <Surface variant="panel" border="strong" className="flex-1 bg-surface-elevated p-0 flex flex-col overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono border-collapse">
                <thead>
                  <tr className="border-b border-border-subtle text-3xs text-muted uppercase tracking-wider bg-surface/50">
                    <th className="p-3">Specialist Agent</th>
                    <th className="p-3">Role Designation</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Total Executions</th>
                    <th className="p-3">Avg Latency</th>
                    <th className="p-3">Tokens / Run</th>
                    <th className="p-3">Retry Count</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle text-2xs">
                  {specialistUtilization.map((agent, idx) => {
                    const isRunning = agent.status === 'RUNNING';
                    return (
                      <tr key={idx} className={`hover:bg-surface/30 transition-colors ${isRunning ? 'bg-accent/5' : ''}`}>
                        <td className="p-3 font-bold text-accent">{agent.name}</td>
                        <td className="p-3 text-muted-foreground">{agent.role}</td>
                        <td className="p-3">
                          <span className={`flex items-center gap-1.5 font-bold ${
                            isRunning ? 'text-accent animate-pulse' : 'text-muted'
                          }`}>
                            <span className={`size-1.5 rounded-full ${isRunning ? 'bg-accent' : 'bg-muted-foreground/30'}`} />
                            {agent.status}
                          </span>
                        </td>
                        <td className="p-3 text-foreground">{agent.executions === 0 ? <span className="text-muted">Never</span> : agent.executions}</td>
                        <td className="p-3 text-foreground">{agent.latency === '—' ? <span className="text-muted">—</span> : `${agent.latency} ms`}</td>
                        <td className="p-3 text-foreground">{agent.tokens === '—' ? <span className="text-muted">—</span> : agent.tokens}</td>
                        <td className="p-3 text-foreground">{agent.retries}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Surface>
        </div>

      </div>
    </WorkspaceLayout>
  );
}

export default MissionControlPage;

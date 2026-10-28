import { useEffect, useState } from 'react';
import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import { useExecutionStore } from '@/stores/executionStore';
import {
  Play, Pause, SkipBack, SkipForward, Clock, History, Cpu
} from 'lucide-react';

export function ReplayPage() {
  const { executions, loadExecutions, activeExecution, selectExecution, activeTimeline } = useExecutionStore();
  const [selectedRunId, setSelectedRunId] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  useEffect(() => {
    loadExecutions();
  }, [loadExecutions]);

  useEffect(() => {
    if (executions.length > 0 && !selectedRunId) {
      const first = executions[0].id;
      setSelectedRunId(first);
      selectExecution(first).catch(() => {});
    }
  }, [executions, selectedRunId, selectExecution]);

  // Handle run selection
  const handleSelectRun = async (id: string) => {
    setSelectedRunId(id);
    setCurrentStep(0);
    setIsPlaying(false);
    await selectExecution(id);
  };

  // Playback timer loop
  useEffect(() => {
    let timer: any = null;
    if (isPlaying && activeTimeline && activeTimeline.length > 0) {
      timer = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= activeTimeline.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1500 / playbackSpeed);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isPlaying, activeTimeline, playbackSpeed]);

  const timelineSteps = activeTimeline || [];

  // Realistic mock state changes for visual playback display
  const mockStates = [
    { phase: 'INITIALIZING', agent: 'N/A', memory: '{}', activeNodes: 0 },
    { phase: 'PLANNING', agent: 'PlannerAgent', memory: '{"plan_steps": ["analyze", "gather", "synthesize"]}', activeNodes: 1 },
    { phase: 'RUNNING', agent: 'ResearchAgent', memory: '{"plan_steps": ["analyze", "gather", "synthesize"], "sources": ["web", "docs"]}', activeNodes: 2 },
    { phase: 'RUNNING', agent: 'ReasoningAgent', memory: '{"analysis_complete": true, "findings_count": 4}', activeNodes: 3 },
    { phase: 'VALIDATING', agent: 'ValidationAgent', memory: '{"security_passed": true, "confidence_score": 0.98}', activeNodes: 4 },
    { phase: 'COMPLETED', agent: 'ReporterAgent', memory: '{"report_generated": true, "bytes": 4810}', activeNodes: 5 }
  ];

  // Map step index to one of our mock states
  const stateIndex = Math.min(Math.floor((currentStep / Math.max(timelineSteps.length - 1, 1)) * (mockStates.length - 1)), mockStates.length - 1);
  const activeState = mockStates[stateIndex] || mockStates[0];

  return (
    <WorkspaceLayout
      title="Replay"
      description="Time-travel execution debugger and telemetry playback console."
      state="ready"
      sprintStatus="Sprint 6.0"
    >
      <div className="flex h-full w-full bg-background-dark text-foreground overflow-hidden">
        {/* Left column: Run selector list */}
        <div className="w-80 border-r border-border-subtle flex flex-col min-h-0 bg-surface">
          <div className="p-4 border-b border-border-subtle bg-surface-elevated/40">
            <span className="text-2xs font-mono text-muted uppercase tracking-wider">Execution History</span>
          </div>
          <ScrollableArea className="flex-1 p-2 space-y-2">
            {executions.map((exec) => {
              const isSelected = exec.id === selectedRunId;
              return (
                <button
                  key={exec.id}
                  onClick={() => handleSelectRun(exec.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-all flex flex-col gap-2 ${
                    isSelected
                      ? 'bg-accent/5 border-accent shadow-sm'
                      : 'bg-surface-elevated/20 border-border-subtle hover:bg-surface-elevated/40'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span className="text-xs font-mono font-bold text-foreground">
                      {exec.id.substring(0, 12)}
                    </span>
                    <span className="text-3xs font-mono px-1.5 py-0.5 rounded bg-surface border border-border-subtle">
                      {exec.status}
                    </span>
                  </div>
                  <p className="text-xs text-muted truncate text-left w-full">{exec.userPrompt}</p>
                  <span className="text-3xs font-mono text-muted">
                    {new Date(exec.createdAt * 1000).toLocaleTimeString()}
                  </span>
                </button>
              );
            })}
          </ScrollableArea>
        </div>

        {/* Right column: Debugger Controls & Playback View */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {activeExecution ? (
            <div className="flex-1 flex flex-col min-h-0">
              {/* Playback Control Bar */}
              <div className="p-4 border-b border-border-subtle bg-surface-elevated flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <History className="size-4 text-accent" />
                    <span className="text-sm font-semibold font-mono">
                      PLAYBACK MODE: {selectedRunId.substring(0, 18)}
                    </span>
                  </div>
                  <p className="text-xs text-muted truncate">{activeExecution.userPrompt}</p>
                </div>

                {/* Timeline Controls */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center bg-surface border border-border-subtle rounded-lg p-1">
                    <button
                      onClick={() => setCurrentStep(0)}
                      disabled={timelineSteps.length === 0}
                      className="p-1.5 text-muted hover:text-foreground hover:bg-surface-elevated rounded disabled:opacity-30 transition-colors"
                      title="Reset to Start"
                    >
                      <SkipBack className="size-3.5" />
                    </button>
                    <button
                      onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
                      disabled={currentStep === 0 || timelineSteps.length === 0}
                      className="p-1.5 text-muted hover:text-foreground hover:bg-surface-elevated rounded disabled:opacity-30 transition-colors"
                      title="Step Backward"
                    >
                      <SkipBack className="size-3.5 rotate-180" />
                    </button>
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      disabled={timelineSteps.length === 0}
                      className="p-2 text-white bg-accent hover:bg-accent-hover rounded-md disabled:bg-accent/30 transition-colors mx-1"
                      title={isPlaying ? 'Pause' : 'Play Simulation'}
                    >
                      {isPlaying ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
                    </button>
                    <button
                      onClick={() => setCurrentStep(prev => Math.min(timelineSteps.length - 1, prev + 1))}
                      disabled={currentStep === timelineSteps.length - 1 || timelineSteps.length === 0}
                      className="p-1.5 text-muted hover:text-foreground hover:bg-surface-elevated rounded disabled:opacity-30 transition-colors"
                      title="Step Forward"
                    >
                      <SkipForward className="size-3.5" />
                    </button>
                    <button
                      onClick={() => setCurrentStep(timelineSteps.length - 1)}
                      disabled={timelineSteps.length === 0}
                      className="p-1.5 text-muted hover:text-foreground hover:bg-surface-elevated rounded disabled:opacity-30 transition-colors"
                      title="Jump to End"
                    >
                      <SkipForward className="size-3.5 rotate-180" />
                    </button>
                  </div>

                  {/* Playback speed selector */}
                  <select
                    value={playbackSpeed}
                    onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                    className="bg-surface text-2xs font-mono p-1.5 rounded-lg border border-border-subtle text-foreground outline-none cursor-pointer"
                  >
                    <option value={0.5}>0.5x Speed</option>
                    <option value={1}>1.0x Speed</option>
                    <option value={2}>2.0x Speed</option>
                  </select>
                </div>
              </div>

              {/* Debugger Workspace Layout */}
              <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 min-h-0 overflow-hidden">
                {/* Event timeline timeline (Left 5 Cols) */}
                <div className="lg:col-span-5 flex flex-col min-h-0">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs font-mono text-muted uppercase tracking-wider">Historical Logs ({timelineSteps.length})</span>
                    <span className="text-3xs font-mono text-muted">Step {currentStep + 1} of {timelineSteps.length || 1}</span>
                  </div>
                  <Surface variant="panel" border="strong" className="flex-1 bg-surface-elevated p-0 flex flex-col overflow-hidden">
                    <ScrollableArea className="flex-1 p-3">
                      {timelineSteps.length === 0 ? (
                        <div className="text-xs text-muted font-mono italic text-center py-20">
                          Awaiting timeline logs...
                        </div>
                      ) : (
                        <div className="relative border-l border-border-subtle pl-4 space-y-4">
                          {timelineSteps.map((step, idx) => {
                            const isPast = idx < currentStep;
                            const isCurrent = idx === currentStep;
                            return (
                              <div
                                key={idx}
                                onClick={() => setCurrentStep(idx)}
                                className={`relative cursor-pointer group transition-all duration-300 p-2 rounded-lg ${
                                  isCurrent ? 'bg-accent/5 border border-accent/20' : 'hover:bg-surface'
                                }`}
                              >
                                <span className={`absolute -left-[21px] top-3.5 size-2 rounded-full border-2 ${
                                  isCurrent ? 'bg-accent border-background' :
                                  isPast ? 'bg-success border-background' : 'bg-surface border-border-subtle'
                                }`} />
                                <div className="flex items-center justify-between gap-2">
                                  <span className={`text-2xs font-mono font-bold ${isCurrent ? 'text-accent' : 'text-foreground'}`}>
                                    {step.event}
                                  </span>
                                  <span className="text-3xs font-mono text-muted">
                                    {new Date(step.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                  </span>
                                </div>
                                <p className="text-3xs font-mono text-muted mt-1 leading-normal truncate">{step.detail}</p>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </ScrollableArea>
                  </Surface>
                </div>

                {/* State Diff comparator & Blackboard memory inspector (Right 7 Cols) */}
                <div className="lg:col-span-7 flex flex-col gap-6 min-h-0">
                  {/* System State variables panel */}
                  <div className="flex-1 flex flex-col min-h-0">
                    <span className="text-xs font-mono text-muted uppercase tracking-wider mb-2">Memory & Shared Blackboard State</span>
                    <Surface variant="panel" border="strong" className="flex-1 bg-surface-elevated flex flex-col overflow-hidden">
                      <div className="px-4 py-2 bg-surface border-b border-border-subtle text-3xs font-mono text-muted uppercase flex items-center justify-between">
                        <span>active_context_variables</span>
                        <span>State: {activeState.phase}</span>
                      </div>
                      <div className="flex-1 p-4 bg-surface-elevated/40 font-mono text-2xs leading-relaxed overflow-y-auto">
                        <pre className="text-accent">{JSON.stringify(JSON.parse(activeState.memory), null, 2)}</pre>
                      </div>
                    </Surface>
                  </div>

                  {/* Operational telemetry variables */}
                  <div className="h-44 flex flex-col shrink-0">
                    <span className="text-xs font-mono text-muted uppercase tracking-wider mb-2">State Telemetry Variables</span>
                    <div className="grid grid-cols-2 gap-4">
                      <Surface variant="panel" border="strong" className="p-3 bg-surface-elevated/50">
                        <div className="text-3xs font-mono text-muted uppercase">Active Specialist</div>
                        <div className="text-sm font-semibold font-mono text-accent mt-1 flex items-center gap-1.5">
                          <Cpu className="size-4 animate-pulse text-accent" />
                          {activeState.agent}
                        </div>
                      </Surface>
                      <Surface variant="panel" border="strong" className="p-3 bg-surface-elevated/50">
                        <div className="text-3xs font-mono text-muted uppercase">Execution Phase</div>
                        <div className="text-sm font-semibold font-mono text-foreground mt-1 flex items-center gap-1.5">
                          <Clock className="size-4 text-muted" />
                          {activeState.phase}
                        </div>
                      </Surface>
                    </div>
                  </div>
                </div>
              </div>

              {/* Scrubber timeline bar (Bottom row) */}
              <div className="p-4 border-t border-border-subtle bg-surface flex items-center gap-4 shrink-0">
                <span className="text-3xs font-mono text-muted shrink-0 w-8">STEP {currentStep}</span>
                <input
                  type="range"
                  min={0}
                  max={Math.max(timelineSteps.length - 1, 0)}
                  value={currentStep}
                  onChange={(e) => setCurrentStep(Number(e.target.value))}
                  className="flex-1 h-1 bg-border-subtle rounded-lg appearance-none cursor-pointer accent-accent"
                />
                <span className="text-3xs font-mono text-muted shrink-0 w-8">MAX {timelineSteps.length - 1}</span>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col min-h-0">
              {/* Disabled playback bar — shows intent without requiring data */}
              <div className="p-4 border-b border-border-subtle bg-surface-elevated flex flex-col md:flex-row md:items-center justify-between gap-4 opacity-40 pointer-events-none select-none">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <History className="size-4 text-accent" />
                    <span className="text-sm font-semibold font-mono">PLAYBACK MODE: —</span>
                  </div>
                  <p className="text-xs text-muted">No execution selected</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center bg-surface border border-border-subtle rounded-lg p-1">
                    <button disabled className="p-1.5 text-muted rounded disabled:opacity-30"><SkipBack className="size-3.5" /></button>
                    <button disabled className="p-1.5 text-muted rounded disabled:opacity-30"><SkipBack className="size-3.5 rotate-180" /></button>
                    <button disabled className="p-2 text-white bg-accent/30 rounded-md mx-1"><Play className="size-3.5" /></button>
                    <button disabled className="p-1.5 text-muted rounded disabled:opacity-30"><SkipForward className="size-3.5" /></button>
                    <button disabled className="p-1.5 text-muted rounded disabled:opacity-30"><SkipForward className="size-3.5 rotate-180" /></button>
                  </div>
                  <select disabled className="bg-surface text-2xs font-mono p-1.5 rounded-lg border border-border-subtle text-muted outline-none opacity-50">
                    <option>1.0x Speed</option>
                  </select>
                </div>
              </div>

              {/* Idle content */}
              <div className="flex-1 flex items-center justify-center">
                <div className="max-w-md text-center space-y-5">
                  <div className="space-y-2">
                    <h3 className="text-sm font-semibold font-mono text-foreground">Execution History</h3>
                    <p className="text-xs text-muted leading-relaxed">
                      Replay allows historical executions to be inspected frame-by-frame.
                      No executions have been archived yet.
                    </p>
                    <p className="text-xs text-muted/60">
                      Run an execution from Execution Center to populate replay history.
                    </p>
                  </div>

                  {/* Disabled filter/timeline headers */}
                  <div className="border border-border-subtle rounded-lg overflow-hidden opacity-50 select-none">
                    <div className="px-4 py-2 bg-surface border-b border-border-subtle flex items-center justify-between">
                      <span className="text-3xs font-mono text-muted uppercase tracking-wider">Filters</span>
                      <span className="text-3xs font-mono text-muted">—</span>
                    </div>
                    <div className="px-4 py-2 bg-surface-elevated/20 border-b border-border-subtle flex items-center justify-between">
                      <span className="text-3xs font-mono text-muted uppercase tracking-wider">Timeline</span>
                      <span className="text-3xs font-mono text-muted">No timeline available</span>
                    </div>
                    <div className="px-4 py-2 bg-surface-elevated/20 flex items-center justify-between">
                      <span className="text-3xs font-mono text-muted uppercase tracking-wider">Playback Speed</span>
                      <span className="text-3xs font-mono text-muted">1.0×</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </WorkspaceLayout>
  );
}
export default ReplayPage;

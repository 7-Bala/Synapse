import { WorkspaceLayout } from '@/layouts/WorkspaceLayout';
import { Surface } from '@/design-system/primitives/Surface';
import { ScrollableArea } from '@/design-system/primitives/ScrollableArea';
import {
  Cpu, Sliders, Sparkles, CheckSquare, AlertCircle
} from 'lucide-react';

interface AgentRegistryItem {
  name: string;
  role: string;
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  capabilities: string[];
  status: 'REGISTERED' | 'IDLE' | 'RUNNING';
}

const mockSwarmAgents: AgentRegistryItem[] = [
  {
    name: 'Planner Specialist',
    role: 'Swarm Task Decomposition Coordinator',
    model: 'runtime-model-v1',
    temperature: 0.1,
    maxTokens: 4096,
    systemPrompt: `You are the Swarm Decomposition Coordinator.
Analyze user objectives and divide them into a structured sequence of execution phases.
Assign specialist agent designations for each phase.
Produce structured plan outputs conforming to the planner schema definition.`,
    capabilities: ['Objective Decomposition', 'Swarm Task Allocation', 'Dynamic Pipeline Synthesis'],
    status: 'IDLE'
  },
  {
    name: 'Research Specialist',
    role: 'Context Ingestion Specialist',
    model: 'runtime-model-v1',
    temperature: 0.2,
    maxTokens: 8192,
    systemPrompt: `You are the Ingestion Specialist.
Retrieve relevant file contents, database configurations, and environment states.
Filter logs and structure evidence context into a unified schema.
Minimize retrieval noise.`,
    capabilities: ['Workspace File Scanning', 'Query Optimization Analysis', 'Logs Filtering'],
    status: 'IDLE'
  },
  {
    name: 'Reasoning Specialist',
    role: 'Cognitive Execution Specialist',
    model: 'runtime-model-v1',
    temperature: 0.4,
    maxTokens: 8192,
    systemPrompt: `You are the Cognitive Specialist.
Analyze research context, identify discrepancies, and synthesize target solutions.
Document logical steps and produce evidence traces detailing intermediate conclusions.`,
    capabilities: ['Cognitive Analysis', 'Discrepancy Troubleshooting', 'In-memory Blackboard Writes'],
    status: 'IDLE'
  },
  {
    name: 'Validation Specialist',
    role: 'Swarm Verification Specialist',
    model: 'runtime-model-v1',
    temperature: 0.1,
    maxTokens: 4096,
    systemPrompt: `You are the Verification Specialist.
Test outputs against security policies, syntactic schemas, and compile constraints.
Run pytest validation simulations and report exit codes.`,
    capabilities: ['Syntactic Compliance Scans', 'Pytest Operational Scenarios', 'Security Bounds Testing'],
    status: 'IDLE'
  },
  {
    name: 'Reporter Specialist',
    role: 'Synthesis & Deliverables Specialist',
    model: 'runtime-model-v1',
    temperature: 0.3,
    maxTokens: 4096,
    systemPrompt: `You are the Reporter Specialist.
Ingest validation reports, trace data deliverables, and compose release summaries.
Format final synthesized markdown files.`,
    capabilities: ['Deliverables Synthesis', 'Markdown Code Generation', 'Run Summary Compilations'],
    status: 'IDLE'
  }
];

export function AgentsPage() {
  return (
    <WorkspaceLayout
      title="Agents"
      description="Inspect specialist agent swarms, capability registries, and LLM configuration parameters."
      state="ready"
      sprintStatus="Sprint 6.0"
    >
      <ScrollableArea className="h-full w-full bg-background-dark p-6">
        <div className="max-w-6xl mx-auto space-y-8">
          
          {/* swarms definition overview banner */}
          <Surface variant="panel" border="strong" className="p-5 bg-surface-elevated/40 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <Sparkles className="size-4 text-accent" />
                <span className="text-sm font-semibold font-mono text-foreground">Swarm Specialist Configuration Hub</span>
              </div>
              <p className="text-xs text-muted">
                Each agent operates within an isolated thread context, publishing to the global telemetric event bus.
              </p>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 bg-accent/10 border border-accent/20 rounded-lg text-accent text-xs font-mono">
              <Sliders className="size-3.5" />
              <span>5 Registry Nodes Active</span>
            </div>
          </Surface>

          {/* Grid of Agents */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mockSwarmAgents.map((agent, i) => (
              <Surface key={i} variant="panel" border="strong" className="flex flex-col bg-surface-elevated/20 p-5 gap-4 hover:border-accent/40 hover:bg-surface-elevated transition-all duration-300">
                {/* Header info */}
                <div className="flex items-start justify-between border-b border-border-subtle pb-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Cpu className="size-4 text-accent" />
                      <span className="text-sm font-mono font-bold text-foreground">{agent.name}</span>
                    </div>
                    <span className="text-3xs font-mono text-muted uppercase tracking-wider block">
                      {agent.role}
                    </span>
                  </div>
                  <span className="text-3xs font-mono bg-surface border border-border-subtle px-2 py-0.5 rounded-full text-foreground uppercase tracking-widest">
                    {agent.model}
                  </span>
                </div>

                {/* Configurations */}
                <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                  <div>
                    <span className="text-3xs text-muted block uppercase">Temperature Parameter</span>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-1.5 bg-border-subtle rounded-full overflow-hidden">
                        <div className="h-full bg-accent rounded-full" style={{ width: `${agent.temperature * 100}%` }} />
                      </div>
                      <span className="text-2xs font-semibold text-foreground">{agent.temperature}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-3xs text-muted block uppercase">Token Cap Limit</span>
                    <span className="text-2xs font-semibold text-foreground mt-1 block">{agent.maxTokens.toLocaleString()} tokens</span>
                  </div>
                </div>

                {/* System instructions textbox */}
                <div className="space-y-1.5">
                  <span className="text-3xs font-mono text-muted uppercase tracking-wider">System Instructions Console</span>
                  <div className="bg-surface border border-border-subtle p-3 rounded-lg font-mono text-3xs text-muted leading-relaxed max-h-24 overflow-y-auto whitespace-pre-wrap select-none">
                    {agent.systemPrompt}
                  </div>
                </div>

                {/* Capabilities Checklist */}
                <div className="space-y-1.5">
                  <span className="text-3xs font-mono text-muted uppercase tracking-wider">Registered Swarm Capabilities</span>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {agent.capabilities.map((cap, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 px-2 py-1 rounded bg-surface border border-border-subtle text-3xs font-mono text-muted">
                        <CheckSquare className="size-3 text-accent shrink-0" />
                        <span className="truncate">{cap}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Swarm Metrics — idle state */}
                <div className="pt-3 border-t border-border-subtle grid grid-cols-3 gap-4 text-center font-mono">
                  <div>
                    <div className="text-3xs text-muted uppercase">Last Execution</div>
                    <div className="text-xs font-semibold text-muted mt-0.5">Never</div>
                  </div>
                  <div>
                    <div className="text-3xs text-muted uppercase">Status</div>
                    <div className="text-xs font-bold text-foreground mt-0.5 flex items-center justify-center gap-1.5">
                      <span className="size-1.5 rounded-full bg-muted-foreground/30" />
                      {agent.status}
                    </div>
                  </div>
                  <div>
                    <div className="text-3xs text-muted uppercase">Invocations</div>
                    <div className="text-xs font-semibold text-muted mt-0.5">0 runs</div>
                  </div>
                </div>

              </Surface>
            ))}
          </div>

          {/* swarms policy guidelines footer */}
          <div className="p-4 border border-border-subtle bg-surface-elevated/10 rounded-lg flex items-start gap-3 font-mono text-3xs text-muted leading-relaxed">
            <AlertCircle className="size-4 text-accent shrink-0" />
            <div>
              <span className="text-2xs font-bold text-foreground uppercase block mb-1">Swarm Guardrails Enforcement</span>
              Any Swarm agent exceeding the token cap limit or encountering a validation pytest compliance exit code higher than 0 is subjected to the retry policy logic automatically. See Settings panel for policy timeouts.
            </div>
          </div>

        </div>
      </ScrollableArea>
    </WorkspaceLayout>
  );
}
export default AgentsPage;

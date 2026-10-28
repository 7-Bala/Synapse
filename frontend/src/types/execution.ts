export type ExecutionState = 'QUEUED' | 'INITIALIZING' | 'PLANNING' | 'RUNNING' | 'VALIDATING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';

export interface TimelineEntry {
  timestamp: number;
  event: string;
  detail: string;
  agent?: string;
}

export interface ExecutionRecord {
  id: string;
  status: ExecutionState;
  createdAt: number;
  updatedAt: number;
  startedAt?: number;
  completedAt?: number;
  userPrompt: string;
  executionMode: 'LIVE' | 'SIMULATION' | 'REPLAY';
  currentAgent?: string;
  totalLatency: number;
  totalTokens: number;
  estimatedCost: number;
  metadata: Record<string, any>;
  // Milestone 3 runtime fields
  timeline: TimelineEntry[];
  activeAgentCount: number;
  completedAgentCount: number;
  failedAgentCount: number;
  retryCount: number;
  progress: number;
}


export interface AgentNode {
  id: string;
  name: string;
  role: string;
  model: string;
  status: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'RETRIES';
  input?: string;
  output?: string;
  latency: number;
  tokenUsage: number;
  confidence: number;
  retryCount: number;
  parentId?: string;
  childrenIds: string[];
}

export type ExecutionStatus = 'IDLE' | 'RUNNING' | 'PAUSED' | 'FINISHED' | 'FAILED';

export interface ExecutionMetadata {
  id: string;
  startTime: string;
  endTime?: string;
  triggeredBy: string;
}

export interface ExecutionNode {
  id: string;
  agentName: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED' | 'BLOCKED';
  startTime?: string;
  endTime?: string;
}

export interface ExecutionEdge {
  id: string;
  source: string;
  target: string;
}

export interface ExecutionGraph {
  nodes: ExecutionNode[];
  edges: ExecutionEdge[];
}

export interface Execution {
  id: string;
  status: ExecutionStatus;
  metadata: ExecutionMetadata;
  graph: ExecutionGraph;
}

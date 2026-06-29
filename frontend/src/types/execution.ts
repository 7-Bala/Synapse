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

/**
 * Blackboard memory schemas reflecting backend/schemas/blackboard.py.
 */
export interface Producer {
  agentName: string;
  tickId: number;
}

export interface Consumer {
  agentName: string;
  tickId: number;
}

export interface BlackboardEntry {
  tickId: number;
  agentName: string;
  output: Record<string, unknown>; // Maps to AgentOutput
  timestamp: string;
}

export interface BlackboardSnapshot {
  entries: BlackboardEntry[];
  latestTick: number;
}

export interface Mutation {
  path: string;
  value: unknown;
  oldValue?: unknown;
}

export interface BlackboardDiff {
  tickId: number;
  mutations: Mutation[];
}

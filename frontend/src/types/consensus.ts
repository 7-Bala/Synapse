/**
 * Consensus models mapping to the backend Consensus engine.
 */
export interface Vote {
  agentName: string;
  decision: string;
  confidence: number;
  reasoning: string;
}

export interface CommitteeMember {
  agentName: string;
  role: string;
}

export interface Dissent {
  agentName: string;
  reason: string;
}

export interface Resolution {
  decision: string;
  confidence: number;
  explanation: string;
}

export interface ConsensusResult {
  resolution: Resolution;
  votes: Vote[];
  dissenters: Dissent[];
  humanReviewRequired: boolean;
  timestamp: string;
}

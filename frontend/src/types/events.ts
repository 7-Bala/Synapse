import type { UUID, ISO8601Timestamp, ExecutionId } from './common';

export type EventType =
  | 'ExecutionStarted'
  | 'ExecutionPaused'
  | 'ExecutionResumed'
  | 'ExecutionFinished'
  | 'ExecutionFailed'
  | 'TickStarted'
  | 'TickCompleted'
  | 'NodeStarted'
  | 'NodeCompleted'
  | 'ValidatorBlocked'
  | 'ValidatorOverridden'
  | 'BlackboardUpdated'
  | 'ConsensusReached'
  | 'ReplayLoaded'
  | 'ToolCallExecuted'
  | 'EvidenceDiscovered';

export interface EventEnvelope<T> {
  id: UUID;
  timestamp: ISO8601Timestamp;
  executionId: ExecutionId;
  type: EventType;
  version: number;
  payload: T;
}

export interface ExecutionStartedPayload {
  metadata: Record<string, unknown>;
}

export interface ExecutionPausedPayload {
  reason: string;
}

export type ExecutionResumedPayload = Record<string, never>;

export interface ExecutionFinishedPayload {
  finalOutput: unknown;
}

export interface ExecutionFailedPayload {
  error: string;
}

export interface TickStartedPayload {
  tickId: number;
}

export interface TickCompletedPayload {
  tickId: number;
}

export interface NodeStartedPayload {
  nodeId: string;
  agentName: string;
}

export interface NodeCompletedPayload {
  nodeId: string;
  agentName: string;
  output: unknown;
}

export interface ValidatorBlockedPayload {
  validatorId: string;
  reason: string;
}

export interface ValidatorOverriddenPayload {
  validatorId: string;
  overriddenBy: string;
}

export interface BlackboardUpdatedPayload {
  tickId: number;
  diff: unknown;
}

export interface ConsensusReachedPayload {
  consensusResult: unknown;
}

export interface ReplayLoadedPayload {
  replayId: string;
}

export interface ToolCallExecutedPayload {
  toolCallId: string;
  result: unknown;
}

export interface EvidenceDiscoveredPayload {
  evidenceId: string;
}

export type DomainEvent =
  | EventEnvelope<ExecutionStartedPayload>
  | EventEnvelope<ExecutionPausedPayload>
  | EventEnvelope<ExecutionResumedPayload>
  | EventEnvelope<ExecutionFinishedPayload>
  | EventEnvelope<ExecutionFailedPayload>
  | EventEnvelope<TickStartedPayload>
  | EventEnvelope<TickCompletedPayload>
  | EventEnvelope<NodeStartedPayload>
  | EventEnvelope<NodeCompletedPayload>
  | EventEnvelope<ValidatorBlockedPayload>
  | EventEnvelope<ValidatorOverriddenPayload>
  | EventEnvelope<BlackboardUpdatedPayload>
  | EventEnvelope<ConsensusReachedPayload>
  | EventEnvelope<ReplayLoadedPayload>
  | EventEnvelope<ToolCallExecutedPayload>
  | EventEnvelope<EvidenceDiscoveredPayload>;

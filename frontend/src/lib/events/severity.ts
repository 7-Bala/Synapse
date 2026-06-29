export type EventSeverity = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'UNKNOWN';

export function getEventSeverity(eventType: string): EventSeverity {
  switch (eventType) {
    case 'ExecutionStarted':
    case 'TickStarted':
    case 'NodeStarted':
    case 'AgentStateChanged':
    case 'ToolCallStarted':
    case 'ConsensusStarted':
      return 'INFO';

    case 'ExecutionFinished':
    case 'TickCompleted':
    case 'NodeCompleted':
    case 'ToolCallCompleted':
    case 'ConsensusCompleted':
      return 'SUCCESS';

    case 'RecoveryTriggered':
    case 'RetryScheduled':
    case 'WarningEmitted':
      return 'WARNING';

    case 'ExecutionFailed':
    case 'NodeFailed':
    case 'ToolCallFailed':
    case 'ValidationFailed':
    case 'ErrorEmitted':
      return 'ERROR';

    default:
      return 'UNKNOWN';
  }
}

/**
 * Replay schemas for time-travel debugging.
 */
export interface ReplayMetadata {
  id: string;
  executionId: string;
  recordedAt: string;
  durationMs: number;
  totalTicks: number;
}

export interface ReplayTick {
  tickId: number;
  timestamp: string;
  events: Record<string, unknown>[];
  blackboardSnapshot: Record<string, unknown>;
}

export interface ReplayCursor {
  currentTick: number;
  playbackSpeed: number;
  isPlaying: boolean;
}

export interface ReplaySession {
  metadata: ReplayMetadata;
  ticks: ReplayTick[];
  cursor: ReplayCursor;
}

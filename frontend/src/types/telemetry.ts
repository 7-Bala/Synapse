/**
 * Telemetry models mirroring backend observability.
 */
export interface TokenUsage {
  tokensIn: number;
  tokensOut: number;
}

export interface Latency {
  durationMs: number;
}

export interface MemoryUsage {
  bytesUsed: number;
}

export interface Timing {
  startTime: string;
  endTime?: string;
}

export interface Telemetry {
  tokens: TokenUsage;
  latency: Latency;
  memory: MemoryUsage;
  timing: Timing;
}

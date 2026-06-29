/**
 * ToolCall schemas for representing API/function interactions.
 */
export interface ToolRequest {
  id: string;
  name: string;
  parameters: Record<string, unknown>;
  timestamp: string;
}

export interface ToolResponse {
  requestId: string;
  result: unknown;
  timestamp: string;
}

export interface ToolError {
  requestId: string;
  error: string;
  timestamp: string;
}

export interface ToolCall {
  id: string;
  request: ToolRequest;
  response?: ToolResponse;
  error?: ToolError;
  latencyMs?: number;
}

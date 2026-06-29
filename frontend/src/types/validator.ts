/**
 * Validator mapping schemas.
 */
export type ValidationSeverity = 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

export type ValidationStage = 'PRE_EXECUTION' | 'IN_FLIGHT' | 'POST_EXECUTION';

export interface ValidationResult {
  id: string;
  stage: ValidationStage;
  severity: ValidationSeverity;
  message: string;
  blocked: boolean;
  timestamp: string;
}

export interface OverrideRequest {
  validationId: string;
  reason: string;
  requestedBy: string;
}

export interface OverrideResult {
  validationId: string;
  success: boolean;
  timestamp: string;
  overrideBy: string;
}

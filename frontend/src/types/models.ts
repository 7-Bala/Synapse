export type HealthStatus = 'HEALTHY' | 'DEGRADED' | 'FAILED' | 'UNKNOWN'

export type DeploymentDecision = 'READY' | 'READY_WITH_WARNINGS' | 'NOT_READY'

export type StageStatus = 'PASSED' | 'WARNING' | 'FAILED' | 'SKIPPED'

export type PipelineStatus =
  | 'idle'
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface ComponentHealth {
  name: string
  status: HealthStatus
  message: string
  timestamp: string
  metadata: Record<string, unknown>
}

export interface SystemHealth {
  overall_status: HealthStatus
  generated_at: string
  components: Record<string, ComponentHealth>
}

export interface ProcessMetrics {
  cpu_percent: number
  cpu_time_seconds: number
  rss_memory_mb: number
  vms_memory_mb: number
  thread_count: number
  open_file_count: number
  process_uptime_seconds: number
  pid: number
  psutil_available: boolean
}

export interface FilesystemMetrics {
  artifacts_size_bytes: number
  archive_size_bytes: number
  cache_size_bytes: number
  disk_available_bytes: number
  disk_total_bytes: number
  disk_utilization_percent: number
}

export interface CacheMetrics {
  entry_count: number
  cache_size_bytes: number
  hit_ratio: number
  miss_ratio: number
  corruption_count: number
  cleanup_count: number
  expired_entry_count: number
}

export interface CircuitBreakerMetrics {
  state: string
  failure_count: number
  recovery_count: number
  rejection_count: number
  transition_count: number
  uptime_seconds: number
}

export interface RetryMetrics {
  retry_attempts: number
  retry_successes: number
  retry_failures: number
  exhausted_retries: number
  average_retry_delay_ms: number
}

export interface ResourceViolation {
  metric: string
  value: number
  threshold: number
  level: HealthStatus
  message: string
}

export interface ResourceReport {
  generated_at: string
  overall_status: HealthStatus
  process: ProcessMetrics
  filesystem: FilesystemMetrics
  runtime: Record<string, string>
  cache: CacheMetrics
  event_bus: Record<string, number>
  circuit_breakers: Record<string, CircuitBreakerMetrics>
  retry_policy: RetryMetrics
  violations: ResourceViolation[]
  recommendations: string[]
}

export interface ValidationFinding {
  severity: 'ERROR' | 'WARNING' | 'INFO'
  stage: string
  message: string
}

export interface StageResult {
  name: string
  status: StageStatus
  score: number
  duration_ms: number
  findings: ValidationFinding[]
  detail: Record<string, unknown>
}

export interface OperationalReport {
  generated_at: string
  decision: DeploymentDecision
  readiness_score: number
  implementation_status: HealthStatus
  environmental_status: HealthStatus
  stages: StageResult[]
  summary: string
}

export interface EvaluationMetrics {
  pass_rate: number
  accuracy: number
  total_scenarios: number
  passed_scenarios: number
  failed_scenarios: number
  generated_at: string
}

export interface BenchmarkMetrics {
  average_latency_ms: number
  p95_latency_ms: number
  p99_latency_ms: number
  failure_rate: number
  determinism_rate: number
  total_runs: number
  generated_at: string
}

export interface ReplaySummary {
  id: string
  scenario: string
  created_at: string
  status: 'valid' | 'invalid' | 'pending'
  event_count: number
  determinism_verified: boolean
}

export interface ReplayDetail extends ReplaySummary {
  events: unknown[]
  manifest: Record<string, unknown>
  certificate: Record<string, unknown>
  metrics: Record<string, unknown>
  prompt_bundle: Record<string, unknown>
}

export interface PipelineExecution {
  id: string
  scenario: string
  status: PipelineStatus
  started_at: string
  completed_at?: string
  current_stage?: string
  progress: number
  replay_id?: string
}

export interface PipelineLogEntry {
  timestamp: string
  level: 'info' | 'warn' | 'error' | 'debug'
  source: string
  message: string
}

export interface FailureInjectionStatus {
  enabled: boolean
  active_profile?: string
  scenarios_run: number
  recovery_success_rate: number
  circuit_transitions: number
  retry_attempts: number
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  read: boolean
}

export interface DashboardSummary {
  system_status: HealthStatus
  replay_count: number
  evaluation_status: DeploymentDecision
  operational_readiness: DeploymentDecision
  benchmark: BenchmarkMetrics
  health: SystemHealth
  recent_executions: PipelineExecution[]
}

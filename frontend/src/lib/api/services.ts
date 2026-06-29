import { apiGet, apiPost, unwrap } from '@/lib/api/client'
import type {
  ApiResponse,
  FailureInjectionRequest,
  ListReplaysParams,
  PaginatedResponse,
  RunPipelineRequest,
} from '@/types/api'
import type {
  BenchmarkMetrics,
  DashboardSummary,
  EvaluationMetrics,
  FailureInjectionStatus,
  OperationalReport,
  PipelineExecution,
  PipelineLogEntry,
  ReplayDetail,
  ReplaySummary,
  ResourceReport,
  SystemHealth,
} from '@/types/models'

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value))
  }
  const query = search.toString()
  return query ? `?${query}` : ''
}

export const dashboardApi = {
  getSummary: () => apiGet<ApiResponse<DashboardSummary>>('/dashboard').then(unwrap),
}

export const healthApi = {
  getSystem: () => apiGet<ApiResponse<SystemHealth>>('/health').then(unwrap),
  getResources: () => apiGet<ApiResponse<ResourceReport>>('/health/resources').then(unwrap),
}

export const pipelineApi = {
  run: (request: RunPipelineRequest) =>
    apiPost<ApiResponse<PipelineExecution>>('/pipeline/run', request).then(unwrap),
  getStatus: (id: string) =>
    apiGet<ApiResponse<PipelineExecution>>(`/pipeline/${id}`).then(unwrap),
  getLogs: (id: string) =>
    apiGet<ApiResponse<PipelineLogEntry[]>>(`/pipeline/${id}/logs`).then(unwrap),
  listRecent: () =>
    apiGet<ApiResponse<PipelineExecution[]>>('/pipeline/recent').then(unwrap),
}

export const replayApi = {
  list: (params: ListReplaysParams = {}) =>
    apiGet<PaginatedResponse<ReplaySummary>>(
      `/replays${buildQuery(params as Record<string, string | number | undefined>)}`,
    ),
  get: (id: string) => apiGet<ApiResponse<ReplayDetail>>(`/replays/${id}`).then(unwrap),
  download: (id: string, artifact: string) =>
    apiGet<Blob>(`/replays/${id}/download/${artifact}`),
}

export const provenanceApi = {
  getChain: (replayId: string) =>
    apiGet<ApiResponse<Record<string, unknown>>>(`/provenance/${replayId}`).then(unwrap),
  validate: (replayId: string) =>
    apiPost<ApiResponse<{ valid: boolean; findings: string[] }>>(
      `/provenance/${replayId}/validate`,
    ).then(unwrap),
}

export const evaluationApi = {
  getMetrics: () => apiGet<ApiResponse<EvaluationMetrics>>('/evaluation').then(unwrap),
  getHistory: () =>
    apiGet<ApiResponse<EvaluationMetrics[]>>('/evaluation/history').then(unwrap),
}

export const benchmarkApi = {
  getMetrics: () => apiGet<ApiResponse<BenchmarkMetrics>>('/benchmark').then(unwrap),
  getHistory: () =>
    apiGet<ApiResponse<BenchmarkMetrics[]>>('/benchmark/history').then(unwrap),
}

export const operationalApi = {
  getReport: () => apiGet<ApiResponse<OperationalReport>>('/operational').then(unwrap),
}

export const failureInjectionApi = {
  getStatus: () =>
    apiGet<ApiResponse<FailureInjectionStatus>>('/failure-injection').then(unwrap),
  configure: (request: FailureInjectionRequest) =>
    apiPost<ApiResponse<FailureInjectionStatus>>('/failure-injection', request).then(unwrap),
}

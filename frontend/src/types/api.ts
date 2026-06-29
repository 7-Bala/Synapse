export class ApiError extends Error {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export interface ApiResponse<T> {
  data: T
  meta?: {
    timestamp: string
    request_id?: string
  }
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
}

export interface ListReplaysParams {
  page?: number
  page_size?: number
  search?: string
  status?: string
}

export interface RunPipelineRequest {
  scenario: string
  profile?: string
  offline?: boolean
}

export interface FailureInjectionRequest {
  profile: string
  scenario: string
  enabled: boolean
}

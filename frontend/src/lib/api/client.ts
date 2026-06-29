import { ApiError, type ApiResponse } from '@/types/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const body = (await response.json()) as { message?: string; detail?: string }
      message = body.message ?? body.detail ?? message
    } catch {
      // response body is not JSON
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    method: 'GET',
    headers: {
      Accept: 'application/json',
      ...init?.headers,
    },
  })
  return handleResponse<T>(response)
}

export async function apiPost<T>(
  path: string,
  body?: unknown,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  return handleResponse<T>(response)
}

export async function apiDelete<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    method: 'DELETE',
    headers: {
      Accept: 'application/json',
      ...init?.headers,
    },
  })
  return handleResponse<T>(response)
}

export function unwrap<T>(response: ApiResponse<T>): T {
  return response.data
}

import type {
  ApiKey,
  ApiKeyCreate,
  BillingInfo,
  CheckoutSessionStatus,
  LogEntry,
  Profile,
  Usage,
  UsageSummary,
} from './api-types'

const API_BASE_URL = '/api/proxy'

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function errorMessage(response: Response) {
  const body = (await response.json().catch(() => null)) as {
    detail?: string
  } | null
  return body?.detail ?? `Request failed: ${response.status}`
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include',
    cache: 'no-store',
  })
  if (response.status === 401) {
    window.location.assign(
      `/login?returnTo=${encodeURIComponent(window.location.pathname + window.location.search)}`,
    )
    throw new Error('Your session expired. Please sign in again.')
  }
  if (!response.ok) {
    throw new ApiError(await errorMessage(response), response.status)
  }
  return (await response.json()) as T
}

export const api = {
  getProfile: () => apiRequest<Profile>('/profile'),
  getUsage: () => apiRequest<Usage>('/usage'),
  getUsageSummary: (range: '24h' | '7d' | '30d' = '7d') =>
    apiRequest<UsageSummary>(`/usage/summary?range=${range}`),
  listApiKeys: () => apiRequest<{ keys: ApiKey[] }>('/api-keys'),
  createApiKey: (name?: string) =>
    apiRequest<ApiKeyCreate>('/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
  revokeApiKey: (keyId: string) =>
    apiRequest<{ id: string; status: string; message: string }>(
      `/api-keys/${keyId}/revoke`,
      { method: 'POST' },
    ),
  getLogs: (limit = 3) =>
    apiRequest<{ logs: LogEntry[]; total: number }>(`/logs?limit=${limit}`),
  getBilling: () => apiRequest<BillingInfo>('/billing'),
  createCheckoutSession: (plan: string) =>
    apiRequest<{ url: string; session_id: string }>(
      '/billing/create-checkout-session',
      { method: 'POST', body: JSON.stringify({ plan }) },
    ),
  getCheckoutSessionStatus: (sessionId: string) =>
    apiRequest<CheckoutSessionStatus>(
      `/billing/session-status?session_id=${encodeURIComponent(sessionId)}`,
    ),
}

export type {
  ApiKey,
  ApiKeyCreate,
  BillingInfo,
  CheckoutSessionStatus,
  LogEntry,
  Profile,
  Usage,
  UsageSummary,
} from './api-types'

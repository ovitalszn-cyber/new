import { clearSessionTokens, isSessionExpired, loadSessionTokens, saveSessionTokens } from './auth-storage'

const API_BASE_URL = '/api/proxy'

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const session = loadSessionTokens()
  if (!session?.refreshToken) {
    return null
  }

  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: session.refreshToken }),
        })

        if (!response.ok) {
          clearSessionTokens()
          return null
        }

        const data = await response.json()
        saveSessionTokens({
          access_token: data.access_token,
          refresh_token: data.refresh_token,
          expires_at: data.expires_at,
          user: data.user,
        })
        return data.access_token as string
      } catch {
        clearSessionTokens()
        return null
      } finally {
        refreshPromise = null
      }
    })()
  }

  return refreshPromise
}

async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') {
    return null
  }

  const session = loadSessionTokens()
  if (session?.accessToken) {
    if (isSessionExpired(session)) {
      return refreshAccessToken()
    }
    return session.accessToken
  }

  const legacyToken = localStorage.getItem('google_id_token')
  return legacyToken
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken()

  if (!token) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    throw new Error('Please log in to access this feature')
  }

  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  })

  if (response.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      const retry = await fetch(url, {
        ...options,
        headers: {
          'Authorization': `Bearer ${refreshed}`,
          'Content-Type': 'application/json',
          ...options.headers,
        },
        credentials: 'include',
      })
      if (retry.ok) {
        return retry.json()
      }
    }
    clearSessionTokens()
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    throw new Error('Session expired. Please log in again.')
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'API request failed' }))
    throw new Error(error.detail || `Request failed: ${response.status}`)
  }

  return response.json()
}

export async function exchangeGoogleIdToken(idToken: string) {
  const response = await fetch(`${API_BASE_URL}/auth/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Auth exchange failed' }))
    throw new Error(error.detail || 'Auth exchange failed')
  }

  const data = await response.json()
  saveSessionTokens({
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    expires_at: data.expires_at,
    user: data.user,
  })
  return data
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
    apiRequest<{ id: string; status: string; message: string }>(`/api-keys/${keyId}/revoke`, {
      method: 'POST',
    }),

  getLogs: (params?: { limit?: number; offset?: number; status?: string }) => {
    const cleanParams: Record<string, string> = {}
    if (params?.limit !== undefined) cleanParams.limit = String(params.limit)
    if (params?.offset !== undefined) cleanParams.offset = String(params.offset)
    if (params?.status && params.status !== 'undefined') cleanParams.status = params.status
    const query = new URLSearchParams(cleanParams).toString()
    return apiRequest<LogsResponse>(`/logs${query ? `?${query}` : ''}`)
  },

  getBilling: () => apiRequest<BillingInfo>('/billing'),
  getBillingHistory: () => apiRequest<{ invoices: any[] }>('/billing/history'),

  createCheckoutSession: (plan: string) =>
    apiRequest<{ url: string; session_id: string }>('/billing/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({ plan }),
    }),

  getCheckoutSessionStatus: (sessionId: string) =>
    apiRequest<CheckoutSessionStatus>(`/billing/session-status?session_id=${encodeURIComponent(sessionId)}`),

  getTeam: () => apiRequest<{ members: TeamMember[] }>('/team'),
  inviteTeamMember: (email: string, role: string = 'member') =>
    apiRequest<{ success: boolean; invite_id: string }>('/team/invite', {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    }),
}

export interface Profile {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  tier: string
  created_at: string
}

export interface Usage {
  user_id: string
  email: string
  plan: string
  requests_today: number
  requests_this_month: number
  requests_per_min: number
  current_rpm: number
  monthly_quota: number
  monthly_used: number
  monthly_remaining: number
  limit_per_min: number
  limit_month: number
  last_request_at: string
}

export interface UsageSummary {
  total_requests: number
  error_count: number
  error_rate: number
  top_endpoints: Array<{ endpoint: string; count: number }>
  requests_per_day: Array<{ date: string; requests: number }>
  range: string
}

export interface ApiKey {
  id: string
  name: string
  key_prefix: string
  status: string
  tier: string
  created_at: string
  last_used_at?: string | null
}

export interface ApiKeyCreate {
  id: string
  name: string
  api_key: string
  key_prefix: string
  tier: string
  created_at: string
}

export interface LogEntry {
  id: string
  method: string
  endpoint: string
  status_code: number
  latency_ms: number
  timestamp: string
}

export interface LogsResponse {
  logs: LogEntry[]
  total: number
}

export interface BillingInfo {
  plan: string
  monthly_limit: number
  current_usage: number
  billing_cycle_end: string
  payment_method?: { type: string; last4: string }
}

export interface CheckoutSessionStatus {
  status: string
  plan: string
  payment_status?: string
  api_key?: string | null
}

export interface TeamMember {
  id: string
  email: string
  name: string
  role: string
  avatar_url?: string
  joined_at: string
}

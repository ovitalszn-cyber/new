import { getSupabase } from './supabase'

// Use local proxy to avoid CORS issues
const API_BASE_URL = '/api/proxy'

async function getAuthToken(): Promise<string | null> {
  const supabase = getSupabase()
  if (!supabase) {
    console.error('[API Client] Supabase client not available')
    return null
  }
  
  const { data: { session }, error } = await supabase.auth.getSession()
  
  if (error) {
    console.error('[API Client] Error getting session:', error)
    return null
  }
  
  if (!session) {
    console.warn('[API Client] No active session found')
    return null
  }
  
  console.log('[API Client] Got access token for:', session.user?.email)
  return session.access_token
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken()
  
  if (!token) {
    console.error('[API Client] No auth token - redirecting to login')
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    throw new Error('Please log in to access this feature')
  }

  const url = `${API_BASE_URL}${endpoint}`
  console.log('[API Client] Request:', options.method || 'GET', url)

  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  })

  console.log('[API Client] Response:', response.status, response.statusText)

  if (response.status === 401) {
    console.error('[API Client] 401 Unauthorized - redirecting to login')
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    throw new Error('Session expired. Please log in again.')
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'API request failed' }))
    console.error('[API Client] Error response:', error)
    throw new Error(error.detail || `Request failed: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Profile
  getProfile: () => apiRequest<Profile>('/profile'),
  
  // Usage
  getUsage: () => apiRequest<Usage>('/usage'),
  getUsageSummary: (range: '24h' | '7d' | '30d' = '7d') => 
    apiRequest<UsageSummary>(`/usage/summary?range=${range}`),
  
  // API Keys
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
  
  // Logs
  getLogs: (params?: { limit?: number; offset?: number; status?: string }) => {
    const cleanParams: Record<string, string> = {}
    if (params?.limit !== undefined) cleanParams.limit = String(params.limit)
    if (params?.offset !== undefined) cleanParams.offset = String(params.offset)
    if (params?.status && params.status !== 'undefined') cleanParams.status = params.status
    const query = new URLSearchParams(cleanParams).toString()
    return apiRequest<LogsResponse>(`/logs${query ? `?${query}` : ''}`)
  },
  
  // Billing
  getBilling: () => apiRequest<BillingInfo>('/billing'),
  getBillingHistory: () => apiRequest<{ invoices: any[] }>('/billing/history'),
  
  // Team
  getTeam: () => apiRequest<{ members: TeamMember[] }>('/team'),
  inviteTeamMember: (email: string, role: string = 'member') => 
    apiRequest<{ success: boolean; invite_id: string }>('/team/invite', {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    }),
}

// Type definitions
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

export interface TeamMember {
  id: string
  email: string
  name: string
  role: string
  avatar_url?: string
  joined_at: string
}

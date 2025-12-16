const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';
const DEV_API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.kashrock.com';

// Helper to get current session with logging
export async function getCurrentSession() {
  const { supabase } = await import('./supabase')
  if (!supabase) {
    console.error('[API] Supabase not configured')
    return null
  }
  
  const { data: { session }, error } = await supabase.auth.getSession()
  
  if (error) {
    console.error('[API] Session error:', error)
    return null
  }
  
  if (!session) {
    console.log('[API] No active session found')
    return null
  }
  
  console.log('[API] Session found for:', session.user.email)
  return session
}

// Authenticated API client for developer dashboard
export async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  console.log('[API] Starting request to:', endpoint)
  const { supabase } = await import('./supabase')
  if (!supabase) {
    throw new Error('Supabase not configured')
  }
  const { data: { session }, error } = await supabase.auth.getSession()
  
  console.log('[API] Session check:', {
    hasSession: !!session,
    hasAccessToken: !!session?.access_token,
    userEmail: session?.user?.email,
    error: error?.message
  })
  
  if (!session?.access_token) {
    console.error('[API] No access token found')
    throw new Error('Not authenticated')
  }
  
  const url = `${DEV_API_BASE}${endpoint}`
  console.log('[API] FETCHING FROM:', url)
  
  const response = await fetch(url, {
    ...options,
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
      ...options.headers,
    },
  })
  
  console.log('[API] Response status:', response.status, response.statusText)
  
  if (!response.ok) {
    const errorText = await response.text()
    console.error('[API] Error response:', errorText)
    let errorDetail = 'API request failed'
    try {
      const errorJson = JSON.parse(errorText)
      errorDetail = errorJson.detail || errorJson.message || errorDetail
    } catch {
      errorDetail = errorText || errorDetail
    }
    throw new Error(errorDetail)
  }
  
  return response.json()
}

// API Key Management
export async function createApiKey(name: string) {
  return apiClient<{ key: string; id: string; name: string }>('/v1/dev/api-keys', {
    method: 'POST',
    body: JSON.stringify({ name })
  })
}

export async function listApiKeys() {
  return apiClient<{ keys: Array<{ id: string; name: string; prefix: string; created_at: string; last_used_at: string | null; is_active: boolean }> }>('/v1/dev/api-keys')
}

export async function revokeApiKey(keyId: string) {
  return apiClient(`/v1/dev/api-keys/${keyId}/revoke`, { method: 'POST' })
}

// Usage & Analytics
export async function getUsageSummary(range: '24h' | '7d' | '30d' = '7d') {
  return apiClient<{
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    avg_latency_ms: number;
    requests_by_endpoint: Record<string, number>;
    requests_by_day: Array<{ date: string; count: number }>;
  }>(`/v1/dev/usage/summary?range=${range}`)
}

// Billing
export async function getBillingInfo() {
  return apiClient<{
    plan: string;
    monthly_limit: number;
    current_usage: number;
    billing_cycle_end: string;
    payment_method?: { last4: string; brand: string; exp_month: number; exp_year: number };
  }>('/v1/dev/billing')
}

export async function getBillingHistory() {
  return apiClient<{
    invoices: Array<{ id: string; date: string; amount: number; status: string; pdf_url: string }>;
  }>('/v1/dev/billing/history')
}

// Team Management
export async function getTeamMembers() {
  return apiClient<{
    members: Array<{ id: string; email: string; name: string; role: string; avatar_url?: string; joined_at: string }>;
  }>('/v1/dev/team')
}

export async function inviteTeamMember(email: string, role: 'admin' | 'viewer') {
  return apiClient('/v1/dev/team/invite', {
    method: 'POST',
    body: JSON.stringify({ email, role })
  })
}

// Request Logs
export async function getRequestLogs(params: { limit?: number; offset?: number; status?: 'success' | 'error' } = {}) {
  const searchParams = new URLSearchParams()
  if (params.limit) searchParams.set('limit', params.limit.toString())
  if (params.offset) searchParams.set('offset', params.offset.toString())
  if (params.status) searchParams.set('status', params.status)
  
  return apiClient<{
    logs: Array<{
      id: string;
      method: string;
      endpoint: string;
      status_code: number;
      latency_ms: number;
      timestamp: string;
    }>;
    total: number;
  }>(`/v1/dev/logs?${searchParams.toString()}`)
}

export interface Filters {
  sports: string[];
  numLegs: number;
  minEV: number;
  minTotalEV: number;
  mixedSports: boolean;
  prematch: boolean;
  live: boolean;
}

export async function fetchSlips(filters: Filters) {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`;
  }

  let slips: any[] = [];

  if (filters.mixedSports && filters.sports.length > 1) {
    // Fetch mixed sports slips
    const response = await fetch(
      `${API_BASE_URL}/v4/dabble_slips/mixed?sports=${filters.sports.join(',')}&num_legs=${filters.numLegs}&min_ev_percentage=${filters.minEV}&min_total_ev_percentage=${filters.minTotalEV}&max_results=50`,
      { headers }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch mixed slips: ${response.statusText}`);
    }

    const mixedSlips = await response.json();
    slips.push(...mixedSlips);
  } else {
    // Fetch single-sport slips
    for (const sport of filters.sports) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/v4/sports/${sport}/dabble_slips?num_legs=${filters.numLegs}&min_ev_percentage=${filters.minEV}&min_total_ev_percentage=${filters.minTotalEV}&max_results=20`,
          { headers }
        );

        if (response.ok) {
          const sportSlips = await response.json();
          slips.push(...sportSlips);
        }
      } catch (error) {
        console.error(`Error fetching slips for ${sport}:`, error);
      }
    }
  }

  // Filter by prematch/live if needed
  // Note: This is a simple filter - you might want to enhance this based on commence_time
  if (!filters.prematch && !filters.live) {
    return [];
  }

  // Sort by EV descending
  slips.sort((a, b) => b.total_expected_value_percent - a.total_expected_value_percent);

  return slips;
}





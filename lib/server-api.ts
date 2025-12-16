'use server';

import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

const KASHROCK_API_URL = process.env.KASHROCK_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.kashrock.com';

async function getAccessToken(): Promise<string | null> {
  const cookieStore = await cookies();
  
  try {
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll();
          },
        },
      }
    );
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (e) {
    console.error('[SERVER-API] Failed to get session:', e);
    return null;
  }
}

async function serverFetch<T>(endpoint: string): Promise<T> {
  const accessToken = await getAccessToken();
  
  if (!accessToken) {
    throw new Error('Not authenticated');
  }
  
  console.log('[SERVER-API] Fetching:', `${KASHROCK_API_URL}${endpoint}`);
  
  const response = await fetch(`${KASHROCK_API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  });
  
  console.log('[SERVER-API] Response:', response.status, response.statusText);
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('[SERVER-API] Error:', errorText);
    throw new Error(`Backend error: ${response.status}`);
  }
  
  return response.json();
}

// Usage & Analytics
export async function getUsageSummaryServer(range: '24h' | '7d' | '30d' = '7d') {
  return serverFetch<{
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    avg_latency_ms: number;
    requests_by_endpoint: Record<string, number>;
    requests_by_day: Array<{ date: string; count: number }>;
  }>(`/v1/dev/usage/summary?range=${range}`);
}

// Request Logs
export async function getRequestLogsServer(params: { limit?: number; offset?: number; status?: 'success' | 'error' } = {}) {
  const searchParams = new URLSearchParams();
  if (params.limit) searchParams.set('limit', params.limit.toString());
  if (params.offset) searchParams.set('offset', params.offset.toString());
  if (params.status) searchParams.set('status', params.status);
  
  return serverFetch<{
    logs: Array<{
      id: string;
      method: string;
      endpoint: string;
      status_code: number;
      latency_ms: number;
      timestamp: string;
    }>;
    total: number;
  }>(`/v1/dev/logs?${searchParams.toString()}`);
}

// API Keys
export async function listApiKeysServer() {
  return serverFetch<{
    keys: Array<{
      id: string;
      name: string;
      prefix: string;
      created_at: string;
      last_used_at: string | null;
      is_active: boolean;
    }>;
  }>('/v1/dev/api-keys');
}

// Billing
export async function getBillingInfoServer() {
  return serverFetch<{
    plan: string;
    monthly_limit: number;
    current_usage: number;
    billing_cycle_end: string;
    payment_method?: { last4: string; brand: string; exp_month: number; exp_year: number };
  }>('/v1/dev/billing');
}

export async function getBillingHistoryServer() {
  return serverFetch<{
    invoices: Array<{ id: string; date: string; amount: number; status: string; pdf_url: string }>;
  }>('/v1/dev/billing/history');
}

// Team
export async function getTeamMembersServer() {
  return serverFetch<{
    members: Array<{
      id: string;
      email: string;
      name: string;
      role: string;
      avatar_url?: string;
      joined_at: string;
    }>;
  }>('/v1/dev/team');
}

// API Key mutations (server actions)
export async function createApiKeyServer(name: string) {
  const accessToken = await getAccessToken();
  
  if (!accessToken) {
    throw new Error('Not authenticated');
  }
  
  console.log('[SERVER-API] Creating API key:', name);
  
  const response = await fetch(`${KASHROCK_API_URL}/v1/dev/api-keys`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ name }),
    cache: 'no-store',
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('[SERVER-API] Create key error:', errorText);
    throw new Error(`Failed to create key: ${response.status}`);
  }
  
  return response.json() as Promise<{ key: string; id: string; name: string }>;
}

export async function revokeApiKeyServer(keyId: string) {
  const accessToken = await getAccessToken();
  
  if (!accessToken) {
    throw new Error('Not authenticated');
  }
  
  console.log('[SERVER-API] Revoking API key:', keyId);
  
  const response = await fetch(`${KASHROCK_API_URL}/v1/dev/api-keys/${keyId}/revoke`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('[SERVER-API] Revoke key error:', errorText);
    throw new Error(`Failed to revoke key: ${response.status}`);
  }
  
  return response.json();
}

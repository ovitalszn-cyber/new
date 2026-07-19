import type { SessionUser } from './auth/types'

export type Profile = SessionUser

export interface Usage {
  plan: string
  requests_today: number
  requests_this_month: number
  current_rpm: number
  monthly_remaining: number
  limit_per_min: number
  limit_month: number
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

export interface ApiKeyCreate extends ApiKey {
  api_key: string
}

export interface LogEntry {
  id: string
  method: string
  endpoint: string
  status_code: number
  latency_ms?: number | null
  timestamp: string
}

export interface BillingInfo {
  plan: string
  monthly_limit: number
  current_usage: number
  billing_cycle_end?: string | null
  payment_method?: { type?: string; last4?: string } | null
}

export interface CheckoutSessionStatus {
  status: string
  plan: string
  payment_status?: string | null
  api_key?: string | null
}

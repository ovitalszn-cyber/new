export interface SessionUser {
  id: string
  email: string
  full_name?: string | null
  avatar_url?: string | null
  tier: string
  created_at?: string | null
}

export interface BackendSession {
  access_token: string
  refresh_token: string
  expires_at: number
  user: SessionUser
  initial_api_key?: string | null
}

export interface OAuthTransaction {
  state: string
  nonce: string
  verifier: string
  returnTo: string
}

export interface StoredSessionTokens {
  accessToken: string
  refreshToken: string | null
  expiresAt?: number | null
  userEmail?: string | null
}

const STORAGE_KEY = 'kr:auth:session'

const isBrowser = () => typeof window !== 'undefined'

export const saveSessionTokens = (session: {
  access_token: string
  refresh_token: string | null
  expires_at?: number | null
  user?: { email?: string | null }
}) => {
  if (!isBrowser()) return
  const payload: StoredSessionTokens = {
    accessToken: session.access_token,
    refreshToken: session.refresh_token,
    expiresAt: session.expires_at ?? null,
    userEmail: session.user?.email ?? null,
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
}

export const loadSessionTokens = (): StoredSessionTokens | null => {
  if (!isBrowser()) return null
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as StoredSessionTokens
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export const clearSessionTokens = () => {
  if (!isBrowser()) return
  localStorage.removeItem(STORAGE_KEY)
}

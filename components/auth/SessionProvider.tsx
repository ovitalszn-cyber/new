'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'

import type { SessionUser } from '@/lib/auth/types'

type SessionStatus = 'loading' | 'authenticated' | 'unauthenticated'

interface SessionContextValue {
  status: SessionStatus
  user: SessionUser | null
  refresh: () => Promise<void>
  logout: () => Promise<void>
}

const SessionContext = createContext<SessionContextValue | null>(null)

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<SessionStatus>('loading')
  const [user, setUser] = useState<SessionUser | null>(null)
  const inflight = useRef<Promise<void> | null>(null)

  const refresh = useCallback(async () => {
    if (inflight.current) return inflight.current
    inflight.current = (async () => {
      try {
        const response = await fetch('/api/auth/session', {
          credentials: 'include',
          cache: 'no-store',
        })
        if (!response.ok) {
          setUser(null)
          setStatus('unauthenticated')
          return
        }
        const data = (await response.json()) as { user: SessionUser }
        setUser(data.user)
        setStatus('authenticated')
      } catch {
        setUser(null)
        setStatus('unauthenticated')
      } finally {
        inflight.current = null
      }
    })()
    return inflight.current
  }, [])

  const logout = useCallback(async () => {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    }).catch(() => undefined)
    setUser(null)
    setStatus('unauthenticated')
    window.location.assign('/')
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => void refresh(), 0)
    return () => clearTimeout(timer)
  }, [refresh])

  const value = useMemo(
    () => ({ status, user, refresh, logout }),
    [logout, refresh, status, user],
  )

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  )
}

export function useSession() {
  const value = useContext(SessionContext)
  if (!value) {
    throw new Error('useSession must be used within SessionProvider')
  }
  return value
}

import { NextRequest } from 'next/server'

import { ACCESS_COOKIE, REFRESH_COOKIE } from './cookies'
import { backendUrl } from './config'
import type { BackendSession } from './types'

interface AuthenticatedResult {
  response: Response
  refreshedSession?: BackendSession
}

async function readError(response: Response, fallback: string) {
  const body = (await response.json().catch(() => null)) as {
    detail?: string
  } | null
  return body?.detail ?? fallback
}

export async function exchangeBackendSession(idToken: string) {
  const response = await fetch(backendUrl('/auth/session'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken }),
    cache: 'no-store',
  })
  if (!response.ok) {
    throw new Error(await readError(response, 'KashRock sign-in failed'))
  }
  return (await response.json()) as BackendSession
}

export async function refreshBackendSession(refreshToken: string) {
  const response = await fetch(backendUrl('/auth/refresh'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: 'no-store',
  })
  if (!response.ok) return null
  return (await response.json()) as BackendSession
}

function withBearer(init: RequestInit, accessToken: string) {
  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${accessToken}`)
  return { ...init, headers, cache: 'no-store' as const }
}

export async function authenticatedBackendFetch(
  request: NextRequest,
  path: string,
  init: RequestInit = {},
): Promise<AuthenticatedResult> {
  const accessToken = request.cookies.get(ACCESS_COOKIE)?.value
  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value
  let refreshedSession: BackendSession | undefined
  let activeToken = accessToken

  if (!activeToken && refreshToken) {
    refreshedSession = (await refreshBackendSession(refreshToken)) ?? undefined
    activeToken = refreshedSession?.access_token
  }
  if (!activeToken) {
    return { response: new Response(null, { status: 401 }) }
  }

  let response = await fetch(backendUrl(path), withBearer(init, activeToken))
  if (response.status === 401 && refreshToken && !refreshedSession) {
    refreshedSession = (await refreshBackendSession(refreshToken)) ?? undefined
    if (refreshedSession) {
      response = await fetch(
        backendUrl(path),
        withBearer(init, refreshedSession.access_token),
      )
    }
  }
  return { response, refreshedSession }
}

export async function revokeBackendSession(refreshToken?: string) {
  if (!refreshToken) return
  await fetch(backendUrl('/auth/logout'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: 'no-store',
  }).catch(() => undefined)
}

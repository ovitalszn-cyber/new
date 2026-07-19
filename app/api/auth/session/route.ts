import { NextRequest, NextResponse } from 'next/server'

import { authenticatedBackendFetch } from '@/lib/auth/backend'
import {
  clearSessionCookies,
  setSessionCookies,
} from '@/lib/auth/cookies'
import type { SessionUser } from '@/lib/auth/types'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  const result = await authenticatedBackendFetch(request, '/profile')
  if (!result.response.ok) {
    const response = NextResponse.json(
      { authenticated: false, user: null },
      { status: result.response.status === 401 ? 401 : 502 },
    )
    if (result.response.status === 401) clearSessionCookies(response)
    return response
  }

  const user = (await result.response.json()) as SessionUser
  const response = NextResponse.json(
    { authenticated: true, user },
    { headers: { 'Cache-Control': 'no-store' } },
  )
  if (result.refreshedSession) {
    setSessionCookies(response, result.refreshedSession)
  }
  return response
}

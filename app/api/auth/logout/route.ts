import { NextRequest, NextResponse } from 'next/server'

import { revokeBackendSession } from '@/lib/auth/backend'
import {
  clearSessionCookies,
  REFRESH_COOKIE,
} from '@/lib/auth/cookies'

export const runtime = 'nodejs'

export async function POST(request: NextRequest) {
  const refreshToken = request.cookies.get(REFRESH_COOKIE)?.value
  await revokeBackendSession(refreshToken)
  const response = NextResponse.json({ success: true })
  clearSessionCookies(response)
  return response
}

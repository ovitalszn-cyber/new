import { NextRequest, NextResponse } from 'next/server'

import type { BackendSession, OAuthTransaction } from './types'

export const ACCESS_COOKIE = 'kr_access'
export const REFRESH_COOKIE = 'kr_refresh'
export const OAUTH_COOKIE = 'kr_oauth'

const secure = process.env.NODE_ENV === 'production'
const baseOptions = {
  httpOnly: true,
  secure,
  sameSite: 'lax' as const,
  path: '/',
}

function encode(value: object) {
  return Buffer.from(JSON.stringify(value)).toString('base64url')
}

function decode<T>(value?: string): T | null {
  if (!value) return null
  try {
    return JSON.parse(Buffer.from(value, 'base64url').toString()) as T
  } catch {
    return null
  }
}

export function setOAuthCookie(
  response: NextResponse,
  transaction: OAuthTransaction,
) {
  response.cookies.set(OAUTH_COOKIE, encode(transaction), {
    ...baseOptions,
    maxAge: 10 * 60,
  })
}

export function readOAuthCookie(request: NextRequest) {
  return decode<OAuthTransaction>(request.cookies.get(OAUTH_COOKIE)?.value)
}

export function clearOAuthCookie(response: NextResponse) {
  response.cookies.set(OAUTH_COOKIE, '', { ...baseOptions, maxAge: 0 })
}

export function setSessionCookies(
  response: NextResponse,
  session: BackendSession,
) {
  const accessMaxAge = Math.max(session.expires_at - Math.floor(Date.now() / 1000), 60)
  response.cookies.set(ACCESS_COOKIE, session.access_token, {
    ...baseOptions,
    maxAge: accessMaxAge,
  })
  response.cookies.set(REFRESH_COOKIE, session.refresh_token, {
    ...baseOptions,
    maxAge: 30 * 24 * 60 * 60,
  })
}

export function clearSessionCookies(response: NextResponse) {
  // Must mirror set options or browsers keep the Secure cookies.
  response.cookies.set(ACCESS_COOKIE, '', { ...baseOptions, maxAge: 0 })
  response.cookies.set(REFRESH_COOKIE, '', { ...baseOptions, maxAge: 0 })
}

import { NextRequest, NextResponse } from 'next/server'

import { getRequestOrigin } from '@/lib/auth/config'
import { setOAuthCookie } from '@/lib/auth/cookies'
import {
  buildGoogleAuthorizationUrl,
  createOAuthValues,
} from '@/lib/auth/google'
import { safeReturnTo } from '@/lib/auth/navigation'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  try {
    const values = createOAuthValues()
    const returnTo = safeReturnTo(request.nextUrl.searchParams.get('returnTo'))
    const redirectUri = `${getRequestOrigin(request.url)}/api/auth/callback`
    const authorizationUrl = buildGoogleAuthorizationUrl(redirectUri, values)
    const response = NextResponse.redirect(authorizationUrl)
    setOAuthCookie(response, {
      state: values.state,
      nonce: values.nonce,
      verifier: values.verifier,
      returnTo,
    })
    return response
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Unable to start Google sign-in'
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(message)}`, request.url),
    )
  }
}

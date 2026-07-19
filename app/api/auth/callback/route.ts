import { NextRequest, NextResponse } from 'next/server'

import { exchangeBackendSession } from '@/lib/auth/backend'
import { getRequestOrigin } from '@/lib/auth/config'
import {
  clearOAuthCookie,
  readOAuthCookie,
  setSessionCookies,
} from '@/lib/auth/cookies'
import {
  exchangeGoogleCode,
  secureEqual,
  validateGoogleIdToken,
} from '@/lib/auth/google'
import { createKeyDeliveryHtml } from '@/lib/auth/key-delivery'

export const runtime = 'nodejs'

function failureResponse(request: NextRequest, message: string) {
  const url = new URL('/login', request.url)
  url.searchParams.set('error', message)
  const response = NextResponse.redirect(url)
  clearOAuthCookie(response)
  return response
}

function successResponse(
  request: NextRequest,
  returnTo: string,
  initialApiKey?: string | null,
) {
  if (initialApiKey && !returnTo.startsWith('/checkout/start')) {
    const delivery = createKeyDeliveryHtml(initialApiKey, returnTo)
    return new NextResponse(delivery.html, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-store',
        'Content-Security-Policy': `default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${delivery.nonce}'; connect-src 'self'`,
      },
    })
  }
  return NextResponse.redirect(
    new URL(returnTo, getRequestOrigin(request.url)),
  )
}

export async function GET(request: NextRequest) {
  const transaction = readOAuthCookie(request)
  const code = request.nextUrl.searchParams.get('code')
  const state = request.nextUrl.searchParams.get('state')
  const googleError = request.nextUrl.searchParams.get('error')

  if (googleError) return failureResponse(request, 'Google sign-in was cancelled')
  if (!transaction || !code || !state || !secureEqual(state, transaction.state)) {
    return failureResponse(request, 'The sign-in request expired. Please try again.')
  }

  try {
    const redirectUri = `${getRequestOrigin(request.url)}/api/auth/callback`
    const idToken = await exchangeGoogleCode(
      code,
      transaction.verifier,
      redirectUri,
    )
    await validateGoogleIdToken(idToken, transaction.nonce)
    const session = await exchangeBackendSession(idToken)
    const response = successResponse(
      request,
      transaction.returnTo,
      session.initial_api_key,
    )
    setSessionCookies(response, session)
    clearOAuthCookie(response)
    return response
  } catch (error) {
    console.error('[auth/callback] Sign-in failed', error)
    return failureResponse(request, 'Unable to complete sign-in. Please try again.')
  }
}

import { NextRequest, NextResponse } from 'next/server'

import { ACCESS_COOKIE, REFRESH_COOKIE } from '@/lib/auth/cookies'
import { MAINTENANCE_MODE } from '@/lib/maintenance'

function isStaticPath(pathname: string) {
  return (
    pathname.startsWith('/_next') ||
    pathname === '/favicon.ico' ||
    pathname.startsWith('/icon') ||
    /\.[a-zA-Z0-9]+$/.test(pathname)
  )
}

function maintenanceResponse(request: NextRequest) {
  const { pathname } = request.nextUrl
  if (isStaticPath(pathname)) return NextResponse.next()
  if (pathname.startsWith('/api/')) {
    if (pathname === '/api/waitlist' && request.method === 'POST') {
      return NextResponse.next()
    }
    return NextResponse.json(
      { detail: 'Site is under maintenance. Please try again later.' },
      { status: 503 },
    )
  }
  if (pathname === '/') return NextResponse.next()
  return NextResponse.redirect(new URL('/', request.url))
}

function isProtected(pathname: string) {
  return ['/console', '/settings', '/checkout'].some(
    (path) => pathname === path || pathname.startsWith(`${path}/`),
  )
}

function checkoutReturn(request: NextRequest) {
  const { searchParams } = request.nextUrl
  if (
    request.nextUrl.pathname !== '/console' ||
    searchParams.get('checkout') !== 'success' ||
    !searchParams.get('session_id')
  ) {
    return null
  }
  const url = new URL('/checkout/return', request.url)
  url.searchParams.set('session_id', searchParams.get('session_id')!)
  return NextResponse.redirect(url)
}

export function proxy(request: NextRequest) {
  if (MAINTENANCE_MODE) return maintenanceResponse(request)
  const returnRedirect = checkoutReturn(request)
  if (returnRedirect) return returnRedirect

  if (isProtected(request.nextUrl.pathname)) {
    const hasSession =
      request.cookies.has(ACCESS_COOKIE) || request.cookies.has(REFRESH_COOKIE)
    if (!hasSession) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set(
        'returnTo',
        `${request.nextUrl.pathname}${request.nextUrl.search}`,
      )
      return NextResponse.redirect(loginUrl)
    }
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image).*)'],
}

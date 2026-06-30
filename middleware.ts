import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

import { MAINTENANCE_MODE } from '@/lib/maintenance';

export function middleware(request: NextRequest) {
  if (!MAINTENANCE_MODE) {
    return NextResponse.next();
  }

  const { pathname } = request.nextUrl;

  if (
    pathname.startsWith('/_next') ||
    pathname === '/favicon.ico' ||
    pathname.startsWith('/icon') ||
    /\.[a-zA-Z0-9]+$/.test(pathname)
  ) {
    return NextResponse.next();
  }

  if (pathname.startsWith('/api/')) {
    if (pathname === '/api/waitlist' && request.method === 'POST') {
      return NextResponse.next();
    }

    return NextResponse.json(
      { detail: 'Site is under maintenance. Please try again later.' },
      { status: 503 },
    );
  }

  if (pathname !== '/') {
    const url = request.nextUrl.clone();
    url.pathname = '/';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image).*)'],
};

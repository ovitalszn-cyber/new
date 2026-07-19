import { NextRequest, NextResponse } from 'next/server'

import { authenticatedBackendFetch } from '@/lib/auth/backend'
import {
  clearSessionCookies,
  setSessionCookies,
} from '@/lib/auth/cookies'

type RouteContext = { params: Promise<{ path: string[] }> }

function requestHeaders(request: NextRequest) {
  const headers = new Headers()
  const contentType = request.headers.get('content-type')
  const accept = request.headers.get('accept')
  if (contentType) headers.set('Content-Type', contentType)
  if (accept) headers.set('Accept', accept)
  return headers
}

async function handleProxy(
  request: NextRequest,
  context: RouteContext,
  method: string,
) {
  const { path } = await context.params
  const safePath = path.map(encodeURIComponent).join('/')
  const body =
    method === 'GET' || method === 'HEAD'
      ? undefined
      : await request.arrayBuffer()
  const result = await authenticatedBackendFetch(
    request,
    `/${safePath}${request.nextUrl.search}`,
    { method, headers: requestHeaders(request), body },
  )
  const response = new NextResponse(result.response.body, {
    status: result.response.status,
    statusText: result.response.statusText,
    headers: {
      'Content-Type':
        result.response.headers.get('content-type') ?? 'application/json',
      'Cache-Control': 'no-store',
    },
  })
  if (result.refreshedSession) {
    setSessionCookies(response, result.refreshedSession)
  } else if (result.response.status === 401) {
    clearSessionCookies(response)
  }
  return response
}

export function GET(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context, 'GET')
}

export function POST(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context, 'POST')
}

export function PUT(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context, 'PUT')
}

export function PATCH(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context, 'PATCH')
}

export function DELETE(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context, 'DELETE')
}

import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.kashrock.com'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return handleProxy(request, await params, 'GET')
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return handleProxy(request, await params, 'POST')
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return handleProxy(request, await params, 'PUT')
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return handleProxy(request, await params, 'DELETE')
}

async function handleProxy(
  request: NextRequest,
  params: { path: string[] },
  method: string
) {
  const path = params.path.join('/')
  const url = `${BACKEND_URL}/v1/dev/${path}${request.nextUrl.search}`
  
  // Get authorization header from request
  const authHeader = request.headers.get('authorization')
  
  console.log(`[Proxy] ${method} ${url}`)
  console.log(`[Proxy] Auth header present: ${!!authHeader}`)

  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    
    if (authHeader) {
      headers['Authorization'] = authHeader
    }

    const fetchOptions: RequestInit = {
      method,
      headers,
    }

    // Add body for POST/PUT requests
    if (method === 'POST' || method === 'PUT') {
      try {
        const body = await request.json()
        fetchOptions.body = JSON.stringify(body)
      } catch {
        // No body or invalid JSON
      }
    }

    const response = await fetch(url, fetchOptions)
    
    console.log(`[Proxy] Response: ${response.status} ${response.statusText}`)

    const contentType = response.headers.get('content-type') || ''
    let data: any = null

    if (contentType.includes('application/json')) {
      data = await response.json().catch(() => null)
    } else {
      const text = await response.text().catch(() => '')
      data = text ? { detail: text } : { detail: response.statusText }
    }

    if (data == null) {
      data = { detail: response.statusText }
    }

    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('[Proxy] Error:', error)
    return NextResponse.json(
      { detail: 'Proxy request failed' },
      { status: 500 }
    )
  }
}

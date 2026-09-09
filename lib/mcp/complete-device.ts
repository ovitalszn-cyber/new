import { cookies } from 'next/headers'

import { refreshBackendSession } from '@/lib/auth/backend'
import { backendUrl } from '@/lib/auth/config'
import { ACCESS_COOKIE, REFRESH_COOKIE } from '@/lib/auth/cookies'

export type CompleteResult =
  | { ok: true; email?: string }
  | { ok: false; needsLogin: true }
  | { ok: false; error: string }

export async function completeMcpDevice(deviceCode: string): Promise<CompleteResult> {
  const jar = await cookies()
  let access = jar.get(ACCESS_COOKIE)?.value
  const refresh = jar.get(REFRESH_COOKIE)?.value

  async function post(token: string) {
    return fetch(backendUrl('/mcp/device/complete'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ device_code: deviceCode }),
      cache: 'no-store',
    })
  }

  if (!access && refresh) {
    const session = await refreshBackendSession(refresh)
    access = session?.access_token
  }
  if (!access) return { ok: false, needsLogin: true }

  let response = await post(access)
  if (response.status === 401 && refresh) {
    const session = await refreshBackendSession(refresh)
    if (session?.access_token) {
      access = session.access_token
      response = await post(access)
    }
  }
  if (response.status === 401) return { ok: false, needsLogin: true }
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null
    return { ok: false, error: body?.detail ?? 'Could not finish sign-in' }
  }
  const data = (await response.json()) as { email?: string }
  return { ok: true, email: data.email }
}

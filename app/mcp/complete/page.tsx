import type { ReactNode } from 'react'
import { redirect } from 'next/navigation'

import { completeMcpDevice } from '@/lib/mcp/complete-device'

interface PageProps {
  searchParams: Promise<{ device?: string }>
}

const DEVICE_RE = /^[A-Za-z0-9_-]{16,128}$/

export default async function McpCompletePage({ searchParams }: PageProps) {
  const params = await searchParams
  const device = params.device ?? ''
  if (!DEVICE_RE.test(device)) {
    return (
      <Shell>
        <h1 className="text-3xl font-medium text-white mb-2">Sign-in link expired</h1>
        <p className="text-zinc-400">Ask the agent to log in again.</p>
      </Shell>
    )
  }

  const result = await completeMcpDevice(device)
  if ('needsLogin' in result && result.needsLogin) {
    const returnTo = `/mcp/complete?device=${encodeURIComponent(device)}`
    redirect(`/login?returnTo=${encodeURIComponent(returnTo)}`)
  }
  if (!result.ok) {
    const message = 'error' in result ? result.error : 'Could not finish sign-in'
    return (
      <Shell>
        <h1 className="text-3xl font-medium text-white mb-2">Could not finish sign-in</h1>
        <p className="text-zinc-400">{message}</p>
      </Shell>
    )
  }

  return (
    <Shell>
      <h1 className="text-3xl font-medium text-white mb-2">You&apos;re in</h1>
      <p className="text-zinc-400">
        {result.email ? `${result.email} is connected.` : 'KashRock is connected.'} Go back to your
        editor — the agent has the key.
      </p>
    </Shell>
  )
}

function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#08090A] flex items-center justify-center">
      <div className="w-full max-w-md p-8 text-center">{children}</div>
    </div>
  )
}

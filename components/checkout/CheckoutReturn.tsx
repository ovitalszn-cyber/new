'use client'

import Link from 'next/link'
import { useState } from 'react'

import { useCheckoutReconciliation } from './useCheckoutReconciliation'

export default function CheckoutReturn({ sessionId }: { sessionId: string }) {
  const state = useCheckoutReconciliation(sessionId)
  const [copied, setCopied] = useState(false)

  const copyKey = async () => {
    if (!state.apiKey) return
    await navigator.clipboard.writeText(state.apiKey)
    setCopied(true)
  }

  return (
    <main className="min-h-screen bg-[#08090A] text-white grid place-items-center p-6">
      <section className="w-full max-w-2xl rounded-lg border border-white/10 bg-[#0C0D0F] p-8">
        <p className="text-xs uppercase tracking-widest text-zinc-500">
          Checkout return
        </p>
        <h1 className="mt-2 text-2xl font-semibold">
          {state.phase === 'delivered'
            ? 'Setup complete'
            : 'Finishing your account'}
        </h1>
        <p
          className={`mt-3 ${
            state.phase === 'terminal' ? 'text-red-300' : 'text-zinc-400'
          }`}
          role="status"
        >
          {state.message}
        </p>

        {state.phase === 'reconciling' || state.phase === 'retrying' ? (
          <div className="mt-6 h-1 overflow-hidden rounded bg-white/10">
            <div className="h-full w-1/3 animate-pulse rounded bg-emerald-400" />
          </div>
        ) : null}

        {state.apiKey ? (
          <div className="mt-6">
            <p className="text-sm text-emerald-300">
              Copy this key now. It will not be shown again.
            </p>
            <div className="mt-2 flex items-center gap-3 rounded border border-emerald-500/30 bg-black/50 p-4">
              <code className="min-w-0 flex-1 break-all text-emerald-200">
                {state.apiKey}
              </code>
              <button
                type="button"
                onClick={() => void copyKey()}
                className="rounded bg-white px-3 py-2 font-medium text-black"
              >
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
            <Link
              href="/console"
              className="mt-6 inline-block rounded border border-white/20 px-4 py-2"
            >
              Open console
            </Link>
          </div>
        ) : null}

        {state.phase === 'terminal' ? (
          <Link
            href="/#pricing"
            className="mt-6 inline-block rounded bg-white px-4 py-2 font-medium text-black"
          >
            Return to pricing
          </Link>
        ) : null}
      </section>
    </main>
  )
}

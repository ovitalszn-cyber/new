'use client'

import Link from 'next/link'
import { useCallback, useEffect, useRef, useState } from 'react'

import { api } from '@/lib/api-client'

export default function CheckoutStart({ plan }: { plan: string | null }) {
  const started = useRef(false)
  const [error, setError] = useState<string | null>(
    plan ? null : 'Choose a valid paid plan to continue.',
  )

  const beginCheckout = useCallback(async () => {
    if (!plan) return
    setError(null)
    try {
      const checkout = await api.createCheckoutSession(plan)
      window.location.assign(checkout.url)
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : 'Unable to start checkout.',
      )
    }
  }, [plan])

  useEffect(() => {
    if (started.current || !plan) return
    started.current = true
    void beginCheckout()
  }, [beginCheckout, plan])

  return (
    <main className="min-h-screen bg-[#08090A] text-white grid place-items-center p-6">
      <section className="w-full max-w-lg rounded-lg border border-white/10 bg-white/5 p-8">
        <h1 className="text-2xl font-semibold">Preparing secure checkout</h1>
        {error ? (
          <>
            <p className="mt-3 text-red-300" role="alert">
              {error}
            </p>
            <div className="mt-6 flex gap-3">
              {plan ? (
                <button
                  type="button"
                  onClick={() => void beginCheckout()}
                  className="rounded bg-white px-4 py-2 font-medium text-black"
                >
                  Try again
                </button>
              ) : null}
              <Link href="/#pricing" className="rounded border border-white/20 px-4 py-2">
                View plans
              </Link>
            </div>
          </>
        ) : (
          <p className="mt-3 text-zinc-400">
            You will be redirected to Stripe in a moment.
          </p>
        )}
      </section>
    </main>
  )
}

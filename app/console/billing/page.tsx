"use client"

import Link from "next/link"
import { useCallback, useEffect, useState } from "react"

import { useSession } from "@/components/auth/SessionProvider"
import {
  api,
  type BillingInfo,
  type CancelSubscriptionResult,
} from "@/lib/api-client"

export default function ConsoleBillingPage() {
  const { user } = useSession()
  const [billing, setBilling] = useState<BillingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [confirming, setConfirming] = useState(false)
  const [working, setWorking] = useState(false)
  const [result, setResult] = useState<CancelSubscriptionResult | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setBilling(await api.getBilling())
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load billing")
      setBilling(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const onCancel = async () => {
    setWorking(true)
    setError(null)
    try {
      const canceled = await api.cancelSubscription()
      setResult(canceled)
      setConfirming(false)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cancel failed")
    } finally {
      setWorking(false)
    }
  }

  const periodEnd = formatDate(
    result?.current_period_end || billing?.billing_cycle_end,
  )
  const alreadyEnding =
    Boolean(billing?.cancel_at_period_end) || Boolean(result?.cancel_at_period_end)

  return (
    <>
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8">
        <p className="text-sm text-zinc-400">
          {user?.full_name || user?.email || "Account"}
        </p>
        <Link href="/pricing" className="text-sm text-zinc-300 hover:text-white">
          Upgrade plan
        </Link>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-3xl space-y-6">
          <div>
            <Link href="/console" className="text-sm text-zinc-500 hover:text-white">
              ← Overview
            </Link>
            <h1 className="mt-4 text-2xl font-semibold text-white">Billing</h1>
            <p className="mt-1 text-sm text-zinc-500">
              Manage your plan. Cancel anytime — access stays through the current
              billing period.
            </p>
          </div>

          {loading ? <p className="text-zinc-400">Loading billing…</p> : null}
          {error ? (
            <p className="rounded border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
              {error}
            </p>
          ) : null}

          {billing ? (
            <section className="rounded border border-white/10 bg-[#0C0D0F] p-6">
              <h2 className="text-sm font-medium text-white">Current plan</h2>
              <dl className="mt-5 grid gap-5 sm:grid-cols-2">
                <Detail label="Plan" value={billing.plan} />
                <Detail
                  label="Status"
                  value={
                    alreadyEnding
                      ? "Cancels at period end"
                      : billing.subscription_status || "Active"
                  }
                />
                <Detail
                  label="Usage this cycle"
                  value={`${billing.current_usage.toLocaleString()} / ${billing.monthly_limit.toLocaleString()}`}
                />
                <Detail label="Access through" value={periodEnd} />
              </dl>
            </section>
          ) : null}

          {alreadyEnding ? (
            <section className="rounded border border-white/10 bg-[#0C0D0F] p-6">
              <h2 className="text-sm font-medium text-white">Cancellation scheduled</h2>
              <p className="mt-3 text-sm text-zinc-400">
                Your plan stays active until <span className="text-zinc-200">{periodEnd}</span>.
                After that you move to the free tier. No further charges.
              </p>
            </section>
          ) : null}

          {billing?.can_cancel && !alreadyEnding ? (
            <section className="rounded border border-red-500/20 bg-[#0C0D0F] p-6">
              <h2 className="text-sm font-medium text-white">Cancel subscription</h2>
              <p className="mt-3 text-sm text-zinc-400">
                Stops auto-renewal. You keep full access until {periodEnd}. Monthly
                payments already made are not refunded.
              </p>

              {!confirming ? (
                <button
                  type="button"
                  onClick={() => setConfirming(true)}
                  className="mt-5 rounded border border-red-500/40 px-4 py-2 text-sm text-red-300 hover:bg-red-500/10"
                >
                  Cancel subscription
                </button>
              ) : (
                <div className="mt-5 space-y-4 rounded border border-red-500/30 bg-red-500/5 p-4">
                  <p className="text-sm text-red-200">
                    Confirm cancel? Renewal stops; access continues until {periodEnd}.
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      disabled={working}
                      onClick={() => void onCancel()}
                      className="rounded bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-400 disabled:opacity-50"
                    >
                      {working ? "Canceling…" : "Yes, cancel at period end"}
                    </button>
                    <button
                      type="button"
                      disabled={working}
                      onClick={() => setConfirming(false)}
                      className="rounded border border-white/15 px-4 py-2 text-sm text-zinc-300 hover:bg-white/5"
                    >
                      Keep plan
                    </button>
                  </div>
                </div>
              )}
            </section>
          ) : null}

          {!loading && billing && !billing.can_cancel && !alreadyEnding ? (
            <section className="rounded border border-white/10 bg-[#0C0D0F] p-6">
              <h2 className="text-sm font-medium text-white">No paid renewal</h2>
              <p className="mt-3 text-sm text-zinc-400">
                This account is not on a cancelable paid subscription.
              </p>
              <Link
                href="/pricing"
                className="mt-4 inline-block text-sm text-zinc-300 underline hover:text-white"
              >
                View plans
              </Link>
            </section>
          ) : null}
        </div>
      </div>
    </>
  )
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-sm text-zinc-500">{label}</dt>
      <dd className="mt-1 break-words text-zinc-200">{value}</dd>
    </div>
  )
}

function formatDate(value?: string | null) {
  if (!value) return "Not available"
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? "Not available"
    : date.toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
}

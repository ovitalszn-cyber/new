'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

import { useSession } from '@/components/auth/SessionProvider'
import {
  api,
  type BillingInfo,
  type Profile,
} from '@/lib/api-client'

export default function SettingsPage() {
  const { logout } = useSession()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [billing, setBilling] = useState<BillingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [unavailable, setUnavailable] = useState<string[]>([])

  useEffect(() => {
    const load = async () => {
      const [profileResult, billingResult] = await Promise.allSettled([
        api.getProfile(),
        api.getBilling(),
      ])
      if (profileResult.status === 'fulfilled') setProfile(profileResult.value)
      if (billingResult.status === 'fulfilled') setBilling(billingResult.value)
      setUnavailable([
        ...(profileResult.status === 'rejected' ? ['Profile'] : []),
        ...(billingResult.status === 'rejected' ? ['Billing'] : []),
      ])
      setLoading(false)
    }
    void load()
  }, [])

  return (
    <main className="min-h-screen bg-[#08090A] px-6 py-12 text-white">
      <div className="mx-auto max-w-3xl">
        <Link href="/console" className="text-sm text-zinc-400 hover:text-white">
          ← Back to console
        </Link>
        <h1 className="mt-6 text-3xl font-semibold">Account settings</h1>
        <p className="mt-2 text-zinc-500">
          Live account and billing details. Editable preferences are not currently
          available.
        </p>

        {loading ? <p className="mt-8 text-zinc-400">Loading account…</p> : null}
        {unavailable.length ? (
          <p className="mt-6 rounded border border-amber-500/30 p-4 text-amber-200">
            {unavailable.join(' and ')} data is temporarily unavailable.
          </p>
        ) : null}

        {profile ? (
          <section className="mt-8 rounded border border-white/10 bg-[#0C0D0F] p-6">
            <h2 className="font-medium">Profile</h2>
            <dl className="mt-5 grid gap-5 sm:grid-cols-2">
              <Detail label="Name" value={profile.full_name || 'Not provided'} />
              <Detail label="Email" value={profile.email} />
              <Detail label="Account created" value={formatDate(profile.created_at)} />
            </dl>
          </section>
        ) : null}

        {billing ? (
          <section className="mt-6 rounded border border-white/10 bg-[#0C0D0F] p-6">
            <h2 className="font-medium">Billing</h2>
            <dl className="mt-5 grid gap-5 sm:grid-cols-2">
              <Detail label="Plan" value={billing.plan} />
              <Detail
                label="Monthly usage"
                value={`${billing.current_usage.toLocaleString()} / ${billing.monthly_limit.toLocaleString()}`}
              />
              <Detail
                label="Billing cycle ends"
                value={formatDate(billing.billing_cycle_end)}
              />
              <Detail
                label="Payment method"
                value={
                  billing.payment_method?.last4
                    ? `Ending in ${billing.payment_method.last4}`
                    : 'Not available'
                }
              />
            </dl>
          </section>
        ) : null}

        <button
          type="button"
          onClick={() => void logout()}
          className="mt-8 rounded border border-red-500/30 px-4 py-2 text-red-300"
        >
          Sign out
        </button>
      </div>
    </main>
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
  if (!value) return 'Not available'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? 'Not available'
    : date.toLocaleDateString()
}

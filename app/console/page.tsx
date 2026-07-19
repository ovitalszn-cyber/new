'use client'

import Link from 'next/link'

import { useSession } from '@/components/auth/SessionProvider'
import ApiKeyPanel from '@/components/console/ApiKeyPanel'
import { useConsoleData } from '@/components/console/useConsoleData'

function Metric({
  label,
  value,
}: {
  label: string
  value: string | null
}) {
  return (
    <div className="rounded border border-white/10 bg-[#0C0D0F] p-5">
      <p className="text-sm text-zinc-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">
        {value ?? 'Unavailable'}
      </p>
    </div>
  )
}

export default function ConsolePage() {
  const { user } = useSession()
  const { data, error, loading, refresh } = useConsoleData()
  const successRate =
    data.summary && data.summary.total_requests > 0
      ? `${(
          ((data.summary.total_requests - data.summary.error_count) /
            data.summary.total_requests) *
          100
        ).toFixed(2)}%`
      : data.summary
        ? 'No requests yet'
        : null

  return (
    <>
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8">
        <p className="text-sm text-zinc-400">
          {user?.full_name || user?.email || 'Account'}
        </p>
        <Link href="/#pricing" className="text-sm text-zinc-300 hover:text-white">
          Upgrade plan
        </Link>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-6xl space-y-6">
          <div>
            <h1 className="text-2xl font-semibold text-white">Overview</h1>
            <p className="mt-1 text-sm text-zinc-500">
              Live usage and account data from KashRock.
            </p>
            {error ? <p className="mt-2 text-sm text-amber-300">{error}</p> : null}
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Metric
              label="Requests this month"
              value={
                loading
                  ? 'Loading…'
                  : data.usage?.requests_this_month.toLocaleString() ?? null
              }
            />
            <Metric
              label="Monthly limit"
              value={
                loading
                  ? 'Loading…'
                  : data.usage?.limit_month.toLocaleString() ?? null
              }
            />
            <Metric
              label="Success rate"
              value={loading ? 'Loading…' : successRate}
            />
          </div>

          <ApiKeyPanel keys={data.keys} onChanged={refresh} />

          <section className="rounded border border-white/10 bg-[#0C0D0F] p-6">
            <h2 className="font-medium text-white">Recent requests</h2>
            {loading ? <p className="mt-4 text-zinc-500">Loading…</p> : null}
            {!loading && !data.logs.length ? (
              <p className="mt-4 text-zinc-500">No request logs available.</p>
            ) : null}
            <div className="mt-4 space-y-2">
              {data.logs.map((log) => (
                <div
                  key={log.id}
                  className="grid grid-cols-[70px_1fr_auto] gap-3 rounded bg-black/30 p-3 text-sm"
                >
                  <span className="text-zinc-400">{log.method}</span>
                  <code className="truncate text-zinc-300">{log.endpoint}</code>
                  <span
                    className={
                      log.status_code < 400 ? 'text-emerald-400' : 'text-red-400'
                    }
                  >
                    {log.status_code}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </>
  )
}

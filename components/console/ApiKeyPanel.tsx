'use client'

import { useState } from 'react'

import { api, type ApiKey } from '@/lib/api-client'

interface ApiKeyPanelProps {
  keys: ApiKey[]
  onChanged: () => Promise<void>
}

export default function ApiKeyPanel({ keys, onChanged }: ApiKeyPanelProps) {
  const [plainKey, setPlainKey] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createKey = async () => {
    setBusy(true)
    setError(null)
    try {
      const result = await api.createApiKey('Default Key')
      setPlainKey(result.api_key)
      await onChanged()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Unable to create key.')
    } finally {
      setBusy(false)
    }
  }

  const copyKey = async () => {
    if (!plainKey) return
    await navigator.clipboard.writeText(plainKey)
    setCopied(true)
  }

  return (
    <section className="rounded border border-white/10 bg-[#0C0D0F] p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="font-medium text-white">API keys</h2>
          <p className="mt-1 text-sm text-zinc-500">
            {keys.length
              ? `${keys.length} key${keys.length === 1 ? '' : 's'} on your account`
              : 'No API key is available.'}
          </p>
        </div>
        {!keys.length ? (
          <button
            type="button"
            disabled={busy}
            onClick={() => void createKey()}
            className="rounded bg-white px-3 py-2 text-sm font-medium text-black disabled:opacity-50"
          >
            {busy ? 'Creating…' : 'Create key'}
          </button>
        ) : null}
      </div>

      {keys.map((key) => (
        <div key={key.id} className="mt-4 rounded bg-black/40 p-3 font-mono text-sm">
          {key.key_prefix}… <span className="text-zinc-600">({key.status})</span>
        </div>
      ))}

      {plainKey ? (
        <div className="mt-4 rounded border border-emerald-500/30 p-4">
          <p className="text-sm text-emerald-300">Copy this key now. It will not be shown again.</p>
          <code className="mt-2 block break-all text-emerald-200">{plainKey}</code>
          <button type="button" onClick={() => void copyKey()} className="mt-3 underline">
            {copied ? 'Copied' : 'Copy key'}
          </button>
        </div>
      ) : null}
      {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
    </section>
  )
}

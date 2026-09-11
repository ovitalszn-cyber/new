"use client"

import { useEffect, useState } from "react"

import {
  AUTH_COMPLETE_KEY,
  AUTH_COMPLETE_RETURN,
} from "@/lib/auth/complete-storage"

export default function AuthCompletePage() {
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [returnTo, setReturnTo] = useState("/console")
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    try {
      const key = sessionStorage.getItem(AUTH_COMPLETE_KEY)
      const next = sessionStorage.getItem(AUTH_COMPLETE_RETURN) || "/console"
      setReturnTo(next)
      if (!key) {
        window.location.replace(next)
        return
      }
      setApiKey(key)
      sessionStorage.removeItem(AUTH_COMPLETE_KEY)
    } catch {
      window.location.replace("/console")
    }
  }, [])

  if (!apiKey) {
    return (
      <div className="min-h-screen bg-[#08090A] flex items-center justify-center text-zinc-400">
        Finishing sign-in…
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#08090A] flex items-center justify-center">
      <main className="w-full max-w-xl mx-6 bg-[#0C0D0F] border border-white/10 rounded-lg p-8">
        <h1 className="text-2xl font-medium text-white mb-2">Your API key is ready</h1>
        <p className="text-zinc-400 mb-4">
          Copy it now and store it securely. It will not be shown again.
        </p>
        <code className="block bg-black text-green-300 p-4 overflow-wrap-anywhere break-all">
          {apiKey}
        </code>
        <div className="flex gap-3 mt-5">
          <button
            type="button"
            className="bg-white text-black px-4 py-2.5 font-semibold rounded-sm"
            onClick={async () => {
              await navigator.clipboard.writeText(apiKey)
              setCopied(true)
            }}
          >
            {copied ? "Copied" : "Copy key"}
          </button>
          <a
            href={returnTo}
            className="border border-white/20 text-white px-4 py-2.5 font-semibold rounded-sm"
          >
            Continue
          </a>
        </div>
      </main>
    </div>
  )
}

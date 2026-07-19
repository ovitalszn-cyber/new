'use client'

import { useSession } from '@/components/auth/SessionProvider'

export default function LandingAuthNav() {
  const { status, user, logout } = useSession()

  if (status === 'loading') {
    return (
      <div className="flex items-center gap-4">
        <span className="text-sm text-zinc-600">…</span>
      </div>
    )
  }

  if (status === 'authenticated') {
    return (
      <div className="flex items-center gap-4">
        <span className="hidden sm:inline text-sm text-zinc-400 truncate max-w-[160px]">
          {user?.email}
        </span>
        <a
          href="/console"
          className="text-sm font-normal text-zinc-400 hover:text-white transition-colors"
        >
          Console
        </a>
        <a
          href="#pricing"
          className="bg-white text-black px-4 py-2 text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors"
        >
          Upgrade
        </a>
        <button
          type="button"
          onClick={() => void logout()}
          className="text-sm font-normal text-zinc-500 hover:text-white transition-colors"
        >
          Log out
        </button>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-4">
      <a
        href="/login"
        className="text-sm font-normal text-zinc-400 hover:text-white transition-colors"
      >
        Log in
      </a>
      <a
        href="#pricing"
        className="bg-white text-black px-4 py-2 text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors"
      >
        Get API Key
      </a>
    </div>
  )
}

import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { GoogleSignInButton } from "@/components/auth/GoogleSignInButton"
import { ACCESS_COOKIE, REFRESH_COOKIE } from "@/lib/auth/cookies"
import { hasUsableSessionCookies } from "@/lib/auth/jwt"
import { safeReturnTo } from "@/lib/auth/navigation"

interface LoginPageProps {
  searchParams: Promise<{ error?: string; returnTo?: string }>
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const params = await searchParams
  const returnTo = safeReturnTo(params.returnTo)
  const jar = await cookies()
  if (
    hasUsableSessionCookies({
      access: jar.get(ACCESS_COOKIE)?.value,
      refresh: jar.get(REFRESH_COOKIE)?.value,
    })
  ) {
    redirect(returnTo)
  }

  const loginHref = `/api/auth/login?returnTo=${encodeURIComponent(returnTo)}`

  return (
    <div className="min-h-screen bg-[#08090A] flex items-center justify-center">
      <div className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-medium text-white mb-2">Sign in to KashRock</h1>
          <p className="text-zinc-400">Access your esports data analytics dashboard</p>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-lg p-6">
          {params.error ? (
            <p className="mb-4 text-sm text-red-300" role="alert">
              {params.error}
            </p>
          ) : null}
          <GoogleSignInButton href={loginHref} />
        </div>

        <p className="text-center text-zinc-500 text-sm mt-6">
          By signing in, you agree to our{" "}
          <a href="/legal" className="text-zinc-400 hover:text-white transition-colors">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/legal?tab=privacy" className="text-zinc-400 hover:text-white transition-colors">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  )
}

import Link from 'next/link'

import CheckoutReturn from '@/components/checkout/CheckoutReturn'

interface CheckoutReturnPageProps {
  searchParams: Promise<{ session_id?: string }>
}

export default async function CheckoutReturnPage({
  searchParams,
}: CheckoutReturnPageProps) {
  const { session_id: sessionId } = await searchParams
  if (sessionId) return <CheckoutReturn sessionId={sessionId} />

  return (
    <main className="min-h-screen bg-[#08090A] text-white grid place-items-center p-6">
      <section className="rounded border border-white/10 bg-white/5 p-8">
        <h1 className="text-xl font-semibold">Missing checkout session</h1>
        <p className="mt-2 text-zinc-400">
          Return to pricing and start checkout again.
        </p>
        <Link href="/#pricing" className="mt-5 inline-block underline">
          View plans
        </Link>
      </section>
    </main>
  )
}

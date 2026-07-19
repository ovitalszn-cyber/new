import CheckoutStart from '@/components/checkout/CheckoutStart'

const CHECKOUT_PLANS = new Set(['sandbox', 'hobby', 'builder', 'pro'])

interface CheckoutStartPageProps {
  searchParams: Promise<{ plan?: string }>
}

export default async function CheckoutStartPage({
  searchParams,
}: CheckoutStartPageProps) {
  const { plan } = await searchParams
  return (
    <CheckoutStart plan={plan && CHECKOUT_PLANS.has(plan) ? plan : null} />
  )
}

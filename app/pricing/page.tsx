import type { Metadata } from "next"

import PricingPlans from "@/components/PricingPlans"
import { MarketingShell } from "@/components/seo/MarketingShell"

export const metadata: Metadata = {
  title: { absolute: "Esports Data API Pricing — Plans from Free to Pro | KashRock" },
  description:
    "Transparent esports data API pricing. Free Sandbox for CS2 props, Hobby from $29/mo, Builder $99/mo, Pro $249/mo. Instant key — no enterprise quote.",
  alternates: { canonical: "/pricing" },
  openGraph: {
    title: "Esports Data API Pricing | KashRock",
    description:
      "Flat-rate esports data API plans. Start free with CS2 props; upgrade for LoL, Dota, matches, and production throughput.",
    url: "https://www.kashrock.com/pricing",
  },
}

export default function PricingPage() {
  return (
    <MarketingShell>
      <section className="relative pt-24 pb-12 md:pt-40 md:pb-16 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Pricing.
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-light leading-relaxed">
            Start free with CS2 props. Upgrade when you need full esports coverage, including League of
            Legends, Dota 2, live/historical matches, and production-scale API usage.
          </p>
        </div>
      </section>

      <section className="pb-24 max-w-7xl mx-auto px-6">
        <PricingPlans />
        <p className="text-center text-sm text-zinc-500 mt-10">
          Questions about coverage or volume?{" "}
          <a href="/support" className="text-white underline underline-offset-2">
            Contact support
          </a>
          .
        </p>
      </section>
    </MarketingShell>
  )
}

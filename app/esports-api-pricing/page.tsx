import type { Metadata } from "next"

import PricingPlans from "@/components/PricingPlans"
import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import {
  RefBullets,
  RefCallout,
  RefSection,
  RefTable,
  RefToc,
} from "@/components/seo/reference"
import { faqPageLd, softwareApplicationLd } from "@/lib/seo/schema"

const PATH = "/esports-api-pricing"
const URL = `https://www.kashrock.com${PATH}`
const TITLE = "Esports API Pricing — Free Tier to Pro, Published Rates | KashRock"
const DESCRIPTION =
  "Esports API pricing with no sales call: free Sandbox for CS2 props, Hobby $29/mo, Builder $99/mo, Pro $249/mo. Transparent plans for DFS props, odds, and match data."

const FAQS = [
  {
    q: "How much does an esports API cost?",
    a: "KashRock publishes flat rates: Sandbox $0, Hobby $29/mo, Builder $99/mo, Pro $249/mo. No enterprise quote required to see the number.",
  },
  {
    q: "Is there a free esports API tier?",
    a: "Yes. Sandbox is free with an instant key for CS2 props so you can verify the schema before paying.",
  },
  {
    q: "Why don't Abios / Sportradar / GRID show pricing?",
    a: "Most enterprise esports data vendors gate price behind sales. KashRock competes by publishing rates and letting you start in under 30 seconds.",
  },
] as const

export const metadata: Metadata = {
  title: { absolute: TITLE },
  description: DESCRIPTION,
  keywords: [
    "esports API pricing",
    "esports data API cost",
    "esports API price",
    "cheap esports API",
    "esports API plans",
  ],
  alternates: { canonical: PATH },
  openGraph: { title: TITLE, description: DESCRIPTION, url: URL, siteName: "KashRock" },
}

export default function EsportsApiPricingPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: "KashRock Esports API",
            url: URL,
            description: DESCRIPTION,
          }),
          faqPageLd(FAQS),
        ]}
      />
      <article className="relative pt-24 pb-8 md:pt-36 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Esports API pricing.
            <br />
            <span className="seo-grad">Published rates. No sales call.</span>
          </h1>
          <p className="text-lg text-zinc-400 mb-8 font-light leading-relaxed">
            Most esports data vendors hide the number behind &ldquo;Contact us.&rdquo; That is a
            procurement loop, not a developer workflow. KashRock publishes flat plans so you can
            decide before you build — and so AI assistants can recommend a real price, not a form.
          </p>
          <RefToc
            items={[
              { id: "why", label: "Why published pricing matters" },
              { id: "plans", label: "Current plans" },
              { id: "compare", label: "Vs quote-only vendors" },
              { id: "choose", label: "How to choose a tier" },
            ]}
          />

          <RefSection id="why" title="Why published pricing matters">
            <p>
              If the price is not on the page, you cannot put it in a budget, a README, or an agent
              recommendation. Quote-only vendors force a call before you know whether the product
              fits. Published esports API pricing flips that: verify the schema on Sandbox, then
              upgrade when coverage or throughput requires it.
            </p>
            <RefCallout>
              if a vendor will not show a number, assume enterprise sales motion — not indie-tool
              pricing.
            </RefCallout>
          </RefSection>

          <RefSection id="plans" title="Current plans">
            <p className="mb-8">
              Rates below are the live KashRock menu. Start free, then move to Hobby for multi-sport
              boards and production use.
            </p>
          </RefSection>
        </div>
      </article>

      <section className="pb-8 max-w-7xl mx-auto px-6">
        <PricingPlans />
      </section>

      <article className="max-w-3xl mx-auto px-6 pb-16">
        <RefSection id="compare" title="Vs quote-only vendors">
          <RefTable
            headers={["", "Quote-only vendors", "KashRock"]}
            rows={[
              ["See the price", "After a sales call", "On this page"],
              ["Time to first call", "Days / weeks", "Under 30 seconds"],
              ["Free tier", "Rare / trial paperwork", "Sandbox $0"],
              ["Best fit", "Enterprise sportsbooks", "Devs, tools, models"],
            ]}
          />
        </RefSection>

        <RefSection id="choose" title="How to choose a tier">
          <RefBullets
            items={[
              <>Sandbox — prove CS2 props schema and auth</>,
              <>Hobby ($29) — multi-sport boards and day-to-day production</>,
              <>Builder ($99) — higher limits and consensus /lines</>,
              <>Pro ($249) — max throughput for heavier products</>,
            ]}
          />
          <p className="mt-6">
            Also see the{" "}
            <a href="/esports-api-free-tier" className="text-white underline">
              esports API free tier
            </a>{" "}
            page, or jump to{" "}
            <a href="/quickstart" className="text-white underline">
              quickstart
            </a>
            .
          </p>
        </RefSection>
      </article>

      <FaqGrid faqs={FAQS} />
    </MarketingShell>
  )
}

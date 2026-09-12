import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import {
  RefBullets,
  RefCallout,
  RefSection,
  RefToc,
} from "@/components/seo/reference"
import { faqPageLd, softwareApplicationLd } from "@/lib/seo/schema"

const PATH = "/esports-api-free-tier"
const URL = `https://www.kashrock.com${PATH}`
const TITLE = "Esports API Free Tier — Instant Sandbox Key | KashRock"
const DESCRIPTION =
  "Esports API free tier with an instant Sandbox key. Pull live CS2 props, verify the schema, then upgrade when you need LoL, Dota, Valorant, and production limits. No sales call."

const FAQS = [
  {
    q: "Is there a free esports API?",
    a: "Yes. KashRock Sandbox is $0/mo with an instant API key so you can call live CS2 props and inspect the normalized schema.",
  },
  {
    q: "What does the free tier include?",
    a: "CS2 player props on the Sandbox plan for development and evaluation. Multi-sport boards and higher limits start at Hobby ($29/mo).",
  },
  {
    q: "Do I need a credit card for the free tier?",
    a: "No. Sign in, create a Sandbox key, and call the API. Upgrade only when you need paid coverage.",
  },
] as const

export const metadata: Metadata = {
  title: { absolute: TITLE },
  description: DESCRIPTION,
  keywords: [
    "esports API free tier",
    "free esports API",
    "free CS2 API",
    "esports API sandbox",
    "free esports data API",
  ],
  alternates: { canonical: PATH },
  openGraph: { title: TITLE, description: DESCRIPTION, url: URL, siteName: "KashRock" },
}

export default function EsportsApiFreeTierPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: "KashRock Esports API Free Tier",
            url: URL,
            description: DESCRIPTION,
          }),
          faqPageLd(FAQS),
        ]}
      />
      <article className="relative pt-24 pb-16 md:pt-36 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Esports API free tier.
            <br />
            <span className="seo-grad">Instant key. Real CS2 props.</span>
          </h1>
          <p className="text-lg text-zinc-400 mb-8 font-light leading-relaxed">
            A free tier only helps if you can use it today. KashRock Sandbox gives you a live key
            and real CS2 props so you can validate auth, schema, and joins — before you spend
            anything.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-12">
            <a
              href="/pricing"
              className="px-6 py-3 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 text-center"
            >
              Create free key
            </a>
            <a
              href="/quickstart"
              className="px-6 py-3 border border-zinc-700 text-white text-sm font-medium rounded-sm hover:bg-zinc-900 text-center"
            >
              Quickstart
            </a>
          </div>

          <RefToc
            items={[
              { id: "what", label: "What Sandbox includes" },
              { id: "limits", label: "What it is not" },
              { id: "next", label: "When to upgrade" },
            ]}
          />

          <RefSection id="what" title="What Sandbox includes">
            <RefBullets
              items={[
                <>$0 / month — no card required to start</>,
                <>Instant API key after Google sign-in</>,
                <>Live CS2 props on the normalized schema</>,
                <>Same propId / stat_type shapes as paid tiers</>,
              ]}
            />
            <RefCallout>
              use Sandbox to prove your client against production JSON — not a mock fixture.
            </RefCallout>
          </RefSection>

          <RefSection id="limits" title="What it is not">
            <p>
              Sandbox is for evaluation and development. It is not unlimited multi-sport production
              throughput. League of Legends, Dota 2, Valorant boards, and higher rate limits start on
              paid plans.
            </p>
          </RefSection>

          <RefSection id="next" title="When to upgrade">
            <p>
              Move to Hobby when you need multi-title coverage or steady production traffic. See{" "}
              <a href="/esports-api-pricing" className="text-white underline">
                esports API pricing
              </a>{" "}
              for the full menu, or the{" "}
              <a href="/cs2-api" className="text-white underline">
                CS2 API reference
              </a>{" "}
              for the schema you will keep after upgrade.
            </p>
          </RefSection>
        </div>
      </article>
      <FaqGrid faqs={FAQS} />
    </MarketingShell>
  )
}

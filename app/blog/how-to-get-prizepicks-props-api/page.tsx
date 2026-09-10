import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import {
  GUIDE_PP_DESCRIPTION,
  GUIDE_PP_FAQS,
  GUIDE_PP_TITLE,
} from "@/lib/seo/book-api-copy"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: GUIDE_PP_TITLE },
  description: GUIDE_PP_DESCRIPTION,
  alternates: { canonical: "/blog/how-to-get-prizepicks-props-api" },
}

export default function HowToGetPrizePicksPropsApiPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: "How to Get PrizePicks Props with an API (Without Scraping)",
            author: { "@type": "Organization", name: "KashRock" },
          },
          faqPageLd(GUIDE_PP_FAQS),
        ]}
      />
      <article className="relative pt-24 pb-12 md:pt-36 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            How to get PrizePicks props with an API (without scraping)
          </h1>
          <p className="text-lg text-zinc-400 mb-12 font-light leading-relaxed">
            If you&apos;re building a pick&apos;em tool, optimizer, or hit-rate model, you need PrizePicks
            lines in code. Here&apos;s the fast way, and why most people do it the hard way first.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            The problem with scraping PrizePicks
          </h2>
          <p className="text-base text-zinc-400 mb-10 leading-relaxed">
            PrizePicks has no official public API. So developers reverse-engineer the app&apos;s internal
            endpoints — which change without notice, rate-limit hard, and hand you raw data you still have
            to normalize. It works for a weekend and breaks in production.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            The one-call way
          </h2>
          <p className="text-base text-zinc-400 mb-6 leading-relaxed">
            KashRock ingests and normalizes the lines for you. One request, filtered by book:
          </p>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-6">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/props?book=prizepicks"`}</pre>
          <p className="text-base text-zinc-400 mb-4 leading-relaxed">
            You get back a clean row per prop — player, stat type, line, direction, team, and a canonical{" "}
            <code className="text-white">propId</code> — for CS2, LoL, Dota 2, and Valorant. Grab a free
            key on the{" "}
            <a href="/prizepicks-api" className="text-white underline">
              PrizePicks API page
            </a>{" "}
            and read the{" "}
            <a href="/docs" className="text-white underline">
              docs
            </a>
            .
          </p>
          <p className="text-xs text-zinc-600 mt-16 leading-relaxed">
            KashRock is an independent data provider, not affiliated with PrizePicks. Data is provided for
            informational and analytical use.
          </p>
        </div>
      </article>
      <FaqGrid faqs={GUIDE_PP_FAQS} />
    </MarketingShell>
  )
}

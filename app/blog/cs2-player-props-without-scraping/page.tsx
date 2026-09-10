import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { PropCode } from "@/components/seo/PropCode"
import {
  GUIDE_CS2_DESCRIPTION,
  GUIDE_CS2_FAQS,
  GUIDE_CS2_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_PRIZEPICKS } from "@/lib/seo/live-book-props"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: GUIDE_CS2_TITLE },
  description: GUIDE_CS2_DESCRIPTION,
  alternates: { canonical: "/blog/cs2-player-props-without-scraping" },
}

export default function Cs2PlayerPropsWithoutScrapingPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: "How to Get CS2 Player Props Without Scraping HLTV",
            author: { "@type": "Organization", name: "KashRock" },
          },
          faqPageLd(GUIDE_CS2_FAQS),
        ]}
      />
      <article className="relative pt-24 pb-12 md:pt-36 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            How to get CS2 player props without scraping HLTV
          </h1>
          <p className="text-lg text-zinc-400 mb-12 font-light leading-relaxed">
            Counter-Strike 2 props live across several DFS apps, and none of them hand you clean data.
            Here&apos;s how to skip the scraping.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            Why scraping falls apart
          </h2>
          <p className="text-base text-zinc-400 mb-10 leading-relaxed">
            HLTV gives you match stats but not prop lines; the DFS apps give lines but rate-limit and change
            markup constantly. Stitching them yourself means maintaining a parser per source forever.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            One endpoint, every book
          </h2>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-6">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/props"`}</pre>
          <div className="mb-8">
            <PropCode path={LIVE_PRIZEPICKS.path} sample={LIVE_PRIZEPICKS.sample.props[0]} />
          </div>
          <p className="text-base text-zinc-400 mb-4 leading-relaxed">
            Map-level depth, every DFS book, one schema. Free key on the{" "}
            <a href="/cs2-props-api" className="text-white underline">
              CS2 props API page
            </a>
            ; full board on the{" "}
            <a href="/dfs-esports-api" className="text-white underline">
              DFS Esports API
            </a>
            .
          </p>
          <p className="text-xs text-zinc-600 mt-16 leading-relaxed">
            KashRock is an independent data provider. Data is provided for informational and analytical use.
          </p>
        </div>
      </article>
      <FaqGrid faqs={GUIDE_CS2_FAQS} />
    </MarketingShell>
  )
}

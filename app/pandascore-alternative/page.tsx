import type { Metadata } from "next"

import { CompareTable } from "@/components/seo/CompareTable"
import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import {
  PANDASCORE_COMPARE,
  PANDASCORE_DESCRIPTION,
  PANDASCORE_FAQS,
  PANDASCORE_TITLE,
} from "@/lib/seo/cluster-copy"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: PANDASCORE_TITLE },
  description: PANDASCORE_DESCRIPTION,
  alternates: { canonical: "/pandascore-alternative" },
}

export default function PandaScoreAlternativePage() {
  return (
    <MarketingShell>
      <JsonLd data={faqPageLd(PANDASCORE_FAQS)} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            The PandaScore alternative.<br />
            <span className="seo-grad">Props and stats, no betting-use block.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            PandaScore restricts its stats plans to non-betting usage — a wall if you&apos;re building a DFS,
            pick&apos;em, or props tool. KashRock is built for exactly that: PrizePicks and Underdog props for
            CS2 and LoL, transparent pricing, and an instant key.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a href="/#pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200">
              Get API Key
            </a>
            <a href="/docs" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900">
              Read Documentation
            </a>
          </div>
        </div>
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">KashRock vs PandaScore</h2>
        <CompareTable headers={PANDASCORE_COMPARE.headers} rows={PANDASCORE_COMPARE.rows} />
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">Who it&apos;s for</h2>
        <ul className="space-y-4 max-w-3xl">
          {[
            "Devs building pick\u2019em, optimizer, or props-analysis tools that PandaScore\u2019s stats terms exclude.",
            "Small teams that want flat, predictable pricing instead of per-title plans.",
            "Anyone who needs DFS-book lines, not just fixtures and post-match stats.",
          ].map((item) => (
            <li key={item} className="flex items-start gap-3 text-base text-zinc-300">
              <span className="text-white mt-0.5">—</span>
              {item}
            </li>
          ))}
        </ul>
        <p className="text-base text-zinc-400 mt-10">
          See the <a href="/dfs-esports-api" className="text-white underline">DFS Esports API</a> for the PrizePicks and Underdog board, or the{" "}
          <a href="/esports-data-api" className="text-white underline">esports data API</a> pillar for matches and stats.
        </p>
      </section>
      <FaqGrid faqs={PANDASCORE_FAQS} />
    </MarketingShell>
  )
}

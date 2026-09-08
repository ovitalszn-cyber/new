import type { Metadata } from "next"

import { CompareTable } from "@/components/seo/CompareTable"
import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { ABIOS_COMPARE, ABIOS_DESCRIPTION, ABIOS_FAQS, ABIOS_TITLE } from "@/lib/seo/cluster-copy"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: ABIOS_TITLE },
  description: ABIOS_DESCRIPTION,
  alternates: { canonical: "/abios-alternative" },
}

export default function AbiosAlternativePage() {
  return (
    <MarketingShell>
      <JsonLd data={faqPageLd(ABIOS_FAQS)} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            The Abios alternative.<br />
            <span className="seo-grad">Esports data without the enterprise quote.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            If you hit &ldquo;Contact Us&rdquo; pricing and a sales call looking at Abios, KashRock is the
            developer-first option: CS2, LoL, and Dota 2 props, lines, and stats with published pricing and an
            instant API key.
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
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">KashRock vs Abios</h2>
        <CompareTable headers={ABIOS_COMPARE.headers} rows={ABIOS_COMPARE.rows} />
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">Why developers switch</h2>
        <ul className="space-y-4 max-w-3xl">
          {[
            "You can see the price before you commit — no procurement cycle.",
            "You\u2019re building today, not next quarter after a contract.",
            "You need DFS-book props, not just raw match data.",
          ].map((item) => (
            <li key={item} className="flex items-start gap-3 text-base text-zinc-300">
              <span className="text-white mt-0.5">—</span>
              {item}
            </li>
          ))}
        </ul>
        <p className="text-base text-zinc-400 mt-10">
          Start on the <a href="/esports-data-api" className="text-white underline">esports data API</a>, or jump to the{" "}
          <a href="/dfs-esports-api" className="text-white underline">DFS Esports API</a> for PrizePicks and Underdog boards.
        </p>
      </section>
      <FaqGrid faqs={ABIOS_FAQS} />
    </MarketingShell>
  )
}

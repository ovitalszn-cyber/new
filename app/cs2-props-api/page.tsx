import type { Metadata } from "next"

import { BookGrid } from "@/components/seo/BookGrid"
import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { PropCode } from "@/components/seo/PropCode"
import { CS2_DESCRIPTION, CS2_FAQS, CS2_TITLE } from "@/lib/seo/cluster-copy"
import { appFaqGraphLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: CS2_TITLE },
  description: CS2_DESCRIPTION,
  alternates: { canonical: "/cs2-props-api" },
}

export default function Cs2PropsApiPage() {
  return (
    <MarketingShell>
      <JsonLd data={appFaqGraphLd("KashRock CS2 Player Props API", CS2_FAQS)} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            CS2 Player Props API.<br />
            <span className="seo-grad">Live kills, headshots &amp; map lines.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            Pull Counter-Strike 2 player props with an instant key — serious esports data without enterprise
            pricing. Map-specific kills, headshots, and combined lines, normalized across PrizePicks, Underdog,
            Betr, and Sleeper, from one path: <code className="text-white">GET /v6/esports/cs2/props</code>.
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
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">
          Every CS2 book on one propId
        </h2>
        <p className="text-lg text-zinc-400 max-w-3xl mb-10">
          The same player and market share one canonical propId across each book — read one prop, compare all of them.
        </p>
        <BookGrid />
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">
          What the CS2 props API covers
        </h2>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Map-level stat depth</strong>
            <p className="text-zinc-400 mt-2">kills, headshots, and map-1/map-2 lines, not just who won.</p>
          </li>
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Every DFS book</strong>
            <p className="text-zinc-400 mt-2">PrizePicks, Underdog, Betr, Sleeper, Dabble, ParlayPlay on one schema.</p>
          </li>
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Canonical IDs</strong>
            <p className="text-zinc-400 mt-2">a FaZe vs NaVi match keeps one ID across books, so a name-spelling difference never breaks your app.</p>
          </li>
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Outcome verification</strong>
            <p className="text-zinc-400 mt-2">props resolve hit/miss/push from final stats, so you can build bet trackers and leaderboards without your own scoring engine.</p>
          </li>
        </ul>
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <div className="flex flex-col lg:flex-row gap-16 items-center">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
              GET /v6/esports/cs2/props
            </h2>
            <p className="text-lg text-zinc-500 mb-6">Live CS2 PrizePicks prop from production. Same shape for every book.</p>
            <h2 className="text-2xl font-medium tracking-tight text-white mb-4">Why developers use it</h2>
            <p className="text-base text-zinc-400 mb-6">
              Raw provider APIs only show active markets and only for one book. KashRock normalizes CS2 props
              across every DFS book and tracks each one through its full lifecycle, so a pick&apos;em tool,
              optimizer, or hit-rate model reads one schema instead of six scrapers.
            </p>
            <p className="text-base text-zinc-400">
              Building a pick&apos;em or optimizer? Start on the <a href="/dfs-esports-api" className="text-white underline">DFS Esports API</a>.
              Comparing prices across books? See the <a href="/esports-odds-api" className="text-white underline">esports odds API</a>. Want the
              full picture? The <a href="/esports-data-api" className="text-white underline">esports data API</a> adds matches and stats.
            </p>
          </div>
          <div className="flex-1 w-full max-w-2xl">
            <PropCode />
          </div>
        </div>
      </section>
      <FaqGrid faqs={CS2_FAQS} />
    </MarketingShell>
  )
}

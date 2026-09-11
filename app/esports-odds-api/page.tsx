import type { Metadata } from "next"

import { BookGrid } from "@/components/seo/BookGrid"
import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { PropCode } from "@/components/seo/PropCode"
import { ODDS_DESCRIPTION, ODDS_FAQS, ODDS_TITLE } from "@/lib/seo/cluster-copy"
import { appFaqGraphLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: ODDS_TITLE },
  description: ODDS_DESCRIPTION,
  alternates: { canonical: "/esports-odds-api" },
}

export default function EsportsOddsApiPage() {
  return (
    <MarketingShell>
      <JsonLd data={appFaqGraphLd("KashRock Esports Odds API", ODDS_FAQS)} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Esports Odds API.<br />
            <span className="seo-grad">Normalized lines across every book.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            Pull esports odds and lines for CS2, League of Legends, and Dota 2 with an instant key. Compare DFS
            books plus Thunderpick sportsbook prices and Kalshi / Polymarket prediction-market mainlines on the
            same canonical <code className="text-white">propId</code>:{" "}
            <code className="text-white">GET /v6/esports/{"{sport}"}/props</code> and consensus{" "}
            <code className="text-white">GET /v6/esports/{"{sport}"}/lines</code>.
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
          One propId, every book&apos;s price
        </h2>
        <p className="text-lg text-zinc-400 max-w-3xl mb-10">
          Read a single prop and get each book&apos;s line and odds side by side — no reconciling schemas.
        </p>
        <BookGrid />
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">
          Built for line shopping and off-market detection
        </h2>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">American odds + line</strong>
            <p className="text-zinc-400 mt-2">on every offer — model the price and the threshold.</p>
          </li>
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Over and under share a propId</strong>
            <p className="text-zinc-400 mt-2">build both sides of a market cleanly.</p>
          </li>
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Multi-title</strong>
            <p className="text-zinc-400 mt-2">CS2, LoL, Dota 2, and Valorant on one key.</p>
          </li>
          <li className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <strong className="text-white">Historical lines</strong>
            <p className="text-zinc-400 mt-2">backtest against indexed player game logs.</p>
          </li>
        </ul>
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <div className="flex flex-col lg:flex-row gap-16 items-center">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
              GET /v6/esports/cs2/props
            </h2>
            <p className="text-lg text-zinc-500 mb-6">Live prop from production — <code className="text-zinc-300">odds</code> and <code className="text-zinc-300">line</code> on every offer.</p>
            <h2 className="text-2xl font-medium tracking-tight text-white mb-4">Why developers use it</h2>
            <p className="text-base text-zinc-400 mb-6">
              Comparing lines across DFS books normally means one integration per site and constant markup
              breakage. KashRock hands you a de-duplicated, cross-book view on one propId, so a line-shopping
              tool or value model reads one feed instead of maintaining six scrapers.
            </p>
            <p className="text-base text-zinc-400 mb-6">
              Want the DFS-book framing? See the <a href="/dfs-esports-api" className="text-white underline">DFS Esports API</a>. Focused on CS2?
              The <a href="/cs2-props-api" className="text-white underline">CS2 player props API</a>. Everything at once? The{" "}
              <a href="/esports-data-api" className="text-white underline">esports data API</a> pillar.
            </p>
            <div className="flex flex-col gap-2 text-sm text-zinc-400">
              <a href="/esports-consensus-api" className="hover:text-white">Esports consensus API →</a>
              <a href="/thunderpick-api" className="hover:text-white">Thunderpick API →</a>
              <a href="/kalshi-api" className="hover:text-white">Kalshi API →</a>
              <a href="/polymarket-api" className="hover:text-white">Polymarket API →</a>
              <a href="/boom-api" className="hover:text-white">Boom API →</a>
              <a href="/pick6-api" className="hover:text-white">Pick6 API →</a>
              <a href="/prizepicks-api" className="hover:text-white">PrizePicks API →</a>
            </div>
          </div>
          <div className="flex-1 w-full max-w-2xl">
            <PropCode />
          </div>
        </div>
      </section>
      <FaqGrid faqs={ODDS_FAQS} />
    </MarketingShell>
  )
}

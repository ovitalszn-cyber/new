import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import {
  HISTORICAL_DESCRIPTION,
  HISTORICAL_FAQS,
  HISTORICAL_TITLE,
} from "@/lib/seo/historical-copy"
import { faqPageLd, softwareApplicationLd } from "@/lib/seo/schema"

const PATH = "/historical-esports-data-api"
const URL = `https://www.kashrock.com${PATH}`

export const metadata: Metadata = {
  title: { absolute: HISTORICAL_TITLE },
  description: HISTORICAL_DESCRIPTION,
  alternates: { canonical: PATH },
  keywords: [
    "historical esports data",
    "historical esports data api",
    "esports historical odds",
    "esports quote tape",
    "esports gamelogs api",
    "backtest esports props",
    "prizepicks historical lines",
  ],
  openGraph: {
    title: HISTORICAL_TITLE,
    description: HISTORICAL_DESCRIPTION,
    url: URL,
    siteName: "KashRock",
  },
  twitter: {
    card: "summary_large_image",
    title: HISTORICAL_TITLE,
    description: HISTORICAL_DESCRIPTION,
  },
}

const STRUGGLES = [
  {
    title: "Books do not sell you a history API",
    body: "PrizePicks, Underdog, and the rest show today's board. Yesterday's line is gone from the app. Scrapers that worked last month break when the payload or CDN changes.",
  },
  {
    title: "Stats sites are not book-native",
    body: "HLTV, VLR, and DatDota tell you what happened on the map. They do not tell you what line the DFS app posted at 2pm — so hit-rate models invent joins that never match production props.",
  },
  {
    title: "IDs drift across every source",
    body: "One player, five spellings. One market, six stat strings. Without stable prop and player IDs, historical joins silently miss rows and your backtest looks better than live.",
  },
]

const SOLVES = [
  {
    title: "Quote tape per contract",
    body: "GET /v6/esports/history/contract returns the vault tape for a market_key or prop_id+book — line, price, status — without live fan-out on the request.",
  },
  {
    title: "Player map gamelogs",
    body: "GET /v6/esports/{sport}/players/{slug}/gamelogs pulls vault-backed map rows so you can score a prop against what the player actually posted.",
  },
  {
    title: "Settled results",
    body: "The results feed grades props against outcomes so you can measure hit / miss / push on the same IDs you used for the live board.",
  },
]

export default function HistoricalEsportsDataApiPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: "KashRock Historical Esports Data API",
            url: URL,
            description: HISTORICAL_DESCRIPTION,
          }),
          faqPageLd(HISTORICAL_FAQS),
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: "Historical Esports Data Without Scraping",
            description: HISTORICAL_DESCRIPTION,
            author: { "@type": "Organization", name: "KashRock" },
            mainEntityOfPage: URL,
          },
        ]}
      />

      <section className="relative pt-24 pb-16 md:pt-40 md:pb-20 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Historical esports data.
            <br />
            <span className="seo-grad">Without the scrape tax.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            Builders looking for historical lines hit the same wall: books hide the past, stats sites
            omit the offer, and scrapers rot. KashRock keeps the quote tape, gamelogs, and settlements
            behind one key.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/pricing"
              className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200"
            >
              Get API Key
            </a>
            <a
              href="/docs/endpoints/history"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900"
            >
              History tape docs
            </a>
          </div>
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">
          Why historical esports data is hard to find
        </h2>
        <p className="text-base text-zinc-400 max-w-3xl mb-10 leading-relaxed">
          If you searched for historical PrizePicks lines, CS2 kill tapes, or LoL prop backtests, you
          already know the gap. The pain is not &quot;more scrapers.&quot; It is missing a vault that
          remembers what was offered and how it settled.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {STRUGGLES.map((item) => (
            <div
              key={item.title}
              className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8"
            >
              <h3 className="text-lg font-medium text-white mb-3">{item.title}</h3>
              <p className="text-base text-zinc-400 leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">
          How KashRock solves it
        </h2>
        <p className="text-base text-zinc-400 max-w-3xl mb-10 leading-relaxed">
          Workers ingest live boards and match stats continuously. History endpoints read what was
          stored — so your backtest uses the same contract IDs as production.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SOLVES.map((item) => (
            <div
              key={item.title}
              className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8"
            >
              <h3 className="text-lg font-medium text-white mb-3">{item.title}</h3>
              <p className="text-base text-zinc-400 leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16 max-w-3xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
          Start with one contract
        </h2>
        <p className="text-base text-zinc-400 mb-6 leading-relaxed">
          Pull the vault tape for a market you already saw on the live board:
        </p>
        <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-6">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/history/contract?market_key=kr_mk_…"`}</pre>
        <p className="text-base text-zinc-400 mb-4 leading-relaxed">
          Then join{" "}
          <a href="/docs/api-reference" className="text-white underline">
            player gamelogs
          </a>{" "}
          and{" "}
          <a href="/docs/endpoints/results" className="text-white underline">
            results
          </a>
          . Coverage by title is on{" "}
          <a href="/coverage" className="text-white underline">
            /coverage
          </a>
          . Full route list on the{" "}
          <a href="/esports-data-api" className="text-white underline">
            esports data API
          </a>{" "}
          page.
        </p>
      </section>

      <FaqGrid faqs={HISTORICAL_FAQS} />
    </MarketingShell>
  )
}

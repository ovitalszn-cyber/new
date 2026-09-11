import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import {
  CONSENSUS_DESCRIPTION,
  CONSENSUS_FAQS,
  CONSENSUS_TITLE,
} from "@/lib/seo/consensus-copy"
import { faqPageLd, softwareApplicationLd } from "@/lib/seo/schema"

const PATH = "/esports-consensus-api"
const URL = `https://www.kashrock.com${PATH}`

export const metadata: Metadata = {
  title: { absolute: CONSENSUS_TITLE },
  description: CONSENSUS_DESCRIPTION,
  alternates: { canonical: PATH },
  keywords: [
    "esports consensus odds api",
    "esports fair odds api",
    "esports lines api",
    "kalshi polymarket thunderpick",
    "prediction market consensus",
    "de-vig esports odds",
    "cs2 consensus lines",
    "esports edge api",
  ],
  openGraph: {
    title: CONSENSUS_TITLE,
    description: CONSENSUS_DESCRIPTION,
    url: URL,
    siteName: "KashRock",
  },
  twitter: {
    card: "summary_large_image",
    title: CONSENSUS_TITLE,
    description: CONSENSUS_DESCRIPTION,
  },
}

const STRUGGLES = [
  {
    title: "One venue is not a fair price",
    body: "A single sportsbook or DFS board can lag, shade, or thin out. Models that anchor to one feed inherit that bias and call it edge.",
  },
  {
    title: "Prediction markets and books do not share a schema",
    body: "Kalshi and Polymarket speak probability. Thunderpick speaks American. Without de-vig and join keys, you cannot build a real consensus.",
  },
  {
    title: "Raw edge spam is noise",
    body: "Huge gaps usually mean bad joins, dead liquidity, or two-source accidents — not alpha. Ungated feeds train models on garbage.",
  },
]

const SOLVES = [
  {
    title: "De-vig + weighted consensus",
    body: "Each venue is normalized to probabilities that sum to 1.0. Consensus is a weighted mean (prediction markets default weight 1.5).",
  },
  {
    title: "Hard quality gates",
    body: "Liquidity floors, ≥3 sources for top_edges, disagreement ≤12 pts, raw edge ≤8%. Ranked by confidence × liquidity × edge.",
  },
  {
    title: "One route, four markets",
    body: "match_winner, map_winner, total_maps, and map_handicap on GET /v6/esports/{sport}/lines — CS2, Valorant, LoL, Dota 2.",
  },
]

export default function EsportsConsensusApiPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: "KashRock Esports Consensus Odds API",
            url: URL,
            description: CONSENSUS_DESCRIPTION,
          }),
          faqPageLd(CONSENSUS_FAQS),
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: "Esports Consensus Odds from Sportsbooks and Prediction Markets",
            description: CONSENSUS_DESCRIPTION,
            author: { "@type": "Organization", name: "KashRock" },
            mainEntityOfPage: URL,
          },
        ]}
      />

      <section className="relative pt-24 pb-16 md:pt-40 md:pb-20 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Esports consensus odds.
            <br />
            <span className="seo-grad">Fair lines, gated edges.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            De-vig Thunderpick, Kalshi, and Polymarket into one fair probability per outcome. Surface
            only edges that clear liquidity and agreement gates —{" "}
            <code className="text-white">GET /v6/esports/{"{sport}"}/lines</code>.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/#pricing"
              className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200"
            >
              Get API Key
            </a>
            <a
              href="/docs/endpoints/lines"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900"
            >
              /lines docs
            </a>
          </div>
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">
          Why consensus odds beat a single book
        </h2>
        <p className="text-base text-zinc-400 max-w-3xl mb-10 leading-relaxed">
          If you searched for fair esports odds, prediction-market priors, or a Kalshi + Polymarket +
          sportsbook join — this is the product. Not another scrape. A consensus layer.
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
          How KashRock builds consensus
        </h2>
        <p className="text-base text-zinc-400 max-w-3xl mb-10 leading-relaxed">
          Workers keep venue boards warm. The /lines request reads Redis, joins matchups, de-vigs,
          and ranks — no live upstream fan-out on the call path.
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
          Call consensus in one request
        </h2>
        <p className="text-base text-zinc-400 mb-6 leading-relaxed">
          Builder or Pro key. Response includes full <code className="text-white">events</code> with
          quality flags plus a gated <code className="text-white">top_edges</code> feed.
        </p>
        <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-6">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/lines?market=match_winner"`}</pre>
        <p className="text-base text-zinc-400 mb-4 leading-relaxed">
          Venue pages:{" "}
          <a href="/thunderpick-api" className="text-white underline">
            Thunderpick
          </a>
          ,{" "}
          <a href="/kalshi-api" className="text-white underline">
            Kalshi
          </a>
          ,{" "}
          <a href="/polymarket-api" className="text-white underline">
            Polymarket
          </a>
          . Cross-book props:{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          . Field reference:{" "}
          <a href="/docs/endpoints/lines" className="text-white underline">
            /docs/endpoints/lines
          </a>
          .
        </p>
      </section>

      <FaqGrid faqs={CONSENSUS_FAQS} />
    </MarketingShell>
  )
}

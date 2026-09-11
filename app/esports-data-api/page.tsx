import type { Metadata } from "next"

import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { DATA_API_DESCRIPTION, DATA_API_FAQS, DATA_API_TITLE } from "@/lib/seo/copy"
import { GAME_LOGOS } from "@/lib/seo/game-logos"
import { faqPageLd, softwareApplicationLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: DATA_API_TITLE,
  description: DATA_API_DESCRIPTION,
  alternates: { canonical: "https://www.kashrock.com/esports-data-api" },
  keywords: [
    "esports data api",
    "esports api",
    "esports stats api",
    "cs2 api",
    "lol esports api",
    "dota 2 api",
  ],
  openGraph: {
    title: DATA_API_TITLE,
    description: DATA_API_DESCRIPTION,
    url: "https://www.kashrock.com/esports-data-api",
    siteName: "KashRock",
  },
  twitter: { card: "summary_large_image", title: DATA_API_TITLE, description: DATA_API_DESCRIPTION },
}

const PILLARS = [
  { title: "Props and lines", body: "Live ingested player props across CS2, LoL, Dota 2, and Valorant. One schema, many books." },
  { title: "Matches and stats", body: "Schedules, box scores, game logs, and map-level stats — not just who won." },
  { title: "Stable IDs", body: "Players, teams, matches, and props keep the same ID when a book spells the name differently." },
]

export default function EsportsDataApiPage() {
  const url = "https://www.kashrock.com/esports-data-api"
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: "KashRock Esports Data API",
            url,
            description: DATA_API_DESCRIPTION,
          }),
          faqPageLd(DATA_API_FAQS),
        ]}
      />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Esports Data API.<br />
            <span className="seo-grad">CS2, LoL, Dota props, lines & stats.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            One affordable esports data API: normalized props, lines, matches, and player stats. Instant key. No enterprise quote.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a href="/pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200">
              Get API Key
            </a>
            <a href="/dfs-esports-api" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900">
              DFS Esports API — PrizePicks & Underdog
            </a>
          </div>
          <div className="mt-14 flex flex-wrap items-center justify-center gap-x-8 gap-y-4">
            {GAME_LOGOS.map((logo) => (
              <img key={logo.alt} src={logo.src} alt={logo.alt} className={`h-8 w-auto ${logo.invert ? "invert" : ""}`} />
            ))}
          </div>
        </div>
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">
          What the esports data API covers
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PILLARS.map((item) => (
            <div key={item.title} className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
              <h3 className="text-xl font-medium text-white mb-2">{item.title}</h3>
              <p className="text-base text-zinc-400 leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
        <p className="text-base text-zinc-400 mt-10">
          Shipping this weekend? Start on{" "}
          <a href="/build-esports-app" className="text-white underline">Build an esports app</a>
          {" "}or the{" "}
          <a href="/quickstart" className="text-white underline">quickstart</a>. Working on a specific
          build? Jump to the{" "}
          <a href="/cs2-props-api" className="text-white underline">CS2 player props API</a>, the{" "}
          <a href="/prizepicks-api" className="text-white underline">PrizePicks API</a>,{" "}
          <a href="/underdog-api" className="text-white underline">Underdog API</a>,{" "}
          <a href="/sleeper-api" className="text-white underline">Sleeper API</a>,{" "}
          <a href="/betr-api" className="text-white underline">Betr API</a>,{" "}
          <a href="/boom-api" className="text-white underline">Boom API</a>,{" "}
          <a href="/pick6-api" className="text-white underline">Pick6 API</a>,{" "}
          <a href="/thunderpick-api" className="text-white underline">Thunderpick API</a>,{" "}
          <a href="/kalshi-api" className="text-white underline">Kalshi API</a>, or{" "}
          <a href="/polymarket-api" className="text-white underline">Polymarket API</a>. Line shopping
          lives on the{" "}
          <a href="/esports-odds-api" className="text-white underline">esports odds API</a>. Full board:{" "}
          <a href="/dfs-esports-api" className="text-white underline">DFS Esports API</a>. See{" "}
          <a href="/coverage" className="text-white underline">coverage</a> for titles and books.
        </p>
      </section>
      <section className="py-24 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">Frequently asked questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {DATA_API_FAQS.map((faq) => (
            <div key={faq.q} className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
              <h3 className="text-lg font-medium text-white mb-2">{faq.q}</h3>
              <p className="text-base text-zinc-400 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>
    </MarketingShell>
  )
}

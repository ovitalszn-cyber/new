import type { Metadata } from "next"

import { MarketingShell } from "@/components/seo/MarketingShell"

export const metadata: Metadata = {
  title: { absolute: "Esports Data API Features — Normalized Props & Stats | KashRock" },
  description:
    "KashRock features: multi-title esports coverage, near-real-time + historical data, canonical IDs, map-depth stats, model-ready feeds, and outcome verification.",
  alternates: { canonical: "/features" },
}

const FEATURES: { title: string; body: string }[] = [
  {
    title: "Esports Data Coverage",
    body: "CS2, League of Legends, Dota 2, and expanding titles — normalized across schedules, market props, player metrics, and verified outcomes.",
  },
  {
    title: "Near-Real-Time + Historical",
    body: "Sub-5-second refresh on live match data. Pull upcoming, live, and completed matches — including box scores and game logs for any date.",
  },
  {
    title: "Canonical IDs",
    body: "Players, teams, and matches are normalized across naming differences so your app never breaks when a source renames a roster.",
  },
  {
    title: "Granular Stat Depth",
    body: "Not just who won. Map-specific kill rates, first-blood percentages, round-by-round performance — the stats pro researchers actually need.",
  },
  {
    title: "Model-Ready Data",
    body: "Clean, structured payloads optimized for ML and predictive modeling — consistent timestamps and identifiers across history.",
  },
  {
    title: "Outcome Verification",
    body: "Automatically verify statistical props (matched / unmatched / push) from final stats — built for dashboards and model validation.",
  },
  {
    title: "API Reliability",
    body: "99.9% uptime target with failover across sources. Rate limiting and caching protect your integrations.",
  },
]

export default function FeaturesPage() {
  return (
    <MarketingShell>
      <section className="relative pt-24 pb-12 md:pt-40 md:pb-16 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Features.
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-light leading-relaxed">
            Everything normalized. One schema across books, titles, and history.
          </p>
        </div>
      </section>
      <section className="pb-24 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8 hover:border-white/20 transition-colors"
          >
            <h2 className="text-xl font-medium text-white mb-2 tracking-tight">{f.title}</h2>
            <p className="text-base text-zinc-400 leading-relaxed">{f.body}</p>
          </div>
        ))}
      </section>
      <section className="pb-24 text-center px-6">
        <a
          href="/pricing"
          className="inline-block px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200"
        >
          See pricing
        </a>
      </section>
    </MarketingShell>
  )
}

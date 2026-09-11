import type { Metadata } from "next"

import { MarketingShell } from "@/components/seo/MarketingShell"

export const metadata: Metadata = {
  title: { absolute: "How KashRock Works — One Esports Data Schema | KashRock" },
  description:
    "How KashRock works: standardized JSON across providers, canonical player/team/match IDs, and a single props schema for CS2, LoL, Dota, and more.",
  alternates: { canonical: "/how-it-works" },
}

export default function HowItWorksPage() {
  return (
    <MarketingShell>
      <section className="relative pt-24 pb-12 md:pt-40 md:pb-16 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            How it works.
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-light leading-relaxed">
            Built for shipping, not parsing strings. One analytics schema across schedules, props,
            stats, and outcome verification.
          </p>
        </div>
      </section>

      <section className="pb-24 max-w-3xl mx-auto px-6 space-y-10">
        <div>
          <h2 className="text-2xl font-medium text-white mb-3">Standardized JSON</h2>
          <p className="text-base text-zinc-400 leading-relaxed">
            Consistent response shape regardless of the source provider or esports title. Your client
            code stays the same when a book or feed changes underneath.
          </p>
        </div>
        <div>
          <h2 className="text-2xl font-medium text-white mb-3">Cross-source mapping</h2>
          <p className="text-base text-zinc-400 leading-relaxed">
            Canonical IDs across players, teams, and matches keep joins stable when nicknames or
            roster labels diverge across books and stats providers.
          </p>
        </div>
        <div>
          <h2 className="text-2xl font-medium text-white mb-3">One props call</h2>
          <p className="text-base text-zinc-400 leading-relaxed mb-4">
            Example shape from{" "}
            <code className="text-zinc-200">GET /v6/esports/cs2/props</code>:
          </p>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 overflow-x-auto text-xs font-mono text-zinc-300 leading-relaxed">{`{
  "source": "kashrock",
  "sport": "cs2",
  "props": [
    {
      "propId": "kr_prop_…",
      "player_name": "fear",
      "stat_type": "CS2_KILLS_MAPS_1_2",
      "line": 25.5,
      "odds": -118,
      "direction": "over",
      "team": "Fnatic",
      "book_name": "PrizePicks"
    }
  ]
}`}</pre>
        </div>
        <div className="pt-4 text-center">
          <a
            href="/quickstart"
            className="inline-block px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200 mr-3"
          >
            Quickstart
          </a>
          <a
            href="/pricing"
            className="inline-block px-8 py-3.5 border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900"
          >
            Pricing
          </a>
        </div>
      </section>
    </MarketingShell>
  )
}

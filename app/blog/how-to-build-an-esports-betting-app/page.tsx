import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: {
    absolute: "How to Build an Esports Betting App (Data, Odds & Props) | KashRock",
  },
  description:
    "What you need to build an esports betting or props app: normalized odds and lines, player stats, and outcome verification from one API. Free key, ship fast.",
  alternates: { canonical: "https://www.kashrock.com/blog/how-to-build-an-esports-betting-app" },
  openGraph: {
    title: "How to Build an Esports Betting App (Data, Odds & Props) | KashRock",
    description:
      "Normalized odds and lines, player stats, and outcome verification from one API. Free key, ship fast.",
    url: "https://www.kashrock.com/blog/how-to-build-an-esports-betting-app",
    siteName: "KashRock",
  },
}

const faqs = [
  {
    q: "What data does an esports betting app need?",
    a: "Lines and odds, player and match stats to model them, and outcome verification to grade results. KashRock exposes all three from one normalized API.",
  },
  {
    q: "Do I need to integrate each sportsbook separately?",
    a: "No. KashRock normalizes PrizePicks, Underdog, Betr, Sleeper and more onto one canonical propId, so you read one schema instead of many.",
  },
] as const

export default function HowToBuildAnEsportsBettingAppPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: "How to Build an Esports Betting App",
            author: { "@type": "Organization", name: "KashRock" },
          },
          faqPageLd(faqs),
        ]}
      />
      <article className="relative pt-24 pb-12 md:pt-36 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            How to build an esports betting app
          </h1>
          <p className="text-lg text-zinc-400 mb-12 font-light leading-relaxed">
            Three data problems stand between you and a working esports betting or props app. One API
            solves all three.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            1. Lines &amp; odds
          </h2>
          <p className="text-base text-zinc-400 mb-6 leading-relaxed">
            Pull normalized props and odds across every DFS book from one endpoint, joined on a
            canonical <code className="text-zinc-200">propId</code> for line comparison.
          </p>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-10">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/props"`}</pre>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            2. Stats to model them
          </h2>
          <p className="text-base text-zinc-400 mb-10 leading-relaxed">
            Player game logs, box scores, and match history let you build fair lines and hit-rate
            models — same key, same schema.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            3. Outcome verification
          </h2>
          <p className="text-base text-zinc-400 mb-6 leading-relaxed">
            Props resolve hit / miss / push from final stats, so you grade results without your own
            scoring engine.
          </p>
          <p className="text-base text-zinc-400 mb-4 leading-relaxed">
            Start on the{" "}
            <a href="/quickstart" className="text-white underline">
              quickstart
            </a>
            , or go deep on the{" "}
            <a href="/esports-odds-api" className="text-white underline">
              esports odds API
            </a>{" "}
            and{" "}
            <a href="/dfs-esports-api" className="text-white underline">
              DFS Esports API
            </a>
            .
          </p>
          <p className="text-xs text-zinc-600 mt-16 leading-relaxed">
            KashRock is an independent data provider, not a sportsbook. Data is for informational and
            analytical use.
          </p>
        </div>
      </article>
      <FaqGrid faqs={faqs} />
    </MarketingShell>
  )
}

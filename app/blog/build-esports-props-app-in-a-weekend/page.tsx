import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: "Build a CS2 Props App in a Weekend | KashRock" },
  description:
    "A step-by-step guide to shipping a Counter-Strike 2 player props app in two days — free API key, normalized data, and the exact calls to build the board.",
  alternates: { canonical: "https://www.kashrock.com/blog/build-esports-props-app-in-a-weekend" },
  openGraph: {
    title: "Build a CS2 Props App in a Weekend | KashRock",
    description:
      "Ship a Counter-Strike 2 player props app in two days — free API key, normalized data, exact calls.",
    url: "https://www.kashrock.com/blog/build-esports-props-app-in-a-weekend",
    siteName: "KashRock",
  },
}

const faqs = [
  {
    q: "What do I need to build a props app?",
    a: "A data source for the lines and a front end. KashRock's free key covers the data — normalized CS2 props from every DFS book — so you only build the UI.",
  },
  {
    q: "How long does it really take?",
    a: "A weekend. Data is one call; the rest is your front end. No scraping, no normalization layer to write.",
  },
] as const

export default function BuildEsportsPropsAppInAWeekendPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "Article",
            headline: "Build a CS2 Props App in a Weekend",
            author: { "@type": "Organization", name: "KashRock" },
          },
          faqPageLd(faqs),
        ]}
      />
      <article className="relative pt-24 pb-12 md:pt-36 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Build a CS2 props app in a weekend
          </h1>
          <p className="text-lg text-zinc-400 mb-12 font-light leading-relaxed">
            You don&apos;t need a data pipeline to ship a Counter-Strike 2 player props app. Here&apos;s
            the two-day path.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            Day 1: data
          </h2>
          <p className="text-base text-zinc-400 mb-6 leading-relaxed">
            Grab a free key and pull the board. One call gets you every book&apos;s CS2 props,
            normalized:
          </p>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-6">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/props"`}</pre>
          <p className="text-base text-zinc-400 mb-10 leading-relaxed">
            Each row has player, stat type, line, direction, team, book, and a canonical{" "}
            <code className="text-zinc-200">propId</code> — so you skip scraping and normalization
            entirely.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            Day 2: front end
          </h2>
          <p className="text-base text-zinc-400 mb-6 leading-relaxed">
            Render the rows, add a book filter and an over/under toggle, and you have a working board.
            Poll the endpoint for updates. Ship it.
          </p>
          <p className="text-base text-zinc-400 mb-4 leading-relaxed">
            Start on the{" "}
            <a href="/quickstart" className="text-white underline">
              quickstart
            </a>
            , get your key on the{" "}
            <a href="/cs2-props-api" className="text-white underline">
              CS2 props API page
            </a>
            , or see the{" "}
            <a href="/build-esports-app" className="text-white underline">
              full build guide
            </a>
            .
          </p>
          <p className="text-xs text-zinc-600 mt-16 leading-relaxed">
            KashRock is an independent data provider. Data is for informational and analytical use.
          </p>
        </div>
      </article>
      <FaqGrid faqs={faqs} />
    </MarketingShell>
  )
}

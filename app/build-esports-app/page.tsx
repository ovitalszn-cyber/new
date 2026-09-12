import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { faqPageLd, softwareApplicationLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: {
    absolute: "Build an Esports App Fast — Ship in 2 Days with One Data API | KashRock",
  },
  description:
    "The fastest way to build an esports app. Instant API key, one normalized endpoint for props, matches, stats & rankings, SDKs and starter templates. Free tier — ship this weekend.",
  alternates: { canonical: "https://www.kashrock.com/build-esports-app" },
  openGraph: {
    title: "Build an Esports App Fast — Ship in 2 Days with One Data API | KashRock",
    description:
      "Instant API key, one normalized endpoint for props, matches, stats & rankings. Free tier — ship this weekend.",
    url: "https://www.kashrock.com/build-esports-app",
    siteName: "KashRock",
  },
  twitter: {
    card: "summary_large_image",
    title: "Build an Esports App Fast — Ship in 2 Days | KashRock",
    description:
      "Instant API key, one normalized endpoint for props, matches, stats & rankings. Free tier — ship this weekend.",
  },
}

const faqs = [
  {
    q: "How fast can I get started?",
    a: "Instant. Create a free key, make your first call in under 30 seconds, and ship a working product in a weekend — no sales call, no procurement, no scraping to maintain.",
  },
  {
    q: "What can I build with it?",
    a: "Props and pick'em tools, DFS optimizers, stats dashboards, Discord alert bots, betting models, and esports data sites — all off one normalized API across CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, and Deadlock.",
  },
  {
    q: "Do you have SDKs and starter templates?",
    a: "Yes — copy-paste examples in the docs, plus open-source starter repos so you clone, drop in your key, and go.",
  },
  {
    q: "Is it free to start?",
    a: "Yes. Sandbox is $0/mo with an instant key. Paid plans start at $29/mo when you're ready to scale.",
  },
] as const

const SHIP_POINTS = [
  { title: "Instant key", body: "Sandbox in ~60 seconds, no sales call." },
  { title: "One normalized schema", body: "Every DFS book and title, no per-source integration." },
  { title: "Starter templates", body: "Clone, add your key, go." },
] as const

const BUILDS = [
  "Pick'em & DFS optimizer tools",
  "Player-props and line-shopping apps",
  "Esports stats dashboards & fan sites",
  "Discord alert bots and betting models",
] as const

export default function BuildEsportsAppPage() {
  const url = "https://www.kashrock.com/build-esports-app"
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: "KashRock Esports Data API",
            url,
            description:
              "The fastest way to build an esports app. Instant API key, one normalized endpoint for props, matches, stats & rankings.",
          }),
          faqPageLd(faqs),
        ]}
      />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Build an esports app in 2 days.
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            One API key, one normalized endpoint, everything esports — props, matches, player stats,
            rankings. No enterprise contract, no scraping, no data-cleaning pipeline to build first.
            Grab a free key and ship this weekend.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/pricing"
              className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200"
            >
              Get free API key
            </a>
            <a
              href="/quickstart"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900"
            >
              Quickstart
            </a>
            <a
              href="/docs"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900"
            >
              Docs
            </a>
          </div>
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">
          Ship in a weekend, not a quarter
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SHIP_POINTS.map((item) => (
            <div key={item.title} className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
              <h3 className="text-xl font-medium text-white mb-2">{item.title}</h3>
              <p className="text-base text-zinc-400 leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">
          What people build
        </h2>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {BUILDS.map((item) => (
            <li
              key={item}
              className="bg-[#0C0D0F] border border-white/10 rounded-sm px-6 py-5 text-base text-zinc-300"
            >
              {item}
            </li>
          ))}
        </ul>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
          Your first call
        </h2>
        <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-6">{`curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/props"`}</pre>
        <p className="text-base text-zinc-400 leading-relaxed">
          Start on the{" "}
          <a href="/quickstart" className="text-white underline">
            quickstart
          </a>
          , then go deep on the{" "}
          <a href="/esports-data-api" className="text-white underline">
            esports data API
          </a>{" "}
          or{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          .
        </p>
      </section>

      <FaqGrid faqs={faqs} />
    </MarketingShell>
  )
}

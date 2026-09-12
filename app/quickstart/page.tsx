import type { Metadata } from "next"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { faqPageLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: {
    absolute: "Esports Data API Quickstart — First Call in Under 30 Seconds | KashRock",
  },
  description:
    "Get an instant API key and pull normalized esports props, matches, and stats in under 30 seconds. curl, Python, and JavaScript examples. Free tier, no sales call.",
  alternates: { canonical: "https://www.kashrock.com/quickstart" },
  openGraph: {
    title: "Esports Data API Quickstart — First Call in Under 30 Seconds | KashRock",
    description:
      "Instant API key and normalized esports props in under 30 seconds. curl, Python, and JavaScript examples.",
    url: "https://www.kashrock.com/quickstart",
    siteName: "KashRock",
  },
  twitter: {
    card: "summary_large_image",
    title: "Esports Data API Quickstart | KashRock",
    description:
      "Instant API key and normalized esports props in under 30 seconds. Free tier, no sales call.",
  },
}

const faqs = [
  {
    q: "How do I get an API key?",
    a: "Sign in and create a free Sandbox key instantly from the console — no card, no sales call.",
  },
  {
    q: "What's the base URL?",
    a: "All endpoints live under /v6/esports/. Pass your key in the X-API-Key header.",
  },
  {
    q: "What are the rate limits on the free tier?",
    a: "The Sandbox tier is for development and testing; paid plans from $29/mo raise the limits for production.",
  },
] as const

const STEPS = [
  { name: "Get a free key", text: "Create a Sandbox key in the console." },
  {
    name: "Call the API",
    text: "GET /v6/esports/cs2/props with your key in the X-API-Key header.",
  },
  {
    name: "Parse the response",
    text: "Read normalized props: player, stat type, line, direction, book.",
  },
] as const

export default function QuickstartPage() {
  return (
    <MarketingShell>
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "HowTo",
            name: "Make your first KashRock esports API call",
            step: STEPS.map((step, i) => ({
              "@type": "HowToStep",
              position: i + 1,
              name: step.name,
              text: step.text,
            })),
          },
          faqPageLd(faqs),
        ]}
      />
      <section className="relative pt-24 pb-16 md:pt-40 md:pb-20 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Quickstart.
            <br />
            <span className="seo-grad">First call in under 30 seconds.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 mb-12 font-light leading-relaxed">
            Three steps from zero to normalized esports data. Free key, no sales call.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            1. Get a free key
          </h2>
          <p className="text-base text-zinc-400 mb-10 leading-relaxed">
            Create a Sandbox key in the{" "}
            <a href="/console" className="text-white underline">
              console
            </a>{" "}
            — instant, no card.
          </p>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            2. Make the call
          </h2>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-4">{`# curl
curl -H "X-API-Key: YOUR_KEY" \\
  "https://kashrock.up.railway.app/v6/esports/cs2/props"`}</pre>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-4">{`# python
import requests
r = requests.get(
  "https://kashrock.up.railway.app/v6/esports/cs2/props",
  headers={"X-API-Key": "YOUR_KEY"},
)
print(r.json()["props"][0])`}</pre>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-10">{`// javascript
const res = await fetch(
  "https://kashrock.up.railway.app/v6/esports/cs2/props",
  { headers: { "X-API-Key": "YOUR_KEY" } }
);
const { props } = await res.json();`}</pre>

          <h2 className="text-2xl md:text-3xl font-medium tracking-tight text-white mb-4">
            3. Read the response
          </h2>
          <pre className="bg-[#0C0D0F] border border-white/10 rounded-sm p-5 font-mono text-xs text-zinc-300 overflow-x-auto mb-8">{`{
  "propId": "kr_prop_959e4bdd3a1d",
  "player_name": "Ax1Le",
  "stat_type": "CS2_HEADSHOTS_MAPS_1_2",
  "line": 15.5,
  "direction": "over",
  "book_name": "PrizePicks",
  "team": "1win"
}`}</pre>
          <p className="text-base text-zinc-400 leading-relaxed">
            That&apos;s it. Full endpoints in the{" "}
            <a href="/docs" className="text-white underline">
              docs
            </a>
            ; see what you can build on{" "}
            <a href="/build-esports-app" className="text-white underline">
              Build an esports app
            </a>
            .
          </p>
        </div>
      </section>
      <FaqGrid faqs={faqs} />
    </MarketingShell>
  )
}

import type { Metadata } from "next"

import { AlternativePage } from "@/components/seo/AlternativePage"

const FAQS = [
  {
    q: "Is KashRock a Sportradar alternative for esports?",
    a: "For developers who need esports DFS props, odds, and match data with published pricing — yes. Sportradar is enterprise-oriented with sales-led packaging; KashRock is self-serve from a free Sandbox.",
  },
  {
    q: "How does pricing compare to Sportradar?",
    a: "KashRock publishes flat plans (free, then $29+/mo). Sportradar esports packages are typically quote-based through sales.",
  },
  {
    q: "What does KashRock cover?",
    a: "CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, and Deadlock props/markets, schedules, history, and Hobby+ consensus lines — with canonical IDs across books.",
  },
] as const

export const metadata: Metadata = {
  title: {
    absolute: "Sportradar Alternative for Esports Data — Published Pricing | KashRock",
  },
  description:
    "Looking for a Sportradar alternative for esports? KashRock offers DFS props, odds, and match data with transparent pricing and an instant key — no enterprise sales loop.",
  alternates: { canonical: "/sportradar-alternative" },
}

export default function SportradarAlternativePage() {
  return (
    <AlternativePage
      jsonLdFaqs={FAQS}
      h1={
        <>
          The Sportradar alternative for esports.
          <br />
          <span className="seo-grad">Self-serve data. Published price.</span>
        </>
      }
      lede="Sportradar is built for enterprise sportsbooks and media. If you need esports props and odds without a procurement cycle, KashRock is the developer-first path: instant key, free Sandbox, flat monthly plans."
      compareTitle="KashRock vs Sportradar (esports builder lens)"
      headers={["", "Sportradar", "KashRock"]}
      rows={[
        ["Pricing", "Sales / quote-led", "Published: free → $29+/mo"],
        ["Onboarding", "Enterprise motion", "Instant key, <30s to first call"],
        ["DFS book props", "Not the indie default", "PrizePicks, Underdog, Betr, Sleeper…"],
        ["Best fit", "Large operators", "Devs, tools, models"],
      ]}
      reasonsTitle="Why builders switch"
      reasons={[
        "You can see the price before a call.",
        "You need DFS-native props, not only fixtures.",
        "You ship this week, not next quarter after legal review.",
      ]}
      related={
        <>
          Compare{" "}
          <a href="/abios-alternative" className="text-white underline">
            Abios
          </a>
          ,{" "}
          <a href="/pandascore-alternative" className="text-white underline">
            PandaScore
          </a>
          , and{" "}
          <a href="/grid-alternative" className="text-white underline">
            GRID
          </a>
          — or read{" "}
          <a href="/esports-api-pricing" className="text-white underline">
            esports API pricing
          </a>
          .
        </>
      }
    />
  )
}

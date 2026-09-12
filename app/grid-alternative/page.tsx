import type { Metadata } from "next"

import { AlternativePage } from "@/components/seo/AlternativePage"

const FAQS = [
  {
    q: "Is KashRock a GRID alternative?",
    a: "For teams that want self-serve esports props and odds with public pricing — yes. GRID focuses on high-fidelity official data partnerships; KashRock focuses on normalized DFS/book markets developers can call today.",
  },
  {
    q: "How is onboarding different?",
    a: "KashRock: Google sign-in, Sandbox key, first call in under 30 seconds. GRID-style official data deals are typically partnership- and sales-led.",
  },
  {
    q: "What should I use KashRock for?",
    a: "Pick'em tools, prop models, line shopping, and grading across PrizePicks-class boards and sportsbook/prediction markets — with canonical IDs.",
  },
] as const

export const metadata: Metadata = {
  title: {
    absolute: "GRID Alternative — Esports Props API With Public Pricing | KashRock",
  },
  description:
    "GRID alternative for developers: normalized esports DFS props and odds, transparent pricing, instant API key. No partnership wait to start building.",
  alternates: { canonical: "/grid-alternative" },
}

export default function GridAlternativePage() {
  return (
    <AlternativePage
      jsonLdFaqs={FAQS}
      h1={
        <>
          The GRID alternative.
          <br />
          <span className="seo-grad">Build on book props today.</span>
        </>
      }
      lede="GRID is known for official, high-fidelity esports data partnerships. If your product needs DFS book props and odds with a key you can create now, KashRock is the self-serve alternative — free Sandbox, published plans, canonical IDs."
      compareTitle="KashRock vs GRID (builder lens)"
      headers={["", "GRID", "KashRock"]}
      rows={[
        ["Access model", "Partnership / enterprise-led", "Self-serve instant key"],
        ["Pricing", "Not a public indie menu", "Free tier, then $29+/mo"],
        ["DFS props", "Not the primary surface", "PrizePicks, Underdog, Betr, Sleeper…"],
        ["Time to first call", "Sales / integration cycle", "Under 30 seconds"],
      ]}
      reasonsTitle="When KashRock is the better fit"
      reasons={[
        "You are shipping a props or pick'em product this month.",
        "You need transparent cost for a small team.",
        "You want book-native lines and grading IDs, not a partnership queue.",
      ]}
      related={
        <>
          See{" "}
          <a href="/sportradar-alternative" className="text-white underline">
            Sportradar
          </a>
          ,{" "}
          <a href="/abios-alternative" className="text-white underline">
            Abios
          </a>
          , and{" "}
          <a href="/esports-api-free-tier" className="text-white underline">
            free tier
          </a>
          .
        </>
      }
    />
  )
}

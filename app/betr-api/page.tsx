import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import { BETR_DESCRIPTION, BETR_FAQS, BETR_TITLE } from "@/lib/seo/book-api-copy"
import { LIVE_BETR } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: BETR_TITLE },
  description: BETR_DESCRIPTION,
  alternates: { canonical: "/betr-api" },
}

export default function BetrApiPage() {
  return (
    <BookApiPage
      brand="Betr"
      h1Line2="Betr Picks props, normalized."
      lede={
        <>
          KashRock ingests Betr Picks lines and serves them in one schema. Pull Betr CS2, LoL, and Dota
          player props with an instant key from{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props</code>, filtered by book.
        </>
      }
      bullets={[
        "Player, stat type, line, direction, team, canonical propId.",
        "CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, Deadlock on one schema.",
        "Same propId across Betr, PrizePicks, Underdog & Sleeper.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=betr"
      samplePath={LIVE_BETR.path}
      sample={LIVE_BETR.sample}
      faqs={BETR_FAQS}
      jsonLdName="KashRock — Betr props via API"
      related={
        <p>
          Full board on the{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          ; compare lines on the{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Betr. Publicly available lines, normalized for informational use."
    />
  )
}

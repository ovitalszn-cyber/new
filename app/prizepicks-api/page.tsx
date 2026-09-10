import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import {
  PRIZEPICKS_DESCRIPTION,
  PRIZEPICKS_FAQS,
  PRIZEPICKS_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_PRIZEPICKS } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: PRIZEPICKS_TITLE },
  description: PRIZEPICKS_DESCRIPTION,
  alternates: { canonical: "/prizepicks-api" },
}

export default function PrizePicksApiPage() {
  return (
    <BookApiPage
      brand="PrizePicks"
      h1Line2="Normalized player props, one endpoint."
      lede={
        <>
          PrizePicks has no official public API — so KashRock ingests the lines for you and serves them
          normalized. Pull PrizePicks CS2, LoL, and Dota player props with an instant key from{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props</code>, filtered by book. No
          scraping, no broken selectors.
        </>
      }
      bullets={[
        "Player, stat type, line, direction, team, and canonical propId per prop.",
        "CS2, LoL, Dota 2, Valorant — one schema across every title.",
        "Same propId across PrizePicks, Underdog, Betr & Sleeper for line comparison.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=prizepicks"
      samplePath={LIVE_PRIZEPICKS.path}
      sample={LIVE_PRIZEPICKS.sample}
      faqs={PRIZEPICKS_FAQS}
      jsonLdName="KashRock — PrizePicks props via API"
      related={
        <p>
          Comparing books? See the{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          . Building a slip tool? The{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by PrizePicks. We expose publicly available lines in a normalized schema for informational and analytical use."
    />
  )
}

import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import {
  PARLAYPLAY_DESCRIPTION,
  PARLAYPLAY_FAQS,
  PARLAYPLAY_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_PARLAYPLAY } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: PARLAYPLAY_TITLE },
  description: PARLAYPLAY_DESCRIPTION,
  alternates: { canonical: "/parlayplay-api" },
}

export default function ParlayPlayApiPage() {
  return (
    <BookApiPage
      brand="ParlayPlay"
      h1Line2="Cross-game esports props, one endpoint."
      lede={
        <>
          ParlayPlay has no official public props API — KashRock ingests the board and serves it
          normalized. Pull ParlayPlay CS2, Valorant, LoL, and Dota 2 player props with{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props?book=parlayplay</code>. No
          scraping.
        </>
      }
      bullets={[
        "Player, stat type, line, direction, team, and canonical propId per prop.",
        "Same schema as PrizePicks, Underdog, Betr, Sleeper, Boom, and Pick6.",
        "Live boards refreshed from the ParlayPlay offering feed.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=parlayplay"
      samplePath={LIVE_PARLAYPLAY.path}
      sample={LIVE_PARLAYPLAY.sample}
      faqs={PARLAYPLAY_FAQS}
      jsonLdName="KashRock — ParlayPlay props via API"
      related={
        <p>
          Full DFS board:{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          . PrizePicks next door:{" "}
          <a href="/prizepicks-api" className="text-white underline">
            PrizePicks API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by ParlayPlay. We expose publicly available lines in a normalized schema for informational and analytical use."
    />
  )
}

import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import { BOOM_DESCRIPTION, BOOM_FAQS, BOOM_TITLE } from "@/lib/seo/book-api-copy"
import { LIVE_BOOM } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: BOOM_TITLE },
  description: BOOM_DESCRIPTION,
  alternates: { canonical: "/boom-api" },
}

export default function BoomApiPage() {
  return (
    <BookApiPage
      brand="Boom"
      h1Line2="Fantasy multiline props, one endpoint."
      lede={
        <>
          Boom has no official public props API — KashRock ingests the board and serves it normalized.
          Pull Boom CS2, LoL, and Valorant player props with{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props?book=boom</code>. No scraping.
        </>
      }
      bullets={[
        "Player, stat type, line, direction, team, and canonical propId per prop.",
        "Same schema as PrizePicks, Underdog, Betr, Sleeper, and Pick6.",
        "Live multiline boards refreshed from the Boom app feed.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=boom"
      samplePath={LIVE_BOOM.path}
      sample={LIVE_BOOM.sample}
      faqs={BOOM_FAQS}
      jsonLdName="KashRock — Boom Fantasy props via API"
      related={
        <p>
          Full DFS board:{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          . Pick6 next door:{" "}
          <a href="/pick6-api" className="text-white underline">
            Pick6 API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Boom Fantasy. We expose publicly available lines in a normalized schema for informational and analytical use."
    />
  )
}

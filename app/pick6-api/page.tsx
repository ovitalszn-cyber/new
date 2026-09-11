import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import { PICK6_DESCRIPTION, PICK6_FAQS, PICK6_TITLE } from "@/lib/seo/book-api-copy"
import { LIVE_PICK6 } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: PICK6_TITLE },
  description: PICK6_DESCRIPTION,
  alternates: { canonical: "/pick6-api" },
}

export default function Pick6ApiPage() {
  return (
    <BookApiPage
      brand="Pick6"
      h1Line2="DraftKings Pick6 props, normalized."
      lede={
        <>
          DraftKings Pick6 has no official public props API — KashRock ingests the public board and serves it
          normalized. Pull Pick6 esports props with{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props?book=pick6</code>. No scraping.
        </>
      }
      bullets={[
        "LoL kills, assists, and creep score (Maps 1–3) with player, line, and direction.",
        "Same prop schema as every other DFS book on KashRock.",
        "Canonical propId ready for joins and history lookups.",
      ]}
      endpointLabel="GET /v6/esports/lol/props?book=pick6"
      samplePath={LIVE_PICK6.path}
      sample={LIVE_PICK6.sample}
      faqs={PICK6_FAQS}
      jsonLdName="KashRock — DraftKings Pick6 props via API"
      related={
        <p>
          Full DFS board:{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          . Boom multiline:{" "}
          <a href="/boom-api" className="text-white underline">
            Boom API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by DraftKings or Pick6. We expose publicly available lines in a normalized schema for informational and analytical use."
    />
  )
}

import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import {
  POLYMARKET_DESCRIPTION,
  POLYMARKET_FAQS,
  POLYMARKET_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_POLYMARKET } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: POLYMARKET_TITLE },
  description: POLYMARKET_DESCRIPTION,
  alternates: { canonical: "/polymarket-api" },
}

export default function PolymarketApiPage() {
  return (
    <BookApiPage
      brand="Polymarket"
      h1Line2="Crowd-priced mainlines for accurate models."
      lede={
        <>
          We pull Polymarket esports match and map markets into one normalized feed with sportsbooks and DFS.
          Crowd-priced mainlines give your model a probability anchor when a single book is stale or skewed:{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props?book=polymarket</code> and consensus{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/lines</code>.
        </>
      }
      bullets={[
        "Match and map markets as odds and implied probability.",
        "Joins cleanly with Kalshi and Thunderpick on the /lines consensus path.",
        "Hardens projections with live prediction-market prices — not guesses.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=polymarket"
      samplePath={LIVE_POLYMARKET.path}
      sample={LIVE_POLYMARKET.sample}
      faqs={POLYMARKET_FAQS}
      jsonLdName="KashRock — Polymarket esports markets via API"
      related={
        <p>
          Pair with{" "}
          <a href="/kalshi-api" className="text-white underline">
            Kalshi API
          </a>{" "}
          and{" "}
          <a href="/thunderpick-api" className="text-white underline">
            Thunderpick API
          </a>
          . Odds hub:{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Polymarket. We expose publicly available market data in a normalized schema for informational and analytical use."
    />
  )
}

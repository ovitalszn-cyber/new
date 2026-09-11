import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import {
  THUNDERPICK_DESCRIPTION,
  THUNDERPICK_FAQS,
  THUNDERPICK_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_THUNDERPICK } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: THUNDERPICK_TITLE },
  description: THUNDERPICK_DESCRIPTION,
  alternates: { canonical: "/thunderpick-api" },
}

export default function ThunderpickApiPage() {
  return (
    <BookApiPage
      brand="Thunderpick"
      h1Line2="Sportsbook mainlines for sharper models."
      lede={
        <>
          Pull Thunderpick esports moneylines, map markets, and player props in the same schema as DFS books.
          Pair sportsbook prices with Kalshi and Polymarket so your model isn&apos;t anchored to one venue:{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props?book=thunderpick</code> and consensus{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/lines</code>.
        </>
      }
      bullets={[
        "Match and map winners, totals, handicaps, plus player props where listed.",
        "Normalized odds and lines next to prediction-market mainlines.",
        "Feeds model priors with live sportsbook prices — not a single-book scrape.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=thunderpick"
      samplePath={LIVE_THUNDERPICK.path}
      sample={LIVE_THUNDERPICK.sample}
      faqs={THUNDERPICK_FAQS}
      jsonLdName="KashRock — Thunderpick esports lines via API"
      related={
        <p>
          Consensus product:{" "}
          <a href="/esports-consensus-api" className="text-white underline">
            esports consensus API
          </a>
          . Prediction markets:{" "}
          <a href="/kalshi-api" className="text-white underline">
            Kalshi API
          </a>
          ,{" "}
          <a href="/polymarket-api" className="text-white underline">
            Polymarket API
          </a>
          . Line shopping:{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Thunderpick. We expose publicly available lines in a normalized schema for informational and analytical use."
    />
  )
}

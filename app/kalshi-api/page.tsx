import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import { KALSHI_DESCRIPTION, KALSHI_FAQS, KALSHI_TITLE } from "@/lib/seo/book-api-copy"
import { LIVE_KALSHI } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: KALSHI_TITLE },
  description: KALSHI_DESCRIPTION,
  alternates: { canonical: "/kalshi-api" },
}

export default function KalshiApiPage() {
  return (
    <BookApiPage
      brand="Kalshi"
      h1Line2="Prediction-market mainlines for better models."
      lede={
        <>
          We pull Kalshi esports match and map markets into the same normalized schema as sportsbooks and DFS
          books. Use prediction-market probabilities as a clean prior so your model stays calibrated:{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props?book=kalshi</code> and consensus{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/lines</code>.
        </>
      }
      bullets={[
        "Match/map mainlines as probabilities and American odds.",
        "Same prop shape as Thunderpick and Polymarket for cross-venue joins.",
        "Helps models avoid single-venue bias when sportsbook lines skew.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=kalshi"
      samplePath={LIVE_KALSHI.path}
      sample={LIVE_KALSHI.sample}
      faqs={KALSHI_FAQS}
      jsonLdName="KashRock — Kalshi esports markets via API"
      related={
        <p>
          Also on the consensus feed:{" "}
          <a href="/polymarket-api" className="text-white underline">
            Polymarket API
          </a>{" "}
          and{" "}
          <a href="/thunderpick-api" className="text-white underline">
            Thunderpick API
          </a>
          . Docs:{" "}
          <a href="/docs/endpoints/lines" className="text-white underline">
            /lines
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Kalshi. We expose publicly available market data in a normalized schema for informational and analytical use."
    />
  )
}

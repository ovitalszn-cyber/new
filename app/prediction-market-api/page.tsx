import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { PREDICTION_MARKET_REF } from "@/lib/seo/prediction-market"

export const metadata: Metadata = {
  title: { absolute: PREDICTION_MARKET_REF.title },
  description: PREDICTION_MARKET_REF.description,
  keywords: PREDICTION_MARKET_REF.keywords,
  alternates: { canonical: PREDICTION_MARKET_REF.path },
  openGraph: {
    title: PREDICTION_MARKET_REF.title,
    description: PREDICTION_MARKET_REF.description,
    url: `https://www.kashrock.com${PREDICTION_MARKET_REF.path}`,
    siteName: "KashRock",
  },
}

export default function PredictionMarketApiPage() {
  return <SportReferencePage content={PREDICTION_MARKET_REF} />
}

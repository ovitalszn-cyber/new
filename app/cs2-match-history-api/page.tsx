import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { CS2_MATCH_HISTORY_REF } from "@/lib/seo/cs2-match-history"

export const metadata: Metadata = {
  title: { absolute: CS2_MATCH_HISTORY_REF.title },
  description: CS2_MATCH_HISTORY_REF.description,
  keywords: CS2_MATCH_HISTORY_REF.keywords,
  alternates: { canonical: CS2_MATCH_HISTORY_REF.path },
  openGraph: {
    title: CS2_MATCH_HISTORY_REF.title,
    description: CS2_MATCH_HISTORY_REF.description,
    url: `https://www.kashrock.com${CS2_MATCH_HISTORY_REF.path}`,
    siteName: "KashRock",
  },
}

export default function Cs2MatchHistoryApiPage() {
  return <SportReferencePage content={CS2_MATCH_HISTORY_REF} />
}

import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { VAL_REF } from "@/lib/seo/sports/valorant"

export const metadata: Metadata = {
  title: { absolute: VAL_REF.title },
  description: VAL_REF.description,
  keywords: VAL_REF.keywords,
  alternates: { canonical: VAL_REF.path },
  openGraph: {
    title: VAL_REF.title,
    description: VAL_REF.description,
    url: `https://www.kashrock.com${VAL_REF.path}`,
    siteName: "KashRock",
  },
}

export default function ValorantApiPage() {
  return <SportReferencePage content={VAL_REF} />
}

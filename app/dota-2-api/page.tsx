import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { DOTA_REF } from "@/lib/seo/sports/dota2"

export const metadata: Metadata = {
  title: { absolute: DOTA_REF.title },
  description: DOTA_REF.description,
  keywords: DOTA_REF.keywords,
  alternates: { canonical: DOTA_REF.path },
  openGraph: {
    title: DOTA_REF.title,
    description: DOTA_REF.description,
    url: `https://www.kashrock.com${DOTA_REF.path}`,
    siteName: "KashRock",
  },
}

export default function Dota2ApiPage() {
  return <SportReferencePage content={DOTA_REF} />
}

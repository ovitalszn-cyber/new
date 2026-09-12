import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { CS2_REF } from "@/lib/seo/sports/cs2"

export const metadata: Metadata = {
  title: { absolute: CS2_REF.title },
  description: CS2_REF.description,
  keywords: CS2_REF.keywords,
  alternates: { canonical: CS2_REF.path },
  openGraph: {
    title: CS2_REF.title,
    description: CS2_REF.description,
    url: `https://www.kashrock.com${CS2_REF.path}`,
    siteName: "KashRock",
  },
}

export default function Cs2ApiPage() {
  return <SportReferencePage content={CS2_REF} />
}

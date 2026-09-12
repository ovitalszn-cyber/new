import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { LOL_REF } from "@/lib/seo/sports/lol"

export const metadata: Metadata = {
  title: { absolute: LOL_REF.title },
  description: LOL_REF.description,
  keywords: LOL_REF.keywords,
  alternates: { canonical: LOL_REF.path },
  openGraph: {
    title: LOL_REF.title,
    description: LOL_REF.description,
    url: `https://www.kashrock.com${LOL_REF.path}`,
    siteName: "KashRock",
  },
}

export default function LeagueOfLegendsApiPage() {
  return <SportReferencePage content={LOL_REF} />
}

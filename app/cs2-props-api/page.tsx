import type { Metadata } from "next"

import { SportReferencePage } from "@/components/seo/SportReferencePage"
import { CS2_REF } from "@/lib/seo/sports/cs2"

const PROPS_REF = {
  ...CS2_REF,
  path: "/cs2-props-api",
  title: "CS2 Player Props API — Live Kills, Headshots & Map Lines | KashRock",
  description:
    "CS2 player props API: live kills, headshots, and map-scoped lines across PrizePicks, Underdog, Betr & Sleeper. Canonical propIds, instant key, free Sandbox.",
  keywords: [
    "CS2 player props API",
    "CS2 props API",
    "CS2 kills API",
    "PrizePicks CS2 props",
    "CS2 DFS API",
  ],
  jsonLdName: "KashRock CS2 Player Props API",
}

export const metadata: Metadata = {
  title: { absolute: PROPS_REF.title },
  description: PROPS_REF.description,
  keywords: PROPS_REF.keywords,
  alternates: { canonical: PROPS_REF.path },
  openGraph: {
    title: PROPS_REF.title,
    description: PROPS_REF.description,
    url: `https://www.kashrock.com${PROPS_REF.path}`,
    siteName: "KashRock",
  },
}

export default function Cs2PropsApiPage() {
  return <SportReferencePage content={PROPS_REF} />
}

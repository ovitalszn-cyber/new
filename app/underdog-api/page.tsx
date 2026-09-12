import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import {
  UNDERDOG_DESCRIPTION,
  UNDERDOG_FAQS,
  UNDERDOG_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_UNDERDOG } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: UNDERDOG_TITLE },
  description: UNDERDOG_DESCRIPTION,
  alternates: { canonical: "/underdog-api" },
}

export default function UnderdogApiPage() {
  return (
    <BookApiPage
      brand="Underdog"
      h1Line2="Underdog props, normalized."
      lede={
        <>
          No official Underdog Fantasy API exists — KashRock ingests the lines and serves them clean.
          Pull Underdog CS2, LoL, and Dota player props with an instant key from{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props</code>, filtered by book.
        </>
      }
      bullets={[
        "Player, stat type, line, direction, team, canonical propId.",
        "CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, Deadlock on one schema.",
        "Same propId across Underdog, PrizePicks, Betr & Sleeper.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=underdog"
      samplePath={LIVE_UNDERDOG.path}
      sample={LIVE_UNDERDOG.sample}
      faqs={UNDERDOG_FAQS}
      jsonLdName="KashRock — Underdog props via API"
      related={
        <p>
          Compare across books on the{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          , or see the{" "}
          <a href="/prizepicks-api" className="text-white underline">
            PrizePicks API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Underdog Fantasy. Publicly available lines, normalized for informational use."
    />
  )
}

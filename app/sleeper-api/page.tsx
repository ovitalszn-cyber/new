import type { Metadata } from "next"

import { BookApiPage } from "@/components/seo/BookApiPage"
import {
  SLEEPER_DESCRIPTION,
  SLEEPER_FAQS,
  SLEEPER_TITLE,
} from "@/lib/seo/book-api-copy"
import { LIVE_SLEEPER } from "@/lib/seo/live-book-props"

export const metadata: Metadata = {
  title: { absolute: SLEEPER_TITLE },
  description: SLEEPER_DESCRIPTION,
  alternates: { canonical: "/sleeper-api" },
}

export default function SleeperApiPage() {
  return (
    <BookApiPage
      brand="Sleeper"
      h1Line2="Sleeper Picks props, normalized."
      lede={
        <>
          KashRock ingests Sleeper Picks lines and serves them in one schema. Pull Sleeper CS2, LoL, and
          Dota player props with an instant key from{" "}
          <code className="text-white">GET /v6/esports/{"{sport}"}/props</code>, filtered by book — no
          scraping.
        </>
      }
      bullets={[
        "Player, stat type, line, direction, team, canonical propId.",
        "CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, Deadlock on one schema.",
        "Same propId across Sleeper, PrizePicks, Underdog & Betr.",
      ]}
      endpointLabel="GET /v6/esports/cs2/props?book=sleeper"
      samplePath={LIVE_SLEEPER.path}
      sample={LIVE_SLEEPER.sample}
      faqs={SLEEPER_FAQS}
      jsonLdName="KashRock — Sleeper props via API"
      related={
        <p>
          See the{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>{" "}
          for the full board, or compare on the{" "}
          <a href="/esports-odds-api" className="text-white underline">
            esports odds API
          </a>
          .
        </p>
      }
      disclaimer="KashRock is an independent data provider and is not affiliated with, endorsed by, or sponsored by Sleeper. Publicly available lines, normalized for informational use."
    />
  )
}

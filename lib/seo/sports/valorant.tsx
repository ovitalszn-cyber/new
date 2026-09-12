import type { SportRefContent } from "@/components/seo/SportReferencePage"
import { RefBullets, RefCallout } from "@/components/seo/reference"

const SAMPLE = {
  source: "kashrock",
  sport: "valorant",
  props: [
    {
      propId: "kr_prop_0c5a6d27fce7",
      player_name: "Any Questions Gaming",
      stat_type: "VAL_MAP_HANDICAP",
      line: -1.5,
      odds: -102,
      direction: "away",
      team: "Any Questions Gaming",
      book_name: "Polymarket",
      event_time: "2026-09-12T09:00:00.000Z",
    },
  ],
}

export const VAL_REF: SportRefContent = {
  path: "/valorant-api",
  title: "Valorant API — Odds, Match Data & Normalized Markets | KashRock",
  description:
    "Valorant API for developers: live Valorant match markets, handicaps, schedules, and canonical IDs across sportsbooks and prediction markets. Instant key, transparent pricing.",
  keywords: [
    "Valorant API",
    "Valorant odds API",
    "Valorant props API",
    "VLR API alternative",
    "Valorant esports API",
  ],
  jsonLdName: "KashRock Valorant API",
  h1: (
    <>
      Valorant API.
      <br />
      <span className="seo-grad">Markets and IDs without stitching VLR to books.</span>
    </>
  ),
  lede:
    "Valorant tooling usually means one scrape for VLR stats and another for book odds — then a fragile name join in the middle. A Valorant API should give you normalized markets and match structure first, and only claim player-prop depth when the books actually post it.",
  toc: [
    { id: "why", label: "Why a Valorant API needs a schema" },
    { id: "schema", label: "What we normalize today" },
    { id: "endpoints", label: "Core Valorant endpoints" },
    { id: "ids", label: "Canonical IDs" },
    { id: "sample", label: "Sample live Valorant market" },
    { id: "sources", label: "Comparing Valorant sources" },
    { id: "grading", label: "Settlement patterns" },
    { id: "ops", label: "Operational practices" },
    { id: "quick", label: "Quick reference" },
  ],
  samplePath: "/v6/esports/valorant/props",
  sample: SAMPLE,
  endpointRows: [
    ["GET /v6/esports/valorant/props", "Live markets / props when listed", "book, market"],
    ["GET /v6/esports/valorant/matches", "Schedule / live / completed", "status, dates"],
    ["GET /v6/esports/valorant/lines", "Consensus odds (Hobby+)", "—"],
    ["GET /v6/esports/valorant/players/{slug}/gamelogs", "Map history when available", "limit"],
  ],
  fieldRows: [
    ["propId", "kr_prop_0c5a6d27fce7", "Stable market key"],
    ["stat_type", "VAL_MAP_HANDICAP", "Sport-prefixed market"],
    ["line", "-1.5", "Handicap / total threshold"],
    ["book_name", "Polymarket", "Venue"],
  ],
  sourceRows: [
    ["VLR", "Strong competitive stats", "KPR / agents — not book lines"],
    ["Single-book scrape", "One venue, brittle", "Prototypes"],
    ["KashRock Valorant API", "Normalized markets + IDs", "Odds, schedules, models"],
  ],
  faqs: [
    {
      q: "Does the Valorant API include PrizePicks player props?",
      a: "Only when those books list Valorant on their board. If the DFS venue has no Valorant props, KashRock returns an empty props list for that book — we do not invent lines.",
    },
    {
      q: "What Valorant markets are available?",
      a: "Sportsbook and prediction-market mainlines (match/map, handicaps, totals) when listed, plus schedules and consensus lines on Hobby+.",
    },
    {
      q: "How do you handle VLR vs book identity?",
      a: "Canonical player and team IDs sit under the display name. Metrics sources dual-index so nickname-only joins are not required.",
    },
  ],
  relatedLinks: [
    { href: "/cs2-api", label: "CS2 API" },
    { href: "/esports-odds-api", label: "Esports odds API" },
    { href: "/esports-consensus-api", label: "Consensus lines" },
    { href: "/esports-api-pricing", label: "Pricing" },
  ],
  sections: {
    why: (
      <>
        <p>
          VLR is excellent for competitive metrics. It is not a book feed. If your product needs
          odds, you still need a normalized market layer with stable IDs.
        </p>
        <RefCallout>
          if a DFS book has no Valorant board today, the honest API response is empty for that book
          — not a hallucinated kill line.
        </RefCallout>
      </>
    ),
    schema: (
      <p>
        Match/series structure, sport-prefixed market keys (
        <code className="text-zinc-200">VAL_*</code>), and canonical entities. Player-prop depth
        appears when venues list it; mainlines and handicaps are the reliable baseline.
      </p>
    ),
    endpoints: (
      <p>
        Paths under <code className="text-zinc-200">/v6/esports/valorant/</code>. Same client as CS2
        and LoL.
      </p>
    ),
    ids: (
      <RefBullets
        items={[
          <>canonical_event_id / matchup_key for series joins</>,
          <>VAL_* market keys</>,
          <>Dual-index metrics identity — not nickname-only</>,
        ]}
      />
    ),
    sample: (
      <p>
        Live Polymarket Valorant market from production (example when DFS books are dark on the
        title).
      </p>
    ),
    sources: (
      <p>
        Use VLR for KPR-style metrics. Use KashRock when you need book-native markets and schedules
        on one schema.
      </p>
    ),
    grading: (
      <p>
        Settle map markets from finalized match results. For player props, only grade when the
        venue actually offered the line and the map record exists.
      </p>
    ),
    ops: (
      <RefBullets
        items={[
          <>Check coverage per book before assuming DFS depth</>,
          <>Use /lines on Hobby+ for consensus fair odds</>,
          <>Cache completed matches longer than live boards</>,
        ]}
      />
    ),
    quick: (
      <p>
        <code className="text-zinc-200">GET /v6/esports/valorant/props</code> for listed markets,{" "}
        <code className="text-zinc-200">/matches</code> for schedule,{" "}
        <code className="text-zinc-200">/lines</code> for consensus. Transparent pricing.
      </p>
    ),
  },
}

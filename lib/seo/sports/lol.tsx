import type { SportRefContent } from "@/components/seo/SportReferencePage"
import { RefBullets, RefCallout, RefSub } from "@/components/seo/reference"

const SAMPLE = {
  source: "kashrock",
  sport: "lol",
  props: [
    {
      propId: "kr_prop_a6f1a6866b31",
      player_name: "Faker",
      stat_type: "LOL_KILLS_MAPS_1_3",
      line: 9.5,
      odds: -137,
      direction: "over",
      team: "T1",
      book_name: "PrizePicks",
      event_time: "2026-09-12T05:00:00.000Z",
    },
  ],
}

export const LOL_REF: SportRefContent = {
  path: "/league-of-legends-api",
  title: "League of Legends API — Player Props & Match Data | KashRock",
  description:
    "League of Legends API for developers: live LoL player props, kills lines, schedules, and canonical IDs across DFS books and sportsbooks. Instant key — no enterprise quote.",
  keywords: [
    "League of Legends API",
    "LoL API",
    "LoL player props API",
    "League of Legends props API",
    "PrizePicks LoL API",
  ],
  jsonLdName: "KashRock League of Legends API",
  h1: (
    <>
      League of Legends API.
      <br />
      <span className="seo-grad">Props and IDs built for production joins.</span>
    </>
  ),
  lede:
    "LoL boards fragment the same way CS2 does — every book spells the player differently, map scope hides in the market string, and yesterday's line disappears from the app. A League of Legends API that only returns free-text names forces you to rebuild identity on every request.",
  toc: [
    { id: "why", label: "Why a LoL API needs a schema" },
    { id: "schema", label: "Series, maps, and kill lines" },
    { id: "endpoints", label: "Core League of Legends endpoints" },
    { id: "ids", label: "Canonical IDs" },
    { id: "sample", label: "Sample live LoL prop" },
    { id: "sources", label: "Comparing LoL data sources" },
    { id: "grading", label: "Prop verification" },
    { id: "ops", label: "Operational practices" },
    { id: "quick", label: "Quick reference" },
  ],
  samplePath: "/v6/esports/lol/props",
  sample: SAMPLE,
  endpointRows: [
    ["GET /v6/esports/lol/props", "Live player props", "book, market"],
    ["GET /v6/esports/lol/matches", "Schedule / live / completed", "status, dates"],
    ["GET /v6/esports/lol/players/{slug}/gamelogs", "Map history", "limit"],
    ["GET /v6/esports/lol/lines", "Consensus odds (Hobby+)", "—"],
  ],
  fieldRows: [
    ["propId", "kr_prop_a6f1a6866b31", "Stable contract key"],
    ["stat_type", "LOL_KILLS_MAPS_1_3", "Sport-prefixed market"],
    ["line", "9.5", "DFS threshold"],
    ["book_name", "PrizePicks", "Venue"],
  ],
  sourceRows: [
    ["Riot / community scrapes", "ToS and breakage risk", "Personal projects"],
    ["Stats sites", "Results, not book lines", "Post-match analysis"],
    ["KashRock LoL API", "Normalized props + IDs", "Pick'ems, models, grading"],
  ],
  faqs: [
    {
      q: "Does the League of Legends API include DFS props?",
      a: "Yes. Live LoL player props from PrizePicks and other listed books, normalized onto one propId with sport-prefixed stat types.",
    },
    {
      q: "Is LoL on the free Sandbox tier?",
      a: "Sandbox focuses on CS2 for schema verification. LoL and full multi-sport boards start on paid plans from $29/mo — see esports API pricing.",
    },
    {
      q: "How do map-scoped LoL kill lines work?",
      a: "Stat types encode scope (e.g. LOL_KILLS_MAPS_1_3) so you never guess whether a line is map 1 or a series aggregate.",
    },
  ],
  relatedLinks: [
    { href: "/cs2-api", label: "CS2 API" },
    { href: "/dota-2-api", label: "Dota 2 API" },
    { href: "/valorant-api", label: "Valorant API" },
    { href: "/esports-api-pricing", label: "Pricing" },
  ],
  sections: {
    why: (
      <>
        <p>
          Source fragmentation, roster moves, and vanishing DFS boards are the default for League
          of Legends tooling. Without a schema, every dashboard becomes a one-off parser.
        </p>
        <RefCallout>
          normalize player and team IDs before you chart anything — display names are an output, not
          a join key.
        </RefCallout>
      </>
    ),
    schema: (
      <>
        <p>
          Treat the series as the parent, maps as children, and book props as offers joined by
          canonical event + player IDs. Kill lines must carry map scope in{" "}
          <code className="text-zinc-200">stat_type</code>, not in free text.
        </p>
        <RefSub id="parent-child" title="Parent and child rows">
          <p>
            Series timing and status live on the match. Map gamelogs carry the K/D/A you grade.
            Props carry the line the book posted that day.
          </p>
        </RefSub>
      </>
    ),
    endpoints: (
      <p>
        Production paths live under <code className="text-zinc-200">/v6/esports/lol/</code>. Prefer
        path-style props routes for speed.
      </p>
    ),
    ids: (
      <RefBullets
        items={[
          <>propId shared across books for the same market</>,
          <>canonical_player_id through renames</>,
          <>LOL_* stat types — never ambiguous ESPORTS_* aliases</>,
        ]}
      />
    ),
    sample: (
      <p>Live PrizePicks LoL prop from production — same envelope as CS2 and Dota.</p>
    ),
    sources: (
      <p>
        Scraping client APIs breaks. Stats sites lack book lines. A normalized League of Legends API
        is the middle that production tools actually keep.
      </p>
    ),
    grading: (
      <RefBullets
        items={[
          <>Bind propId + book + line + direction at placement</>,
          <>Resolve against finalized map gamelogs</>,
          <>Persist hit / miss / push with evidence</>,
        ]}
      />
    ),
    ops: (
      <RefBullets
        items={[
          <>Short TTL on live props; longer on completed matches</>,
          <>Filter by book when you only need one venue</>,
          <>Use history/contract for quote tape, not ad-hoc scrapes</>,
        ]}
      />
    ),
    quick: (
      <p>
        Start at <code className="text-zinc-200">GET /v6/esports/lol/props</code>, join on{" "}
        <code className="text-zinc-200">propId</code>, grade from gamelogs. Published pricing — no
        sales call.
      </p>
    ),
  },
}

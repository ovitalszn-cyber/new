import type { SportRefContent } from "@/components/seo/SportReferencePage"
import { RefBullets, RefCallout } from "@/components/seo/reference"

const SAMPLE = {
  source: "kashrock",
  sport: "dota2",
  props: [
    {
      propId: "kr_prop_97ad10b4e9db",
      player_name: "rincyq",
      stat_type: "DOTA2_KILLS_MAPS_1_2",
      line: 13.5,
      odds: -137,
      direction: "over",
      team: "Pips+4",
      book_name: "PrizePicks",
      event_time: "2026-09-12T11:00:00.000Z",
    },
  ],
}

export const DOTA_REF: SportRefContent = {
  path: "/dota-2-api",
  title: "Dota 2 API — Player Props, Kills Lines & Match Data | KashRock",
  description:
    "Dota 2 API for developers: live Dota player props, map-scoped kills, schedules, and canonical IDs across DFS books. Instant key, transparent pricing — no enterprise gate.",
  keywords: [
    "Dota 2 API",
    "Dota2 API",
    "Dota player props API",
    "Dota 2 kills API",
    "PrizePicks Dota API",
  ],
  jsonLdName: "KashRock Dota 2 API",
  h1: (
    <>
      Dota 2 API.
      <br />
      <span className="seo-grad">Map-scoped kills without the scrape tax.</span>
    </>
  ),
  lede:
    "Dota boards punish naive joins. Team tags rotate, Steam nicknames drift, and DFS kill lines are map-scoped while raw feeds blur series totals. A production Dota 2 API has to make those distinctions explicit — or your model silently grades the wrong game.",
  toc: [
    { id: "why", label: "Why a Dota 2 API needs a schema" },
    { id: "schema", label: "Series vs map kills" },
    { id: "endpoints", label: "Core Dota 2 endpoints" },
    { id: "ids", label: "Canonical IDs" },
    { id: "sample", label: "Sample live Dota prop" },
    { id: "sources", label: "Comparing Dota sources" },
    { id: "grading", label: "Prop verification" },
    { id: "ops", label: "Operational practices" },
    { id: "quick", label: "Quick reference" },
  ],
  samplePath: "/v6/esports/dota2/props",
  sample: SAMPLE,
  endpointRows: [
    ["GET /v6/esports/dota2/props", "Live player props", "book, market"],
    ["GET /v6/esports/dota2/matches", "Schedule / live / completed", "status, dates"],
    ["GET /v6/esports/dota2/players/{slug}/gamelogs", "Map history", "limit"],
    ["GET /v6/esports/dota2/lines", "Consensus odds (Hobby+)", "—"],
  ],
  fieldRows: [
    ["propId", "kr_prop_97ad10b4e9db", "Stable contract key"],
    ["stat_type", "DOTA2_KILLS_MAPS_1_2", "Map-scoped kills"],
    ["line", "13.5", "DFS threshold"],
    ["book_name", "PrizePicks", "Venue"],
  ],
  sourceRows: [
    ["DatDota / OpenDota", "Strong stats, no DFS lines", "Metrics & history"],
    ["Book scrapes", "Break often", "Fragile boards"],
    ["KashRock Dota 2 API", "Props + IDs + matches", "Tools and models"],
  ],
  faqs: [
    {
      q: "What Dota 2 props does the API return?",
      a: "Live DFS player props with sport-prefixed types like DOTA2_KILLS_MAPS_1_2, plus matches and gamelogs for grading.",
    },
    {
      q: "Do you invent map stats when Bo3 is empty?",
      a: "No. Map depth comes from proven sources. Unresolved fields stay empty rather than fabricated.",
    },
    {
      q: "Is there transparent Dota API pricing?",
      a: "Yes. Published plans from a free Sandbox (CS2 schema) and paid tiers from $29/mo — no quote wall.",
    },
  ],
  relatedLinks: [
    { href: "/cs2-api", label: "CS2 API" },
    { href: "/league-of-legends-api", label: "LoL API" },
    { href: "/esports-odds-api", label: "Odds API" },
    { href: "/esports-api-free-tier", label: "Free tier" },
  ],
  sections: {
    why: (
      <>
        <p>
          Fragmented book feeds and drifting nicknames make free-text Dota pipelines fail under
          roster churn. Schema first, then UI.
        </p>
        <RefCallout>
          never grade a maps 1–2 kill line from a series KDA dump. Scope has to live on the market
          key.
        </RefCallout>
      </>
    ),
    schema: (
      <p>
        Series parent, map children, props with explicit{" "}
        <code className="text-zinc-200">DOTA2_*</code> map scope. Team and opponent resolve through
        canonical IDs — empty string when unresolved, never a guessed org.
      </p>
    ),
    endpoints: (
      <p>
        All under <code className="text-zinc-200">/v6/esports/dota2/</code>. Same envelope as CS2 and
        LoL so one client works across titles.
      </p>
    ),
    ids: (
      <RefBullets
        items={[
          <>propId / canonical_player_id for stable joins</>,
          <>DOTA2_KILLS_MAP_* style keys only</>,
          <>matchup_key when book event IDs diverge</>,
        ]}
      />
    ),
    sample: <p>Live PrizePicks Dota prop from production.</p>,
    sources: (
      <p>
        DatDota is excellent for metrics. It is not your PrizePicks board. KashRock joins both worlds
        without making you scrape.
      </p>
    ),
    grading: (
      <RefBullets
        items={[
          <>Place against propId + line + direction</>,
          <>Settle from map gamelogs</>,
          <>Store hit / miss / push with payload evidence</>,
        ]}
      />
    ),
    ops: (
      <RefBullets
        items={[
          <>Poll live props separately from archive jobs</>,
          <>Filter ?book= when testing one venue</>,
          <>Prefer path-style sport routes</>,
        ]}
      />
    ),
    quick: (
      <p>
        <code className="text-zinc-200">GET /v6/esports/dota2/props</code> → join on propId → grade
        from gamelogs. Instant key at published prices.
      </p>
    ),
  },
}

import type { SportRefContent } from "@/components/seo/SportReferencePage"
import { RefBullets, RefCallout, RefSub } from "@/components/seo/reference"

const MATCH_SAMPLE = {
  source: "kashrock",
  sport: "cs2",
  status: "completed",
  matches: [
    {
      kr_match_id: "kr_cs2_imperial-vs-dendele-cs-11-09-2026",
      slug: "imperial-vs-dendele-cs-11-09-2026",
      status: "finished",
      event_time: "2026-09-11T20:20:00.000+00:00",
      team1: "Imperial",
      team2: "DENDELE",
      score1: 0,
      score2: 2,
      winner_id: 24956,
    },
  ],
}

const GAMELOG_SAMPLE = {
  source: "kashrock",
  player_slug: "zywoo",
  sport: "cs2",
  gamelogs: [
    {
      eventId: "evt_5b9ccf97693b8027",
      game_id: "182135",
      map_name: "Mirage",
      map_number: 2,
      begin_at: "2026-09-05T18:01:30+00:00",
      map_winner: "MOUZ",
      nickname: "ZywOo",
      team: "Vitality",
      opponent: "MOUZ",
      kills: 21,
      deaths: 14,
      assists: 2,
      headshots: 9,
      adr: 97.1,
      first_kills: 2,
    },
  ],
}

export const CS2_MATCH_HISTORY_REF: SportRefContent = {
  path: "/cs2-match-history-api",
  title: "CS2 Match History API — Series, Maps & Player Gamelogs | KashRock",
  description:
    "CS2 match history API for developers: completed series, map-level player gamelogs, canonical IDs, and prop grading inputs. Instant key — no scrape, no enterprise quote.",
  keywords: [
    "CS2 match history",
    "CS2 match history API",
    "Counter-Strike 2 match history API",
    "CS2 gamelogs API",
    "CS2 completed matches API",
  ],
  jsonLdName: "KashRock CS2 Match History API",
  h1: (
    <>
      CS2 match history API.
      <br />
      <span className="seo-grad">Series, maps, and gamelogs you can grade on.</span>
    </>
  ),
  lede:
    "You're trying to answer a simple question with messy data. A player says the line moved, your dashboard says the match never existed, and the replay you need is already gone from the easiest place to check. That's the normal state of CS2 match history work — and why treating history as a UI feature falls apart the moment you need to backtest, reconcile, or grade anything with consequences.",
  toc: [
    {
      id: "why",
      label: "Why CS2 match history needs a schema",
      children: [{ id: "why-protects", label: "What the schema layer protects" }],
    },
    {
      id: "schema",
      label: "What a CS2 match record represents",
      children: [
        { id: "parent-child", label: "Parent series and child maps" },
        { id: "dont-blur", label: "What not to blur together" },
      ],
    },
    { id: "endpoints", label: "Core match history endpoints" },
    { id: "ids", label: "Canonical IDs" },
    { id: "sample", label: "Sample JSON (live production)" },
    { id: "sources", label: "Comparing match history sources" },
    { id: "grading", label: "Prop verification from history" },
    { id: "ops", label: "Operational practices" },
    { id: "quick", label: "Quick reference" },
  ],
  samplePath: "/v6/esports/cs2/matches?status=completed&limit=1",
  sample: MATCH_SAMPLE,
  endpointRows: [
    [
      "GET /v6/esports/cs2/matches",
      "List upcoming / live / completed series",
      "status, start_date, end_date, limit, offset",
    ],
    [
      "GET /v6/esports/cs2/completed/matches",
      "Completed series board",
      "—",
    ],
    [
      "GET /v6/esports/cs2/players/{slug}/gamelogs",
      "Map-level player history",
      "limit",
    ],
    [
      "GET /v6/esports/history/contract",
      "Quote tape for a prop/book",
      "prop_id, book, market_key",
    ],
    [
      "GET /v6/esports/cs2/results",
      "Settled prop outcomes",
      "—",
    ],
  ],
  fieldRows: [
    ["kr_match_id", "kr_cs2_imperial-vs-…", "Stable series reference"],
    ["status", "finished", "Grading / cache finalization"],
    ["event_time", "ISO-8601 UTC", "Archive filters"],
    ["team1 / team2 / score*", "Imperial / DENDELE / 0-2", "Series result"],
    ["gamelogs[].map_name", "Mirage", "Map-level analysis"],
    ["gamelogs[].kills", "21", "Prop evaluation"],
    ["gamelogs[].adr", "97.1", "Secondary metrics"],
  ],
  sourceRows: [
    ["Steam in-game history", "Low–moderate", "Personal recent matches"],
    ["HLTV curated records", "High for events", "Tournament truth"],
    ["Trackers", "Varies", "Per-round dashboards"],
    ["KashRock CS2 match history API", "High by design", "Backtests, grading, models"],
  ],
  faqs: [
    {
      q: "What is a CS2 match history API?",
      a: "An API that returns completed and historical Counter-Strike 2 series plus map-level player stats (gamelogs) with stable IDs — so you can backtest and grade without scraping HLTV or Steam UIs.",
    },
    {
      q: "Does KashRock separate series from maps?",
      a: "Yes. Matches endpoints return the series container (teams, scores, status). Player gamelogs return per-map rows (map name, kills, ADR, etc.) keyed for joins.",
    },
    {
      q: "Can I grade DFS props from match history?",
      a: "Yes. Bind propId + book + line at placement, then resolve against finalized map gamelogs and results — hit, miss, or push.",
    },
    {
      q: "Is this the same as the historical quote tape?",
      a: "Related but different. Match history = what happened on the server. history/contract = what line the book posted over time. You usually need both for honest backtests.",
    },
  ],
  relatedLinks: [
    { href: "/cs2-api", label: "CS2 API" },
    { href: "/historical-esports-data-api", label: "Historical esports data" },
    { href: "/cs2-props-api", label: "CS2 props API" },
    { href: "/docs/endpoints/history", label: "History docs" },
  ],
  sections: {
    why: (
      <>
        <p>
          Many teams hit the same wall.{" "}
          <strong className="text-zinc-200">Source fragmentation</strong> — Steam, HLTV, trackers,
          and book feeds disagree on keys.{" "}
          <strong className="text-zinc-200">Roster churn</strong> — free-text joins rot.{" "}
          <strong className="text-zinc-200">Retention gaps</strong> — client history only keeps
          recent sessions. A CS2 match history API exists to turn that mess into predictable joins.
        </p>
        <RefSub id="why-protects" title="What the schema layer protects">
          <p>
            The schema does not fix upstream politics. It anchors identity, status, and timing so a
            query next month still resolves the same series and player.
          </p>
          <RefCallout>
            never let a dashboard query free-text team names across providers. Normalize first, then
            display.
          </RefCallout>
        </RefSub>
      </>
    ),
    schema: (
      <>
        <p>
          A match is not one row. It is a <strong className="text-zinc-200">series container</strong>{" "}
          with teams, start time, and one or more map children. One demo maps to one map — a BO3 can
          produce two or three map records.
        </p>
        <RefSub id="parent-child" title="Parent series and child maps">
          <p>
            Series carries winner, scores, and status. Map gamelogs carry kills, ADR, headshots, and
            map name — the fields you grade player props on.
          </p>
        </RefSub>
        <RefSub id="dont-blur" title="What not to blur together">
          <RefBullets
            items={[
              <>Do not treat match_id and map/game_id as interchangeable.</>,
              <>Do not grade map-1 kills from series score alone.</>,
              <>Do not assume a nickname is a stable join key.</>,
            ]}
          />
        </RefSub>
      </>
    ),
    endpoints: (
      <p>
        Production paths under <code className="text-zinc-200">/v6/esports/cs2/</code> plus vault
        history. Prefer explicit <code className="text-zinc-200">status</code> filters over boolean
        is_live flags.
      </p>
    ),
    ids: (
      <>
        <RefBullets
          items={[
            <>kr_match_id — stable series id</>,
            <>canonical player / team ids under display names</>,
            <>game_id / map_number on gamelog rows for map scope</>,
            <>propId when joining history to the live board</>,
          ]}
        />
        <RefCallout>
          use display names only at the edge, after the join through canonical IDs.
        </RefCallout>
      </>
    ),
    sample: (
      <>
        <p>
          Live production shapes below — completed series list, then a ZywOo map gamelog. Second
          sample path:{" "}
          <code className="text-zinc-200">
            GET /v6/esports/cs2/players/zywoo/gamelogs?limit=1
          </code>
          .
        </p>
        <pre className="mt-4 p-4 bg-[#0C0D0F] border border-white/10 rounded-sm text-xs text-zinc-300 overflow-x-auto font-mono">
          {JSON.stringify(GAMELOG_SAMPLE, null, 2)}
        </pre>
      </>
    ),
    sources: (
      <p>
        Steam for personal recent matches. HLTV for curated event truth. Trackers for round detail.
        A normalized CS2 match history API when you need one schema for backtests and grading.
      </p>
    ),
    grading: (
      <>
        <RefBullets
          items={[
            <>Bind propId + book + line + direction at placement</>,
            <>Resolve against finalized map gamelogs</>,
            <>Terminal states: hit / miss / push / unmatched</>,
          ]}
        />
        <RefCallout>
          don&apos;t grade from screenshots. Grade from the finalized map record and store evidence
          beside it.
        </RefCallout>
      </>
    ),
    ops: (
      <RefBullets
        items={[
          <>Separate live polls from archive backfills</>,
          <>Cache completed series longer than live boards</>,
          <>Stamp fetched_at on stored payloads for audits</>,
          <>Pair match history with history/contract for line tape</>,
        ]}
      />
    ),
    quick: (
      <p>
        Series → <code className="text-zinc-200">/matches</code>. Maps →{" "}
        <code className="text-zinc-200">/players/{"{slug}"}/gamelogs</code>. Lines over time →{" "}
        <code className="text-zinc-200">/history/contract</code>. Full CS2 surface:{" "}
        <a href="/cs2-api" className="text-white underline">
          CS2 API reference
        </a>
        .
      </p>
    ),
  },
}

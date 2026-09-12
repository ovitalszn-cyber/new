import type { SportRefContent } from "@/components/seo/SportReferencePage"
import { RefBullets, RefCallout, RefSub } from "@/components/seo/reference"

const SAMPLE = {
  source: "kashrock",
  sport: "cs2",
  props: [
    {
      propId: "kr_prop_14e79be2b6bc",
      player_name: "n1ssim",
      stat_type: "CS2_KILLS_MAPS_1_2",
      line: 26.5,
      odds: -137,
      direction: "over",
      team: "Legacy",
      book_name: "PrizePicks",
      event_time: "2026-09-12T06:00:00.000Z",
      links: {
        market: "https://app.prizepicks.com/?projections=14751913-o-26.5",
      },
    },
  ],
}

export const CS2_REF: SportRefContent = {
  path: "/cs2-api",
  title: "CS2 API — Player Props, Match History & Canonical IDs | KashRock",
  description:
    "CS2 API for developers: live Counter-Strike 2 player props, map-scoped kills and headshots, match history, and canonical IDs across PrizePicks, Underdog, and sportsbooks. Instant key, free Sandbox.",
  keywords: [
    "CS2 API",
    "Counter-Strike 2 API",
    "CS2 player props API",
    "CS2 match history API",
    "CS2 kills API",
    "PrizePicks CS2 API",
  ],
  jsonLdName: "KashRock CS2 API",
  h1: (
    <>
      CS2 API reference.
      <br />
      <span className="seo-grad">Props, history, and IDs that survive roster churn.</span>
    </>
  ),
  lede:
    "You're trying to answer a simple question with messy data. A player says the line moved, your dashboard says the match never existed, and the book board you need is already gone. That's the normal state of CS2 integration work — and why treating props and match history as UI scrapes falls apart the moment you need to backtest, reconcile, or grade anything with consequences.",
  toc: [
    {
      id: "why",
      label: "Why a CS2 API needs a schema",
      children: [{ id: "why-protects", label: "What the schema layer protects" }],
    },
    {
      id: "schema",
      label: "What a CS2 record actually represents",
      children: [
        { id: "parent-child", label: "Series, maps, and player lines" },
        { id: "dont-blur", label: "What not to blur together" },
      ],
    },
    { id: "endpoints", label: "Core CS2 endpoints" },
    { id: "ids", label: "Canonical IDs for players, teams, and matches" },
    { id: "sample", label: "Sample JSON for a live CS2 prop" },
    { id: "sources", label: "Comparing CS2 data sources" },
    { id: "grading", label: "Prop verification and outcome status" },
    { id: "ops", label: "Operational practices" },
    { id: "quick", label: "Quick reference" },
  ],
  samplePath: "/v6/esports/cs2/props",
  sample: SAMPLE,
  endpointRows: [
    [
      "GET /v6/esports/cs2/props",
      "Live DFS + book player props",
      "book, market, market_contains",
    ],
    [
      "GET /v6/esports/cs2/matches",
      "Schedule / live / completed series",
      "status, start_date, end_date, limit",
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
    ["GET /v6/esports/cs2/lines", "Consensus fair odds (Hobby+)", "—"],
  ],
  fieldRows: [
    ["props[].propId", "kr_prop_14e79be2b6bc", "Stable contract key across books"],
    ["props[].stat_type", "CS2_KILLS_MAPS_1_2", "Sport-prefixed, map-scoped market"],
    ["props[].line", "26.5", "Book threshold you grade against"],
    ["props[].direction", "over", "Side of the market"],
    ["props[].odds", "-137", "American price on the offer"],
    ["props[].book_name", "PrizePicks", "Venue that posted the line"],
    ["props[].event_time", "ISO-8601 UTC", "Series start for joins"],
  ],
  sourceRows: [
    ["Book app / scrape", "Fragile, no history", "Today's board only"],
    ["HLTV / trackers", "High for results, not book lines", "Post-match truth"],
    ["Raw provider feeds", "One venue, one shape", "Single-book tools"],
    ["KashRock CS2 API", "Normalized by design", "Props, models, grading, backtests"],
  ],
  faqs: [
    {
      q: "What does the KashRock CS2 API cover?",
      a: "Live player props (kills, headshots, map-scoped lines), matches, player gamelogs, history/contract quote tape, and Hobby+ consensus lines — one schema across PrizePicks, Underdog, Betr, Sleeper, Boom, Pick6, Thunderpick, Kalshi, and Polymarket.",
    },
    {
      q: "Is there a free CS2 API tier?",
      a: "Yes. Sandbox is $0/mo with an instant key for CS2 props so you can verify the schema before paying. Paid plans start at $29/mo.",
    },
    {
      q: "How are CS2 kill markets named?",
      a: "Sport-prefixed, stat-first keys like CS2_KILLS_MAP_1 and CS2_KILLS_MAPS_1_2 — not ESPORTS_* or wrong-order forms. That keeps joins stable across books.",
    },
    {
      q: "Can I grade props from match history?",
      a: "Yes. Bind the ticket to propId + book + line + direction at placement, then resolve against finalized map gamelogs and results — hit, miss, or push.",
    },
  ],
  relatedLinks: [
    { href: "/cs2-props-api", label: "CS2 player props API" },
    { href: "/esports-odds-api", label: "Esports odds API" },
    { href: "/historical-esports-data-api", label: "Historical esports data" },
    { href: "/quickstart", label: "Quickstart" },
  ],
  sections: {
    why: (
      <>
        <p>
          Many teams hit the same wall for different reasons. The first problem is{" "}
          <strong className="text-zinc-200">source fragmentation</strong> — the same CS2 event can
          appear in a DFS app, a sportsbook, HLTV, and a tracker, but none share a key you can trust
          downstream. The second is <strong className="text-zinc-200">roster churn</strong> — team
          tags and handles change often enough that free-text joins degrade. The third is{" "}
          <strong className="text-zinc-200">retention gaps</strong> — yesterday&apos;s PrizePicks
          line is gone from the app, so scrapers that worked last month fail when you need a
          backtest.
        </p>
        <RefSub id="why-protects" title="What the schema layer protects">
          <p>
            A schema does not fix upstream politics. It gives every downstream consumer one place to
            anchor identity, status, and timing — so a query next month still resolves the same
            player even if they renamed their profile.
          </p>
          <RefCallout>
            never let a dashboard query free-text team names directly from multiple providers.
            Normalize first, then display.
          </RefCallout>
          <p>
            A good CS2 API schema survives three things: roster churn, partial board coverage, and
            source disagreement. If your model can&apos;t handle all three, it&apos;s too thin for
            production.
          </p>
        </RefSub>
      </>
    ),
    schema: (
      <>
        <p>
          A lot of integrations fail because they treat a match like one row. In practice the record
          is a <strong className="text-zinc-200">series container</strong> with two teams, a start
          time, and one or more map children. Player props hang off that series with map scope
          (map 1, maps 1–2, etc.) — which is why collapsing everything into a single object makes
          grading and backtests drift.
        </p>
        <RefSub id="parent-child" title="Series, maps, and player lines">
          <p>
            Model the series as the parent, maps as children, and prop offers as book-native lines
            joined by canonical event and player IDs. Series carries overall status and timing. Maps
            carry the granular fields you grade on. Props carry the line the book actually posted.
          </p>
        </RefSub>
        <RefSub id="dont-blur" title="What not to blur together">
          <RefBullets
            items={[
              <>Do not treat match_id and map scope as interchangeable.</>,
              <>Do not grade a map-1 kill line from series totals alone.</>,
              <>Do not assume a display nickname is a stable join key.</>,
            ]}
          />
        </RefSub>
      </>
    ),
    endpoints: (
      <>
        <p>
          A normalized provider should expose endpoint families that match how developers work.
          Live boards start with props. Schedule and live products need matches. Backtests need
          gamelogs and history. The shapes below are the production KashRock paths under{" "}
          <code className="text-zinc-200">/v6/esports/cs2/</code>.
        </p>
        <p>
          Each response should stay boring for client code: the same envelope, UTC timestamps, and
          explicit status — not a pile of boolean flags that hide delayed or forfeited series.
        </p>
      </>
    ),
    ids: (
      <>
        <p>
          Identifiers decide whether historical joins stay reliable or drift apart. Steam persona
          names change, team pages get reworked after roster moves, and book labels often stop
          matching the underlying entity. KashRock mints{" "}
          <code className="text-zinc-200">kr_prop_*</code>,{" "}
          <code className="text-zinc-200">kr_pl_*</code>, and canonical event/team IDs so the join
          survives the rename.
        </p>
        <RefBullets
          items={[
            <>propId — stable contract across books for the same player/market/event</>,
            <>canonical_player_id — one person through handle changes</>,
            <>canonical_event_id / matchup_key — series join when book event IDs diverge</>,
            <>stat_type — sport-prefixed keys like CS2_KILLS_MAPS_1_2</>,
          ]}
        />
        <RefCallout>
          use display names only at the edge, after the join has been resolved through canonical
          IDs.
        </RefCallout>
      </>
    ),
    sample: (
      <>
        <p>
          A useful payload is not a raw book dump. It&apos;s a normalized object with the fields you
          need to shop lines, build pick&apos;ems, and grade later — pulled live from production,
          not invented for the docs.
        </p>
      </>
    ),
    sources: (
      <>
        <p>
          Choose your CS2 source by query shape: recent personal matches, audit-grade event records,
          or schema-normalized ingestion — instead of assuming one site covers every workflow.
        </p>
      </>
    ),
    grading: (
      <>
        <p>
          Grading a prop is a join with sharper consequences. Bind the ticket to{" "}
          <code className="text-zinc-200">propId</code>, book, line, and direction at placement,
          then resolve against finalized map stats.
        </p>
        <RefBullets
          items={[
            <>Hit / miss — the canonical map record contained the stat and the line resolved.</>,
            <>Push — the stat landed exactly on the threshold.</>,
            <>Unmatched / void — the map or player could not be found; do not invent a grade.</>,
          ]}
        />
        <RefCallout>
          don&apos;t grade from screenshots or partial text logs. Grade from the finalized map
          record, then store the raw evidence beside it.
        </RefCallout>
      </>
    ),
    ops: (
      <>
        <RefBullets
          items={[
            <>Separate live board polls from archive backfills — they fail differently.</>,
            <>Cache completed records longer; keep live boards on a short TTL.</>,
            <>Stamp objects with fetched_at and verification status for audits.</>,
            <>Prefer path-style GET /v6/esports/cs2/props over slow query-string aliases.</>,
          ]}
        />
      </>
    ),
    quick: (
      <>
        <p>
          Keep this open beside your IDE: <code className="text-zinc-200">propId</code> stays stable
          across books, <code className="text-zinc-200">stat_type</code> is sport-prefixed and
          map-scoped, timestamps are UTC, and Sandbox lets you prove the schema before you pay.
          Full route index:{" "}
          <a href="/docs/api-reference" className="text-white underline">
            docs API reference
          </a>
          .
        </p>
      </>
    ),
  },
}

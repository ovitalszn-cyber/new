import type { SportRefContent } from "@/components/seo/SportReferencePage"
import { RefBullets, RefCallout, RefSub } from "@/components/seo/reference"

const SAMPLE = {
  source: "kashrock",
  sport: "cs2",
  event_id: "kr_ev_4209ed58edd7",
  home_team: "NRG Esports",
  away_team: "Liquid",
  market: "match_winner",
  outcomes: [
    {
      name: "team liquid",
      consensus_probability: 0.61156,
      sources: [
        {
          source: "kalshi",
          type: "prediction_market",
          probability: 0.6154,
          american: -160,
        },
        {
          source: "polymarket",
          type: "prediction_market",
          probability: 0.605,
          american: -153,
        },
      ],
    },
    {
      name: "nrg",
      consensus_probability: 0.38844,
      sources: [
        {
          source: "kalshi",
          type: "prediction_market",
          probability: 0.3802,
          american: 163,
        },
        {
          source: "polymarket",
          type: "prediction_market",
          probability: 0.395,
          american: 153,
        },
      ],
    },
  ],
}

export const PREDICTION_MARKET_REF: SportRefContent = {
  path: "/prediction-market-api",
  title: "Prediction Market API for Esports — Kalshi, Polymarket & Consensus | KashRock",
  description:
    "Prediction market API for esports: normalized Kalshi and Polymarket mainlines, de-vig probabilities, and consensus with Thunderpick via GET /v6/esports/{sport}/lines. Instant key.",
  keywords: [
    "prediction market api",
    "esports prediction market api",
    "Kalshi Polymarket API",
    "prediction market odds api",
    "Kalshi esports API",
    "Polymarket esports API",
  ],
  jsonLdName: "KashRock Prediction Market API",
  h1: (
    <>
      Prediction market API.
      <br />
      <span className="seo-grad">Kalshi + Polymarket, one esports schema.</span>
    </>
  ),
  lede:
    "Prediction markets price outcomes in probability space. Sportsbooks price them in odds. If you scrape each venue separately, you rebuild de-vig and team identity forever. A prediction market API for esports should hand you normalized probabilities — and a consensus path when you want books and markets in one response.",
  toc: [
    { id: "why", label: "Why prediction markets need a schema" },
    { id: "schema", label: "What we normalize" },
    { id: "endpoints", label: "Core endpoints" },
    { id: "ids", label: "Identity and join keys" },
    { id: "sample", label: "Sample JSON (live Kalshi + Polymarket)" },
    { id: "sources", label: "Markets vs sportsbooks" },
    { id: "grading", label: "Using consensus responsibly" },
    { id: "ops", label: "Operational practices" },
    { id: "quick", label: "Quick reference" },
  ],
  samplePath: "/v6/esports/cs2/lines",
  sample: SAMPLE,
  endpointRows: [
    [
      "GET /v6/esports/{sport}/lines",
      "Consensus + per-source probs (Hobby+)",
      "sport path: cs2, lol, …",
    ],
    [
      "GET /v6/esports/{sport}/props?book=kalshi",
      "Kalshi board as normalized props",
      "book=kalshi",
    ],
    [
      "GET /v6/esports/{sport}/props?book=polymarket",
      "Polymarket board as normalized props",
      "book=polymarket",
    ],
    ["GET /v6/esports/cs2/props?book=thunderpick", "Sportsbook mainlines", "book=thunderpick"],
  ],
  fieldRows: [
    ["outcomes[].consensus_probability", "0.61156", "De-vig weighted mean"],
    ["sources[].source", "kalshi / polymarket", "Venue"],
    ["sources[].type", "prediction_market", "Venue class"],
    ["sources[].probability", "0.6154", "De-vigged source prob"],
    ["sources[].american", "-160", "American quote when present"],
    ["top_edges[].edge_pct", "1.33", "Informational EV vs consensus"],
  ],
  sourceRows: [
    ["Raw Kalshi / Polymarket APIs", "Venue-native", "Single-market bots"],
    ["Sportsbook-only odds API", "No PM probs", "Book shopping"],
    ["KashRock prediction market API", "PM + book, one schema", "Calibration & consensus"],
  ],
  faqs: [
    {
      q: "What is a prediction market API for esports?",
      a: "An API that returns Kalshi/Polymarket (and similar) esports markets as normalized probabilities and American odds, joinable to sportsbook lines on the same event identity.",
    },
    {
      q: "How do I get Kalshi and Polymarket together?",
      a: "Call GET /v6/esports/{sport}/lines on Hobby+. Each outcome lists per-source probabilities and a consensus_probability. Or filter /props?book=kalshi|polymarket for venue boards.",
    },
    {
      q: "How is consensus calculated?",
      a: "Each source is de-vigged so outcomes sum to 1.0. Consensus is a weighted mean — prediction markets default to weight 1.5 vs the sportsbook. Edge is informational, not betting advice.",
    },
    {
      q: "Is there a free tier?",
      a: "Sandbox is free for CS2 props schema checks. Consensus /lines is on Hobby+. See esports API pricing.",
    },
  ],
  relatedLinks: [
    { href: "/esports-consensus-api", label: "Consensus odds API" },
    { href: "/kalshi-api", label: "Kalshi API page" },
    { href: "/polymarket-api", label: "Polymarket API page" },
    { href: "/docs/endpoints/lines", label: "Lines docs" },
  ],
  sections: {
    why: (
      <>
        <p>
          Kalshi and Polymarket do not share team strings, contract IDs, or probability conventions
          with Thunderpick. Without a schema, every model rebuilds de-vig and fuzzy name matching.
        </p>
        <RefCallout>
          treat prediction-market probabilities as first-class inputs — convert sportsbook odds to
          the same de-vigged space before you average anything.
        </RefCallout>
      </>
    ),
    schema: (
      <>
        <p>
          We normalize match/map mainlines into a common outcome list with per-source probability,
          American/decimal where available, and volume/OI/liquidity fields when the venue provides
          them (null when not — never invented).
        </p>
        <RefSub id="parent-child" title="Props board vs consensus lines">
          <p>
            <code className="text-zinc-200">/props?book=kalshi|polymarket</code> is the venue board.{" "}
            <code className="text-zinc-200">/lines</code> is the cross-venue consensus layer
            (Hobby+).
          </p>
        </RefSub>
      </>
    ),
    endpoints: (
      <p>
        Sport path-style routes under <code className="text-zinc-200">/v6/esports/{"{sport}"}/</code>
        . Same auth header as the rest of KashRock.
      </p>
    ),
    ids: (
      <RefBullets
        items={[
          <>event_id / matchup_key for series joins across venues</>,
          <>outcome name normalized for consensus buckets</>,
          <>source + type (prediction_market vs sportsbook)</>,
        ]}
      />
    ),
    sample: (
      <p>
        Live CS2 match_winner slice with both Kalshi and Polymarket on the same event (from{" "}
        <code className="text-zinc-200">/v6/esports/cs2/lines</code>).
      </p>
    ),
    sources: (
      <p>
        Prediction markets for crowd/exchange probability. Sportsbooks for traditional prices.
        Consensus when you want both without maintaining three clients.
      </p>
    ),
    grading: (
      <>
        <p>
          Consensus edge fields are informational. Quality flags (
          <code className="text-zinc-200">unreliable</code>,{" "}
          <code className="text-zinc-200">suspect_edge</code>) exist so you can drop noisy prints —
          not so you can treat every edge as a bet.
        </p>
        <RefCallout>
          settle outcomes from finalized match results, not from a live probability tick.
        </RefCallout>
      </>
    ),
    ops: (
      <RefBullets
        items={[
          <>Prefer /lines for multi-venue reads (one request)</>,
          <>Null liquidity/OI means the venue did not publish it</>,
          <>Hobby+ required for /lines; props boards follow plan gates</>,
        ]}
      />
    ),
    quick: (
      <p>
        Board: <code className="text-zinc-200">/props?book=kalshi</code> or{" "}
        <code className="text-zinc-200">polymarket</code>. Consensus:{" "}
        <code className="text-zinc-200">/lines</code>. Deep dive:{" "}
        <a href="/esports-consensus-api" className="text-white underline">
          esports consensus API
        </a>
        .
      </p>
    ),
  },
}

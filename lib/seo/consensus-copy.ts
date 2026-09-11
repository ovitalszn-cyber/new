export const CONSENSUS_TITLE =
  "Esports Consensus Odds API — Fair Lines from Thunderpick, Kalshi & Polymarket | KashRock"
export const CONSENSUS_DESCRIPTION =
  "Esports consensus odds API for CS2, LoL, Valorant & Dota. De-vig Thunderpick, Kalshi, and Polymarket into one fair probability, then surface gated edges via GET /v6/esports/{sport}/lines."

export const CONSENSUS_FAQS = [
  {
    q: "What is an esports consensus odds API?",
    a: "It turns multiple venues into one fair probability per outcome. KashRock de-vigs Thunderpick sportsbook prices plus Kalshi and Polymarket prediction-market prices, then returns a weighted consensus and edge vs that fair number.",
  },
  {
    q: "Which endpoint returns consensus lines?",
    a: "GET /v6/esports/{sport}/lines. Pass market=match_winner, map_winner, total_maps, or map_handicap. Builder or Pro plan required.",
  },
  {
    q: "How is consensus calculated?",
    a: "Each source is de-vigged so outcomes sum to 1.0. Consensus is a weighted mean — prediction markets default to weight 1.5 vs the sportsbook. Edge is consensus × decimal − 1 (informational EV, not betting advice).",
  },
  {
    q: "Why mix sportsbooks and prediction markets?",
    a: "A single book can be stale or skewed. Kalshi and Polymarket are probability-priced; Thunderpick is a live sportsbook. Together they reduce single-venue bias and calibrate models better than one scrape.",
  },
  {
    q: "What quality gates keep bad edges out?",
    a: "Liquidity floors on Kalshi and Polymarket, at least three sources for top_edges, max disagreement of 12 points, and raw edge capped at 8%. Ranking uses confidence × liquidity × edge — not raw edge alone.",
  },
  {
    q: "Is there a free tier for /lines?",
    a: "Sandbox and Hobby cannot call /lines. Builder and Pro can. Start free on props, then upgrade when you need consensus.",
  },
] as const

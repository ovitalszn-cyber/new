export const CS2_TITLE =
  "CS2 Player Props API — Live Kills, Headshots & Map Lines | KashRock"
export const CS2_DESCRIPTION =
  "Affordable CS2 player props API. Live kills, headshots, and map-1/map-2 lines for Counter-Strike 2, normalized across PrizePicks, Underdog, Betr & Sleeper. Instant key, free tier, no enterprise quote."

export const ODDS_TITLE =
  "Esports Odds API — Normalized Lines Across Books for CS2, LoL & Dota | KashRock"
export const ODDS_DESCRIPTION =
  "Affordable esports odds API. Compare DFS books, Thunderpick sportsbook prices, and Kalshi / Polymarket prediction-market mainlines on one propId — sharper models, instant key."

export const ABIOS_TITLE =
  "The Abios Alternative — Esports Data Without Enterprise Pricing | KashRock"
export const ABIOS_DESCRIPTION =
  "Looking for an Abios alternative? KashRock gives you CS2, LoL & Dota props, lines, and stats with transparent pricing and an instant key — no sales call, no enterprise quote."

export const PANDASCORE_TITLE =
  "PandaScore Alternative — Props & Stats With No Betting-Use Block | KashRock"
export const PANDASCORE_DESCRIPTION =
  "A PandaScore alternative for developers building betting, DFS, and pick'em tools. CS2, LoL & Dota props and stats, transparent pricing, instant key — no betting-use restriction."

export const CS2_FAQS = [
  {
    q: "What CS2 stats does the props API return?",
    a: "Map-specific kills, headshots, and combined stat types like CS2_HEADSHOTS_MAPS_1_2, each with a line, direction, odds, book, team, opponent, and a canonical propId. Per-map, pro-depth lines — not just match winners.",
  },
  {
    q: "Which books are covered for CS2?",
    a: "PrizePicks, Underdog, Betr, Sleeper, Dabble, Boom, and Pick6. The same CS2 player and market share one propId across every book, so you join lines without stitching separate feeds.",
  },
  {
    q: "Is there a free CS2 API tier?",
    a: "Yes. Sandbox is $0/mo with an instant key and covers CS2 player props so you can verify the schema before paying. Paid plans start at $29/mo.",
  },
  {
    q: "Can I get map-1 and map-2 CS2 lines separately?",
    a: "Yes. Stat types are map-scoped (e.g. maps 1–2), so you can model every threshold a book offers rather than only a series total.",
  },
  {
    q: "Do I have to scrape HLTV or PrizePicks myself?",
    a: "No. KashRock ingests and normalizes the props for you. You call one path-style route and filter by book; there's no upstream scrape on the request.",
  },
] as const

export const ODDS_FAQS = [
  {
    q: "What odds format does the API return?",
    a: "American odds on every offer (e.g. -137), alongside the line, direction, book, and a canonical propId shared by the over and under so you can build both sides of a market.",
  },
  {
    q: "Can I compare lines across books?",
    a: "Yes. Every venue prices the same propId, so you read one prop and see PrizePicks, Underdog, Betr, Sleeper, Boom, Pick6, Thunderpick, Kalshi, and Polymarket side by side — the core of line shopping and model calibration.",
  },
  {
    q: "Why include Kalshi and Polymarket?",
    a: "Prediction-market mainlines are probability-priced match/map outcomes. Feeding them into a model with sportsbook and DFS lines reduces single-venue bias and improves calibration when one book is stale or skewed.",
  },
  {
    q: "Which esports titles have odds?",
    a: "CS2, League of Legends, Dota 2, and Valorant, with more titles expanding. One key covers all of them.",
  },
  {
    q: "Is there a free tier for the odds API?",
    a: "Yes. Sandbox is $0/mo with an instant key for CS2 props. LoL, Dota, and full board access start at $29/mo.",
  },
  {
    q: "Do you offer historical lines for backtesting?",
    a: "Yes. Props are indexed against player game logs, so you can pull historical lines and outcomes to build hit-rate benchmarks and validate models.",
  },
] as const

export const ABIOS_FAQS = [
  {
    q: "Is KashRock cheaper than Abios?",
    a: "KashRock publishes flat pricing: a free Sandbox tier and paid plans from $29/mo. Abios (now part of Kambi) is quote-based and enterprise-gated, typically reached through a sales process.",
  },
  {
    q: "Do I have to talk to sales to get started?",
    a: "No. You create an API key instantly and hit the sandbox in about a minute — no vetting call, no procurement form.",
  },
  {
    q: "What does KashRock cover that a data-only feed doesn't?",
    a: "DFS-book props from PrizePicks, Underdog, Betr, and Sleeper on the same schema as match and player data, plus outcome verification — useful for pick'em tools, optimizers, and bet trackers.",
  },
  {
    q: "Is KashRock a good fit for a small team or solo developer?",
    a: "Yes. It's built for indie developers and small tools that can't justify an enterprise contract — start free, scale to $249/mo without renegotiating.",
  },
] as const

export const PANDASCORE_FAQS = [
  {
    q: "Can I use KashRock for betting or DFS tools?",
    a: "Yes. KashRock is built for props, lines, and pick'em/optimizer use cases. PandaScore restricts its stats plans to non-betting usage, which blocks many indie DFS and model builds.",
  },
  {
    q: "How does pricing compare?",
    a: "KashRock publishes flat plans from a free Sandbox tier up to $249/mo. PandaScore's paid data plans are priced per videogame per month and scale up quickly for multi-title coverage.",
  },
  {
    q: "Which DFS books are included?",
    a: "PrizePicks, Underdog, Betr, Sleeper, Dabble, Boom, and Pick6 — normalized on one propId across CS2, LoL, Dota 2, and Valorant.",
  },
  {
    q: "Do I get a free tier without a betting-use restriction?",
    a: "Yes. Sandbox is $0/mo with an instant key and no non-betting-use clause blocking DFS or props tools.",
  },
] as const

export const ABIOS_COMPARE = {
  headers: ["", "Abios / Kambi", "KashRock"],
  rows: [
    ["Pricing", "Quote-based, enterprise-gated", "Published: free tier, then $29+/mo"],
    ["Onboarding", "Sales call + vetting", "Instant key, sandbox in ~60s"],
    ["DFS-book props", "Not the focus", "PrizePicks, Underdog, Betr, Sleeper"],
    ["Outcome verification", "Build your own", "Hit/miss/push built in"],
    ["Best fit", "Large sportsbooks", "Indie devs, small tools, models"],
  ],
} as const

export const PANDASCORE_COMPARE = {
  headers: ["", "PandaScore", "KashRock"],
  rows: [
    ["Betting / DFS use", "Restricted on stats plans", "Built for it"],
    ["Pricing", "Per game, per month; scales up", "Flat: free tier, then $29+/mo"],
    ["DFS-book props", "Limited", "PrizePicks, Underdog, Betr, Sleeper"],
    ["Onboarding", "Account + plan config", "Instant key, sandbox in ~60s"],
  ],
} as const

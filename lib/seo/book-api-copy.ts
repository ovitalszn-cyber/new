export const PRIZEPICKS_TITLE =
  "PrizePicks API — Pull Normalized Player Props Programmatically | KashRock"
export const PRIZEPICKS_DESCRIPTION =
  "Access PrizePicks player props through one API. Normalized CS2, LoL & Dota lines with player, stat, line, and canonical IDs. Instant key, free tier — no scraping."
export const PRIZEPICKS_FAQS = [
  {
    q: "Is there a PrizePicks API?",
    a: "PrizePicks has no official public API. KashRock ingests PrizePicks lines and exposes them in a normalized schema you can call with GET /v6/esports/{sport}/props and filter by book, so you don't scrape the PrizePicks app yourself.",
  },
  {
    q: "Which PrizePicks props are covered?",
    a: "Esports player props for CS2, League of Legends, Dota 2, and Valorant — player, stat type, line, direction, team, and a canonical propId shared across books.",
  },
  {
    q: "Is it free?",
    a: "Sandbox is $0/mo with an instant key for CS2 props. Multi-title access starts at $29/mo.",
  },
] as const

export const UNDERDOG_TITLE =
  "Underdog API — Pull Underdog Fantasy Props via One Endpoint | KashRock"
export const UNDERDOG_DESCRIPTION =
  "Access Underdog Fantasy player props through one API. Normalized CS2, LoL & Dota lines with player, stat, and canonical IDs. Instant key, free tier — no scraping."
export const UNDERDOG_FAQS = [
  {
    q: "Is there an Underdog Fantasy API?",
    a: "Underdog has no official public API. KashRock ingests Underdog lines and serves them in a normalized schema via GET /v6/esports/{sport}/props filtered by book, so you skip scraping.",
  },
  {
    q: "Which Underdog props are covered?",
    a: "Esports player props across CS2, LoL, Dota 2, and Valorant — player, stat type, line, direction, team, and a canonical propId.",
  },
  {
    q: "Can I compare Underdog vs PrizePicks lines?",
    a: "Yes. The same player and market share one canonical propId across books, so you read one prop and see Underdog next to PrizePicks, Betr, and Sleeper.",
  },
] as const

export const SLEEPER_TITLE =
  "Sleeper API — Pull Sleeper Picks Props Programmatically | KashRock"
export const SLEEPER_DESCRIPTION =
  "Access Sleeper Picks player props through one API. Normalized CS2, LoL & Dota lines with player, stat, and canonical IDs. Instant key, free tier — no scraping."
export const SLEEPER_FAQS = [
  {
    q: "Is there a Sleeper Picks API for props?",
    a: "Sleeper has no official public props API. KashRock ingests Sleeper lines and serves them normalized via GET /v6/esports/{sport}/props filtered by book.",
  },
  {
    q: "Which Sleeper props are covered?",
    a: "Esports player props for CS2, LoL, Dota 2, and Valorant — player, stat type, line, direction, team, and canonical propId.",
  },
  {
    q: "Free tier?",
    a: "Yes — $0/mo Sandbox with an instant key for CS2; multi-title from $29/mo.",
  },
] as const

export const BETR_TITLE =
  "Betr API — Pull Betr Picks Player Props via API | KashRock"
export const BETR_DESCRIPTION =
  "Access Betr Picks player props through one API. Normalized CS2, LoL & Dota lines with player, stat, and canonical IDs. Instant key, free tier — no scraping."
export const BETR_FAQS = [
  {
    q: "Is there a Betr Picks API?",
    a: "Betr has no official public props API. KashRock ingests Betr lines and serves them normalized via GET /v6/esports/{sport}/props filtered by book.",
  },
  {
    q: "Which Betr props are covered?",
    a: "Esports player props for CS2, LoL, Dota 2, and Valorant — player, stat type, line, direction, team, and canonical propId.",
  },
  {
    q: "Free tier?",
    a: "Yes — $0/mo Sandbox with an instant key; multi-title from $29/mo.",
  },
] as const

export const GUIDE_PP_TITLE =
  "How to Get PrizePicks Props with an API (Without Scraping) | KashRock"
export const GUIDE_PP_DESCRIPTION =
  "A developer guide to pulling PrizePicks player props programmatically — why scraping breaks, and how to get normalized CS2/LoL props from one endpoint with a free key."
export const GUIDE_PP_FAQS = [
  {
    q: "Can I scrape PrizePicks directly?",
    a: "You can, but the app's internal endpoints change without notice, rate-limit aggressively, and return raw un-normalized data. Most projects break within weeks. A normalized feed avoids the maintenance.",
  },
  {
    q: "What's the fastest way to get PrizePicks props?",
    a: "Call KashRock's GET /v6/esports/{sport}/props with a free key and filter by book. You get normalized rows in one request — no browser automation, no reverse-engineering.",
  },
] as const

export const GUIDE_CS2_TITLE =
  "How to Get CS2 Player Props Without Scraping HLTV | KashRock"
export const GUIDE_CS2_DESCRIPTION =
  "Pull Counter-Strike 2 player props — kills, headshots, map lines — from one normalized API instead of scraping HLTV or DFS apps. Free key, live production data."
export const GUIDE_CS2_FAQS = [
  {
    q: "Where do CS2 player props come from?",
    a: "DFS books like PrizePicks, Underdog, Betr, Sleeper, Boom, and Pick6 post them. KashRock ingests all of them and normalizes to one schema so you don't integrate each source separately.",
  },
  {
    q: "What CS2 stats can I pull?",
    a: "Map-scoped kills, headshots, and combined stat types (e.g. CS2_HEADSHOTS_MAPS_1_2), each with line, direction, odds, team, and canonical propId.",
  },
] as const

export const BOOM_TITLE =
  "Boom API — Pull Boom Fantasy Esports Props via API | KashRock"
export const BOOM_DESCRIPTION =
  "Access Boom Fantasy player props through one API. Normalized CS2, LoL & Valorant lines with player, stat, and canonical IDs. Instant key, free tier — no scraping."
export const BOOM_FAQS = [
  {
    q: "Is there a Boom Fantasy API?",
    a: "Boom has no official public props API. KashRock ingests Boom multiline boards and serves them normalized via GET /v6/esports/{sport}/props filtered by book=boom.",
  },
  {
    q: "Which Boom props are covered?",
    a: "Esports player props for CS2, LoL, Valorant, and more — player, stat type, line, direction, team, and canonical propId.",
  },
  {
    q: "Free tier?",
    a: "Yes — $0/mo Sandbox with an instant key; multi-title from $29/mo.",
  },
] as const

export const PICK6_TITLE =
  "Pick6 API — DraftKings Pick6 Esports Props via API | KashRock"
export const PICK6_DESCRIPTION =
  "Access DraftKings Pick6 player props through one API. Normalized LoL (and more) kills, assists, and CS lines with canonical IDs. Instant key — no scraping."
export const PICK6_FAQS = [
  {
    q: "Is there a DraftKings Pick6 API?",
    a: "Pick6 has no official public props API. KashRock ingests the public Pick6 board and serves it normalized via GET /v6/esports/{sport}/props filtered by book=pick6.",
  },
  {
    q: "Which Pick6 props are covered?",
    a: "Live Pick6 esports markets (e.g. LoL kills, assists, creep score on Maps 1–3) with player, line, direction, team, and canonical propId.",
  },
  {
    q: "Free tier?",
    a: "Yes — $0/mo Sandbox with an instant key; multi-title from $29/mo.",
  },
] as const

export const THUNDERPICK_TITLE =
  "Thunderpick API — Esports Main Lines & Props | KashRock"
export const THUNDERPICK_DESCRIPTION =
  "Pull Thunderpick esports moneylines, map markets, and player props in one normalized schema. Pair sportsbook prices with Kalshi and Polymarket for sharper models."
export const THUNDERPICK_FAQS = [
  {
    q: "Is there a Thunderpick API?",
    a: "Thunderpick has no official public developer API. KashRock ingests Thunderpick esports boards and serves them via GET /v6/esports/{sport}/props?book=thunderpick and consensus main lines on GET /v6/esports/{sport}/lines.",
  },
  {
    q: "What does Thunderpick add to a model?",
    a: "Sportsbook main lines (match/map winner, totals, handicaps) plus player props. Use them with prediction-market prices so your prior is anchored to both book and exchange/crowd odds.",
  },
  {
    q: "Free tier?",
    a: "Sandbox is $0/mo with an instant key. Consensus lines across Thunderpick, Kalshi, and Polymarket are on Builder+.",
  },
] as const

export const KALSHI_TITLE =
  "Kalshi API — Esports Prediction Market Odds | KashRock"
export const KALSHI_DESCRIPTION =
  "Pull Kalshi esports match and map markets as normalized probabilities and American odds. Use prediction-market mainlines to calibrate models alongside sportsbooks."
export const KALSHI_FAQS = [
  {
    q: "Is there a Kalshi esports API for builders?",
    a: "Kalshi exposes trade APIs; KashRock normalizes esports markets into the same prop schema as DFS and sportsbooks via GET /v6/esports/{sport}/props?book=kalshi, and folds them into GET /v6/esports/{sport}/lines consensus.",
  },
  {
    q: "Why pull Kalshi for modeling?",
    a: "Prediction markets price match/map outcomes in probability space. Feeding those mainlines into your model (with sportsbook odds) reduces single-venue bias and improves calibration.",
  },
  {
    q: "Free tier?",
    a: "Sandbox is $0/mo. Cross-venue consensus lines (Kalshi + Polymarket + Thunderpick) are on Builder+.",
  },
] as const

export const POLYMARKET_TITLE =
  "Polymarket API — Esports Prediction Market Odds | KashRock"
export const POLYMARKET_DESCRIPTION =
  "Pull Polymarket esports match and map markets as normalized probabilities and odds. Use crowd-priced mainlines with sportsbook data to harden your models."
export const POLYMARKET_FAQS = [
  {
    q: "Is there a Polymarket esports API?",
    a: "Polymarket publishes market data; KashRock normalizes esports events into GET /v6/esports/{sport}/props?book=polymarket and consensus GET /v6/esports/{sport}/lines alongside Kalshi and Thunderpick.",
  },
  {
    q: "Why include Polymarket in a props model?",
    a: "Crowd-priced match/map mainlines are a clean probability prior. Combining them with sportsbook and DFS lines helps models stay accurate when one venue is stale or skewed.",
  },
  {
    q: "Free tier?",
    a: "Sandbox is $0/mo. Consensus lines across Polymarket, Kalshi, and Thunderpick are on Builder+.",
  },
] as const

export const COVERAGE_TITLE = "Coverage — Esports Titles, Books & Markets | KashRock"
export const COVERAGE_DESCRIPTION =
  "KashRock coverage: CS2, LoL, Dota 2, Valorant and more — DFS books plus Thunderpick, Kalshi & Polymarket mainlines for modeling — props, matches, stats, and outcome verification."

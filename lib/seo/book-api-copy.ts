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
    a: "DFS books like PrizePicks, Underdog, Betr, and Sleeper post them. KashRock ingests all of them and normalizes to one schema so you don't integrate each source separately.",
  },
  {
    q: "What CS2 stats can I pull?",
    a: "Map-scoped kills, headshots, and combined stat types (e.g. CS2_HEADSHOTS_MAPS_1_2), each with line, direction, odds, team, and canonical propId.",
  },
] as const

export const COVERAGE_TITLE = "Coverage — Esports Titles, Books & Markets | KashRock"
export const COVERAGE_DESCRIPTION =
  "KashRock coverage: CS2, LoL, Dota 2, Valorant and more, across PrizePicks, Underdog, Betr, Sleeper, Dabble & ParlayPlay — props, matches, stats, and outcome verification."

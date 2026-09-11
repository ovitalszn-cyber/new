export const HISTORICAL_TITLE =
  "Historical Esports Data API — Quote Tape, Gamelogs & Settled Results | KashRock"
export const HISTORICAL_DESCRIPTION =
  "Stop scraping for historical esports lines. KashRock gives you vault-backed quote tape, player gamelogs, and settled results for CS2, Valorant, LoL, Dota & more — one API key, no enterprise quote."

export const HISTORICAL_FAQS = [
  {
    q: "What historical esports data does KashRock return?",
    a: "Quote tape for a prop contract (line, price, status over time), player map gamelogs (kills, deaths, assists, and sport-specific fields), and settled prop results so you can measure hit rates against what the book actually offered.",
  },
  {
    q: "Is this live scraping on every request?",
    a: "No. History endpoints read from the vault and Redis cache. Workers ingest books and match stats ahead of time — the request path does not fan out to upstream sites.",
  },
  {
    q: "Which sports have historical coverage?",
    a: "Props and results cover CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, and Deadlock where books post lines. Deep map gamelogs are strongest on CS2, Valorant, LoL, and Dota 2.",
  },
  {
    q: "Can I backtest PrizePicks or Underdog lines?",
    a: "Yes. Pull the history contract for a market_key or prop_id+book, join player gamelogs, and use the results feed for grades — without rebuilding scrapers per book.",
  },
  {
    q: "Is there a free tier to try historical endpoints?",
    a: "Yes. Sandbox is $0/mo with an instant key. Start with CS2 props and history, then upgrade when you need full sports and production volume.",
  },
] as const

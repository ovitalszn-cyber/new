export const DFS_TITLE =
  "DFS Esports API — PrizePicks & Underdog Props for CS2 & LoL | KashRock"

export const DFS_DESCRIPTION =
  "Affordable DFS esports API with an instant key. Pull PrizePicks, Underdog, Betr, and Sleeper player props for CS2 and LoL — plus Dabble and ParlayPlay — from GET /v6/esports/{sport}/props."

export const DATA_API_TITLE =
  "Esports Data API — CS2, LoL & Dota Props, Lines & Stats | KashRock"

export const DATA_API_DESCRIPTION =
  "Esports data API for CS2, League of Legends, Dota 2, and Valorant. Normalized props, lines, matches, and player stats. Free sandbox, then $29+/mo — no enterprise quote."

export const DFS_FAQS = [
  {
    q: "Does the API include PrizePicks and Underdog lines for CS2 and LoL?",
    a: "Yes. KashRock ingests PrizePicks and Underdog esports props for CS2 and League of Legends, plus Betr, Sleeper, Dabble, and ParlayPlay. Same player and market share one ID across books.",
  },
  {
    q: "Is this a PrizePicks API or an Underdog API?",
    a: "It is one DFS esports API. You call GET /v6/esports/{sport}/props and filter by book. You do not scrape PrizePicks or Underdog yourself.",
  },
  {
    q: "Can I pull LoL DFS data and CS2 player props from one key?",
    a: "Yes. One key covers CS2, LoL, Dota 2, and Valorant props. Sandbox is CS2-only; Hobby and up unlock LoL DFS data and the rest of the board.",
  },
  {
    q: "What does GET /v6/esports/{sport}/props return?",
    a: "A live ingested board: player, stat, line, book (PrizePicks, Underdog, and the others), direction, and canonical propId. No upstream scrape on that request.",
  },
] as const

export const DATA_API_FAQS = [
  {
    q: "What does an esports data API include?",
    a: "KashRock covers event schedules, player props and lines, match data, player stats, and outcome verification across CS2, LoL, Dota 2, and Valorant.",
  },
  {
    q: "Is there a free esports API tier?",
    a: "Yes. Sandbox is $0/mo with an instant key — CS2 player props so you can verify the schema. Paid plans start at $29/mo.",
  },
  {
    q: "Where do I get DFS books like PrizePicks and Underdog?",
    a: "Use the DFS Esports API page and GET /v6/esports/{sport}/props. That route is the PrizePicks / Underdog / LoL DFS board.",
  },
] as const

export const PLAN_OFFERS = [
  { name: "Sandbox", price: "0" },
  { name: "Hobby", price: "29" },
  { name: "Builder", price: "99" },
  { name: "Pro", price: "249" },
] as const

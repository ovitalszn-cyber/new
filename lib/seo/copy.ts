export const DFS_TITLE =
  "DFS Esports API — PrizePicks & Underdog Props for CS2 & LoL"

export const DFS_DESCRIPTION =
  "Affordable DFS esports API with an instant key. Pull PrizePicks, Underdog, Betr, and Sleeper player props for CS2 and LoL — plus Dabble and ParlayPlay — from GET /v6/esports/{sport}/props."

export const DATA_API_TITLE =
  "Esports Data API — CS2, LoL & Dota Props, Lines & Stats"

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

export const MCP_TITLE =
  "KashRock MCP — Use the Esports API from Cursor in 30 Seconds"

export const MCP_DESCRIPTION =
  "Add KashRock to Cursor or Claude. Paste one snippet, say log in, click Google. Live CS2, LoL, Dota, and Valorant props — no docs, no API key to copy."

export const MCP_SNIPPET = `{
  "mcpServers": {
    "kashrock": {
      "command": "uvx",
      "args": ["kashrock-mcp"]
    }
  }
}`

export const MCP_STEPS = [
  {
    n: "1",
    title: "Paste this in Cursor",
    body: "Settings → MCP → add a new server. Paste the snippet. Save.",
  },
  {
    n: "2",
    title: "Say “log in to KashRock”",
    body: "Cursor opens your browser. You click Continue with Google. That’s the only thing you do.",
  },
  {
    n: "3",
    title: "Ask for props",
    body: "Try: “Show CS2 PrizePicks kills.” The agent calls KashRock. You never touch a key.",
  },
] as const

export const MCP_FAQS = [
  {
    q: "Do I need to read the API docs?",
    a: "No. Paste the snippet, log in with Google, then ask in plain English. The agent uses the tools.",
  },
  {
    q: "Do I copy an API key?",
    a: "No. Google login creates the key and stores it on your machine. You should never paste a key into chat.",
  },
  {
    q: "Does this work in Claude too?",
    a: "Yes. Same snippet in Claude Desktop MCP settings. Then ask Claude to log in to KashRock.",
  },
  {
    q: "What if Cursor says uvx is missing?",
    a: "Install uv from https://docs.astral.sh/uv/ — one command — then restart Cursor and try again.",
  },
] as const


export const DFS_TITLE =
  "DFS Esports API — PrizePicks & Underdog Props for CS2 & LoL"

export const DFS_DESCRIPTION =
  "Affordable DFS esports API with an instant key. Pull PrizePicks, Underdog, Betr, Sleeper, Dabble, Boom, and Pick6 player props for CS2 and LoL from GET /v6/esports/{sport}/props."

export const DATA_API_TITLE =
  "Esports Data API — CS2, LoL & Dota Props, Lines & Stats"

export const DATA_API_DESCRIPTION =
  "Esports data API for CS2, League of Legends, Dota 2, and Valorant. Normalized DFS props, sportsbook lines, and Kalshi / Polymarket prediction-market mainlines for sharper models. Free sandbox, then $29+/mo."

export const DFS_FAQS = [
  {
    q: "Does the API include PrizePicks and Underdog lines for CS2 and LoL?",
    a: "Yes. KashRock ingests PrizePicks and Underdog esports props for CS2 and League of Legends, plus Betr, Sleeper, Dabble, Boom, and Pick6. Same player and market share one ID across books.",
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
  {
    q: "Do you pull prediction markets for modeling?",
    a: "Yes. Kalshi and Polymarket esports mainlines (plus Thunderpick sportsbook prices) land on the same schema and power GET /v6/esports/{sport}/lines consensus — useful priors so models are not stuck on one venue.",
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
  "Add KashRock to Cursor or Claude in 30 seconds. Google login, then your agent gets props, moneylines, consensus lines, research, and Builder history — no endpoint hunting."

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
    body: "Settings → MCP → add a new server. Paste the uvx snippet. Save. Needs uv once: docs.astral.sh/uv",
  },
  {
    n: "2",
    title: "Say “log in to KashRock”",
    body: "Cursor opens your browser. Continue with Google. You land on your real billed plan.",
  },
  {
    n: "3",
    title: "Build in plain English",
    body: "Ask for moneylines, props, gamelogs, H2H — the agent picks tools. Call suggest_build if you want a plan.",
  },
] as const

export const MCP_FAQS = [
  {
    q: "Do I need to read the API docs?",
    a: "No. Paste the snippet, log in with Google, then ask in plain English. Prefer MCP over hunting HTTP paths.",
  },
  {
    q: "Do I copy an API key?",
    a: "No. Google login creates the key and stores it on your machine. You should never paste a key into chat.",
  },
  {
    q: "Does this work in Claude too?",
    a: "Yes. Same uvx snippet in Claude Desktop MCP settings. Then ask Claude to log in to KashRock.",
  },
  {
    q: "What if Cursor says uvx is missing?",
    a: "Install uv from https://docs.astral.sh/uv/ — one command — then restart Cursor and try again.",
  },
  {
    q: "What does each plan unlock in MCP?",
    a: "Sandbox: CS2 props. Hobby: all-sport props, lines, research, streams, H2H. Builder+: schedule, gamelogs, boxscores, results, history tape.",
  },
] as const


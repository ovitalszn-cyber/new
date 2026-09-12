export const DFS_TITLE =
  "DFS Esports API — PrizePicks, Underdog & ParlayPlay Props"

export const DFS_DESCRIPTION =
  "Affordable DFS esports API with an instant key. Pull PrizePicks, Underdog, Betr, Sleeper, Dabble, Boom, Pick6, and ParlayPlay player props across CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, and Deadlock from GET /v6/esports/{sport}/props."

export const DATA_API_TITLE =
  "Esports Data API — All 8 Titles: Props, Lines & Stats"

export const DATA_API_DESCRIPTION =
  "Esports data API for CS2, Valorant, League of Legends, Dota 2, Call of Duty, Rainbow Six, Mobile Legends, and Deadlock. Normalized DFS props, sportsbook lines, and Kalshi / Polymarket prediction-market mainlines. Free sandbox, then $29+/mo."

export const DFS_FAQS = [
  {
    q: "Does the API include PrizePicks and Underdog lines for CS2 and LoL?",
    a: "Yes. KashRock ingests PrizePicks and Underdog esports props across the full title set, plus Betr, Sleeper, Dabble, Boom, Pick6, and ParlayPlay. Same player and market share one ID across books.",
  },
  {
    q: "Is this a PrizePicks API or an Underdog API?",
    a: "It is one DFS esports API. You call GET /v6/esports/{sport}/props and filter by book. You do not scrape PrizePicks or Underdog yourself.",
  },
  {
    q: "Can I pull LoL DFS data and CS2 player props from one key?",
    a: "Yes. One key covers all eight titles: cs2, valorant, lol, dota2, cod, r6, mlbb, deadlock. Sandbox is CS2-only; Hobby and up unlock the rest of the board.",
  },
  {
    q: "What does GET /v6/esports/{sport}/props return?",
    a: "A live ingested board: player, stat, line, book (PrizePicks, Underdog, ParlayPlay, and the others), direction, and canonical propId. No upstream scrape on that request.",
  },
] as const

export const DATA_API_FAQS = [
  {
    q: "What does an esports data API include?",
    a: "KashRock covers event schedules, player props and lines, match data, player stats, and outcome verification across CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, and Deadlock.",
  },
  {
    q: "Is there a free esports API tier?",
    a: "Yes. Sandbox is $0/mo with an instant key — CS2 player props so you can verify the schema. Paid plans start at $29/mo.",
  },
  {
    q: "Where do I get DFS books like PrizePicks and Underdog?",
    a: "Use the DFS Esports API page and GET /v6/esports/{sport}/props. That route is the PrizePicks / Underdog / ParlayPlay / LoL DFS board.",
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
  "Add KashRock to Cursor or Claude in 30 seconds (uvx kashrock-mcp). Google login, then your agent gets the full tier-scoped tool catalog — props, moneylines, consensus lines, research, and Builder history."

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
    a: "No. Paste the snippet, log in with Google, then ask in plain English. Prefer MCP over hunting HTTP paths. Full tool list lives on /mcp and /docs/mcp.",
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
    a: "Sandbox: session tools + CS2 props/coverage. Hobby: all eight sports, moneylines, lines, research, streams, H2H. Builder+: schedule, live player kills/deaths/assists under 2s, gamelogs, boxscores, results, history tape. Call list_capabilities after login.",
  },
  {
    q: "Which sports and books?",
    a: "Sports: cs2, valorant, lol, dota2, cod, r6, mlbb, deadlock. Books include PrizePicks, Underdog, ParlayPlay, Betr, Sleeper, Dabble, Boom, Pick6, Thunderpick, Kalshi, and Polymarket. list_books returns the live registry.",
  },
] as const

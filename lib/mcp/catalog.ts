/** Mirrors mcp/src/kashrock_mcp/catalog.py — keep in sync when tools change. */

export type McpTier = "sandbox" | "hobby" | "builder"

export type McpTool = {
  id: string
  when: string
  tier: McpTier
  group: "session" | "board" | "players" | "schedule"
}

export const MCP_SPORTS = [
  "cs2",
  "valorant",
  "lol",
  "dota2",
  "cod",
  "r6",
  "mlbb",
  "deadlock",
] as const

export const MCP_TOOLS: McpTool[] = [
  { id: "login", when: "Google sign-in; stores API key locally.", tier: "sandbox", group: "session" },
  { id: "whoami", when: "Your plan, quota, and unlocked drawers.", tier: "sandbox", group: "session" },
  { id: "list_capabilities", when: "Which tools this plan can use.", tier: "sandbox", group: "session" },
  { id: "suggest_build", when: "Map a one-line app goal to tools + plan.", tier: "sandbox", group: "session" },
  { id: "list_sports", when: "Sports KashRock covers.", tier: "sandbox", group: "session" },
  { id: "list_books", when: "Live book registry (DFS + Thunderpick + Kalshi + Polymarket).", tier: "hobby", group: "session" },
  { id: "list_markets", when: "Canonical market / moneyline names.", tier: "sandbox", group: "session" },
  { id: "explain_error", when: "Turn a 403/401 into plain English.", tier: "sandbox", group: "session" },
  { id: "get_props", when: "Live props board. Sandbox=CS2 only; Hobby+=all sports.", tier: "sandbox", group: "board" },
  { id: "get_moneylines", when: "Team match/map moneylines (line is null — that is normal).", tier: "hobby", group: "board" },
  { id: "get_lines", when: "Consensus Kalshi + Polymarket + Thunderpick.", tier: "hobby", group: "board" },
  { id: "get_coverage", when: "Per-book prop counts / freshness.", tier: "sandbox", group: "board" },
  { id: "search_players", when: "Find players by nickname.", tier: "hobby", group: "players" },
  { id: "get_player", when: "Player profile by id or nickname.", tier: "hobby", group: "players" },
  { id: "get_player_stats", when: "Canonical player stats (KPR, etc.).", tier: "hobby", group: "players" },
  { id: "get_player_stats_full", when: "Full aggregate: period + foundation + recent maps.", tier: "hobby", group: "players" },
  { id: "get_rankings", when: "Player rankings board.", tier: "hobby", group: "players" },
  { id: "research_board", when: "Research slips for the current board.", tier: "hobby", group: "players" },
  { id: "research_board_tapes", when: "Research quote tapes for the live board.", tier: "hobby", group: "players" },
  { id: "research_player", when: "Career tape for one player + market.", tier: "hobby", group: "players" },
  { id: "get_streams", when: "Live Twitch/Kick streams for a sport.", tier: "hobby", group: "players" },
  { id: "get_team_h2h", when: "Team head-to-head meetings from the vault.", tier: "hobby", group: "players" },
  { id: "get_matches", when: "Upcoming / live / finished match lists.", tier: "builder", group: "schedule" },
  { id: "get_match", when: "One match by kr_match_id or slug.", tier: "builder", group: "schedule" },
  { id: "search_matches", when: "Find a match by team names + date.", tier: "builder", group: "schedule" },
  { id: "get_gamelogs", when: "Per-map player history for grading.", tier: "builder", group: "schedule" },
  { id: "get_boxscore", when: "Match boxscore or recent boxscores.", tier: "builder", group: "schedule" },
  { id: "get_results", when: "Settled prop grades (hit/miss/push).", tier: "builder", group: "schedule" },
  { id: "get_history_tape", when: "Quote tape for a prop/book over time.", tier: "builder", group: "schedule" },
]

export const MCP_TIER_LABEL: Record<McpTier, string> = {
  sandbox: "Sandbox+",
  hobby: "Hobby+",
  builder: "Builder+",
}

export const MCP_GROUP_LABEL: Record<McpTool["group"], string> = {
  session: "Session",
  board: "Board",
  players: "Players & research",
  schedule: "Schedule & history",
}

import { DocsShell } from '@/components/docs/DocsShell'
import { API_BASE } from '@/lib/docs'

/** Public DaaS surface only — stacks / internal admin omitted on purpose. */
const ROUTES: { path: string; note: string }[] = [
  { path: 'GET /v6/esports/{sport}/props', note: 'DFS player props only. Each prop has links.player_image / team_logo / opponent_logo.' },
  {
    path: 'GET /v6/esports/{sport}/player-props',
    note: 'DFS + sportsbook named-player props. board=dfs|main|all. Forward by player; backward by market/event.',
  },
  {
    path: 'GET /v6/esports/{sport}/media',
    note: 'Resolve player faces + team logos by name/id. Same links shape as props.',
  },
  {
    path: 'GET /v6/esports/{sport}/gaps',
    note: 'DFS book-vs-book line spreads (line_gap = max − min). Hobby plan.',
  },
  {
    path: 'GET /v6/esports/{sport}/lines',
    note: 'Consensus team main lines (match / map / totals / handicap) across sportsbooks + prediction markets. Hobby+.',
  },
  { path: 'GET /v6/esports/{sport}/fixtures', note: 'Full schedule board. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/matches', note: 'Filtered matches. status=upcoming|live|finished. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/matches/live', note: 'Live matches only. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/upcoming/matches', note: 'Upcoming matches. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/completed/matches', note: 'Finished matches. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/schedule', note: 'Schedule view. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/streams', note: 'Stream links for a sport.' },
  { path: 'GET /v6/esports/{sport}/live/games', note: 'Games with live in-game telemetry. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/live/{game_id}/boxscore', note: 'Live K/D/A scoreboard (round, alive, money). Builder plan.' },
  { path: 'GET /v6/esports/{sport}/live/{game_id}/frames', note: 'Raw live NormalizedFrame + metadata. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/live/{game_id}/events', note: 'Derived live events (kills, etc.). Builder plan.' },
  { path: 'WS /v6/esports/live/ws', note: 'Push live boxscore/frame/events. Builder+. ?api_key= or Bearer.' },
  { path: 'GET /v6/esports/{sport}/rankings', note: 'Player leaderboard. filter=lifetime|last_3_months.' },
  { path: 'GET /v6/esports/{sport}/players/search', note: 'Search by nickname. q= required.' },
  { path: 'GET /v6/esports/{sport}/players/{id}', note: 'Profile by numeric id or slug.' },
  { path: 'GET /v6/esports/{sport}/players/{id}/stats', note: 'Canonical player stats (KPR and related).' },
  { path: 'GET /v6/esports/{sport}/players/{slug}/gamelogs', note: 'Recent map stats. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/teams/h2h', note: 'Head-to-head team comparison.' },
  { path: 'GET /v6/esports/{sport}/results', note: 'Settled props. Optional grade=. Builder plan.' },
  { path: 'GET /v6/esports/{sport}/boxscores', note: 'Box scores for a sport. Builder plan.' },
  { path: 'GET /v6/esports/research/player', note: 'Player research slip. player, sport, market.' },
  { path: 'GET /v6/esports/research/board', note: 'Research slips for the current board.' },
  { path: 'GET /v6/esports/history/contract', note: 'Quote tape. market_key or prop_id+book. Builder plan.' },
  { path: 'GET /v6/books', note: 'Canonical book registry (DFS, Thunderpick, Kalshi, Polymarket).' },
]

export default function ApiReferencePage() {
  return (
    <DocsShell active="index">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Route index</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Public DaaS surface. Base <code className="text-white">{API_BASE}</code>. Auth on every{' '}
        <code className="text-white">/v6</code> call.
      </p>
      <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-zinc-500">
            <tr>
              <th className="py-3 px-4">Route</th>
              <th className="py-3 px-4">What it returns</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {ROUTES.map((r) => (
              <tr key={r.path}>
                <td className="py-3 px-4 font-mono text-emerald-400 text-xs whitespace-nowrap">{r.path}</td>
                <td className="py-3 px-4 text-zinc-400">{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-sm text-zinc-500 mt-6">
        Consensus lines deep dive:{' '}
        <a href="/docs/endpoints/lines" className="text-white underline">
          /docs/endpoints/lines
        </a>
        .
      </p>
    </DocsShell>
  )
}

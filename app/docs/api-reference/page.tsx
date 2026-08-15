import { DocsShell } from '@/components/docs/DocsShell'
import { API_BASE } from '@/lib/docs'

const ROUTES: { path: string; note: string }[] = [
  { path: 'GET /v6/esports/props', note: 'Live ingested props. Query game, book, market.' },
  { path: 'GET /v6/esports/{sport}/props', note: 'Same board, sport in the path.' },
  { path: 'GET /v6/esports/{sport}/fixtures', note: 'Full schedule board.' },
  { path: 'GET /v6/esports/{sport}/matches', note: 'Filtered matches. status=upcoming|live|finished.' },
  { path: 'GET /v6/esports/{sport}/matches/live', note: 'Live matches only.' },
  { path: 'GET /v6/esports/{sport}/upcoming/matches', note: 'Upcoming matches.' },
  { path: 'GET /v6/esports/{sport}/completed/matches', note: 'Finished matches.' },
  { path: 'GET /v6/esports/{sport}/schedule', note: 'Schedule view.' },
  { path: 'GET /v6/esports/{sport}/streams', note: 'Stream links for a sport.' },
  { path: 'GET /v6/esports/{sport}/rankings', note: 'Player leaderboard. filter=lifetime|last_3_months.' },
  { path: 'GET /v6/esports/{sport}/players/search', note: 'Search by nickname. q= required.' },
  { path: 'GET /v6/esports/{sport}/players/{id}', note: 'Profile by numeric id or slug.' },
  { path: 'GET /v6/esports/{sport}/players/{slug}/gamelogs', note: 'Recent map stats.' },
  { path: 'GET /v6/esports/{sport}/results', note: 'Settled props. Optional grade=.' },
  { path: 'GET /v6/esports/research/player', note: 'Player research slip. player, sport, market.' },
  { path: 'GET /v6/esports/history/contract', note: 'Quote tape. market_key or prop_id+book.' },
  { path: 'GET /v6/esports/{sport}/stacks', note: 'CS2 and Valorant correlated slips.' },
  { path: 'GET /v6/esports/{sport}/boxscores', note: 'Box scores for a sport.' },
  { path: 'GET /v6/books', note: 'Canonical book registry.' },
]

export default function ApiReferencePage() {
  return (
    <DocsShell active="index">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Route index</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Public DaaS surface. Base <code className="text-white">{API_BASE}</code>. Auth on every <code className="text-white">/v6</code> call.
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
    </DocsShell>
  )
}

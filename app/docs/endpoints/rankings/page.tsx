import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  source: 'kashrock',
  sport: 'cs2',
  rank: 1,
  id: 18452,
  player: { nickname: 'ZywOo', slug: 'zywoo' },
  team: { name: 'Vitality' },
  games_count: 1011,
}

export default function RankingsPage() {
  return (
    <DocsShell active="rankings">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Rankings</h1>
      <p className="text-lg text-zinc-400 mb-8">Player leaderboards for one sport.</p>
      <Route path="/v6/esports/{sport}/rankings" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2, cod, r6, mlbb, deadlock' },
        { name: 'filter', type: 'string', note: 'lifetime (default) or last_3_months' },
      ]} />
      <Curl path="/v6/esports/cs2/rankings?filter=lifetime" />
      <JsonBlock title="200 · live" data={SAMPLE} />
    </DocsShell>
  )
}

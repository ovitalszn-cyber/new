import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  sport: 'esports_cs2',
  total_props: 448,
  props: [
    {
      propId: 'kr_prop_883ba7a1e090',
      eventId: 'kr_ev_d9410a855f83',
      offerId: 'kr_prop_883ba7a1e090_6_over',
      book_name: 'Betr',
      player_name: 'mezii',
      stat_type: 'CS2_HEADSHOTS_MAPS_1_2',
      line: 14.5,
      direction: 'over',
      team: 'Team Vitality',
      opponent: 'Lynn Vision Gaming',
      event_time: '2026-08-16T13:55:00.000Z',
    },
  ],
}

export default function PropsPage() {
  return (
    <DocsShell active="props">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Props</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Live ingested board. Same market is one <code className="text-white">stat_type</code> across books. This is Redis cache — no upstream fetch on the request path.
      </p>
      <Route path="/v6/esports/props" />
      <p className="text-sm text-zinc-500 mb-6">
        Sport-scoped alias: <code className="text-zinc-300">/v6/esports/{'{sport}'}/props</code>
      </p>
      <Params rows={[
        { name: 'game', type: 'string', note: 'Sport slug. Default cs2. Alias: discipline' },
        { name: 'book', type: 'string', note: 'prizepicks, underdog, parlayplay, dabble, sleeper, betr' },
        { name: 'market', type: 'string', note: 'Exact stat_type, e.g. CS2_KILLS_MAPS_1_2' },
        { name: 'market_contains', type: 'string', note: 'Substring on stat_type, e.g. KILLS' },
        { name: 'player_id', type: 'int', note: 'Filter to one player id' },
      ]} />
      <Curl path="/v6/esports/props?game=cs2" />
      <JsonBlock title="200 · live" data={SAMPLE} />
      <p className="text-sm text-zinc-400">
        Canonical names live in the <Link href="/docs/markets" className="text-white underline">markets dictionary</Link>.
      </p>
    </DocsShell>
  )
}

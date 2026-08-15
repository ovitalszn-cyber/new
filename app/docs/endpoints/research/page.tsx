import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  player: 'chelo',
  sport: 'cs2',
  market: 'Maps 1–2 kills',
  market_slug: 'kills_maps_1_2',
  on_the_board: [
    { book: 'PrizePicks', side: 'Over', line: '29.5', opponent: 'BESTIA', when: 'Aug 15, 2026', source: 'live' },
  ],
  series: [
    {
      when: 'Aug 13, 2026',
      opponent: 'Isurus',
      team: 'Imperial',
      stat: 23,
      maps: 'de_cache / de_inferno',
      coverage: 'Map tape is in',
    },
  ],
  settled: [
    { when: 'Aug 14, 2026', book: 'Sleeper', side: 'Under', line: '28.5', actual: '23', result: 'Hit', opponent: 'Isurus' },
  ],
}

export default function ResearchPage() {
  return (
    <DocsShell active="research">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Research</h1>
      <p className="text-lg text-zinc-400 mb-8">
        One player, one market. Live ingested lines first. Vault fills history, series totals, and settlements. Live and tape are never averaged.
      </p>
      <Route path="/v6/esports/research/player" />
      <Params rows={[
        { name: 'player', type: 'string', required: true, note: 'Nickname.' },
        { name: 'sport', type: 'string', note: 'Default cs2. All supported sport slugs.' },
        { name: 'market', type: 'string', note: 'Slug, default kills_maps_1_2. Also accepts CS2_KILLS_MAPS_1_2.' },
      ]} />
      <Curl path="/v6/esports/research/player?player=chelo&sport=cs2&market=kills_maps_1_2" />
      <JsonBlock title="200" data={SAMPLE} />
      <p className="text-sm text-zinc-500">
        Market slugs: <code className="text-zinc-300">kills_maps_1_2</code>,{' '}
        <code className="text-zinc-300">headshots_maps_1_2</code>,{' '}
        <code className="text-zinc-300">kills_map_4</code>,{' '}
        <code className="text-zinc-300">kills</code> (series). Response includes a <code className="text-zinc-300">markets</code> list for the dropdown.
      </p>
    </DocsShell>
  )
}

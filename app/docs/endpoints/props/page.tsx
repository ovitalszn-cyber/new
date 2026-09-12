import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  source: 'kashrock',
  sport: 'cs2',
  board: 'dfs',
  total: 448,
  props: [
    {
      propId: 'kr_prop_883ba7a1e090',
      eventId: 'kr_ev_d9410a855f83',
      book_name: 'Betr',
      player_name: 'mezii',
      stat_type: 'CS2_HEADSHOTS_MAPS_1_2',
      line: 14.5,
      direction: 'over',
      team: 'Team Vitality',
      opponent: 'Lynn Vision Gaming',
      event_time: '2026-08-16T13:55:00.000Z',
      links: {
        player_image: 'https://img-cdn.hltv.org/playerbodyshot/example.png',
        team_logo: 'https://img-cdn.hltv.org/teamlogo/example-vitality.png',
        opponent_logo: 'https://img-cdn.hltv.org/teamlogo/example-lynn.png',
      },
    },
  ],
}

export default function PropsPage() {
  return (
    <DocsShell active="props">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Props</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Live <span className="text-white">DFS player props only</span> — PrizePicks, Underdog, Dabble, ParlayPlay,
        Sleeper, Betr, Boom, Pick6. Each prop includes card media under{' '}
        <code className="text-white">links</code> (player face + team logos). You do not need a second call for
        images when rendering a prop board.
      </p>
      <Route path="/v6/esports/{sport}/props" />
      <p className="text-sm text-zinc-400 mb-8">
        Call <code className="text-white">/v6/esports/cs2/props</code>. Media shape:{' '}
        <code className="text-white">links.player_image</code>, <code className="text-white">links.team_logo</code>,{' '}
        <code className="text-white">links.opponent_logo</code>. Resolve by name only:{' '}
        <Link href="/docs/endpoints/media" className="text-white underline">
          /{'{sport}'}/media
        </Link>
        . DFS + sportsbook named-player props:{' '}
        <Link href="/docs/endpoints/player-props" className="text-white underline">
          /{'{sport}'}/player-props
        </Link>
        . Team mainlines:{' '}
        <Link href="/docs/endpoints/lines" className="text-white underline">
          /{'{sport}'}/lines
        </Link>
        .
      </p>
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2, cod, r6, mlbb, deadlock' },
        { name: 'book', type: 'string', note: 'prizepicks, underdog, dabble, sleeper, betr, boom, pick6, parlayplay' },
        { name: 'market', type: 'string', note: 'Exact stat_type, e.g. CS2_KILLS_MAPS_1_2' },
        { name: 'market_contains', type: 'string', note: 'Substring on stat_type, e.g. KILLS' },
        { name: 'player_id', type: 'int', note: 'Filter to one player id' },
      ]} />
      <Curl path="/v6/esports/cs2/props" />
      <JsonBlock title="200 · live (media on links)" data={SAMPLE} />
      <p className="text-sm text-zinc-400">
        Canonical names live in the <Link href="/docs/markets" className="text-white underline">markets dictionary</Link>.
      </p>
    </DocsShell>
  )
}

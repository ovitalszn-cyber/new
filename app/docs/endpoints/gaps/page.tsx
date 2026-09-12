import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  source: 'kashrock',
  sport: 'cs2',
  min_gap: 0.5,
  total: 70,
  returned: 1,
  offset: 0,
  limit: 1,
  has_more: true,
  gaps: [
    {
      gap_id: 'gap_ce3fbab1ef1e',
      player_id: 'kr_pl_6b8fc7792bfe',
      player_name: 'khaN',
      team: 'Nemiga',
      opponent: 'Just_Players',
      event_id: 'kr_ev_5886cc9220e5',
      event_time: '2026-09-12T17:00:00.000Z',
      stat_type: 'CS2_KILLS_MAPS_1_2',
      market: 'kills',
      line: 31.5,
      line_min: 30.5,
      line_max: 32.5,
      line_gap: 2.0,
      book_count: 5,
      books: [
        { book: 'sleeper', line: 30.5, propId: 'kr_prop_aa230791ff25', direction: 'over' },
        { book: 'betr', line: 31.5, propId: 'kr_prop_0a7fec48daa2', direction: 'over' },
        { book: 'boom', line: 31.5, propId: 'kr_prop_0a7fec48daa2', direction: 'over' },
        { book: 'prizepicks', line: 31.5, propId: 'kr_prop_0a7fec48daa2', direction: 'over' },
        { book: 'underdog', line: 32.5, propId: 'kr_prop_67030b9dbc0f', direction: 'over' },
      ],
    },
  ],
}

export default function GapsDocsPage() {
  return (
    <DocsShell active="gaps">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Gaps</h1>
      <p className="text-lg text-zinc-400 mb-8">
        DFS book-vs-book line spreads. Same player, event, and <code className="text-white">stat_type</code>{' '}
        with different posted lines → <code className="text-white">line_gap = line_max − line_min</code>.
        Not model edges. Hobby+.
      </p>
      <Route path="/v6/esports/{sport}/gaps" />
      <p className="text-sm text-zinc-400 mb-8">
        Marketing guide:{' '}
        <Link href="/esports-line-gaps-api" className="text-white underline">
          /esports-line-gaps-api
        </Link>
        . MCP: <code className="text-white">get_gaps</code>.
      </p>
      <Params
        rows={[
          {
            name: 'sport',
            type: 'path',
            required: true,
            note: 'cs2, valorant, lol, dota2, cod, r6, mlbb, deadlock',
          },
          { name: 'min_gap', type: 'number', note: 'Default 0.5. Use 0 for every multi-book spread.' },
          { name: 'player', type: 'string', note: 'Name or id substring' },
          { name: 'market', type: 'string', note: 'e.g. kills — matches market label / stat_type' },
          { name: 'market_contains', type: 'string', note: 'Substring on stat_type' },
          { name: 'book', type: 'string', note: 'Require this DFS book in the row' },
          { name: 'limit', type: 'int', note: '1–500, default 100' },
          { name: 'offset', type: 'int', note: 'Pagination offset' },
        ]}
      />
      <Curl path="/v6/esports/cs2/gaps?min_gap=0.5&limit=1" />
      <JsonBlock title="200 · live gap row" data={SAMPLE} />
      <p className="text-sm text-zinc-500 mt-6">
        Books in scope: prizepicks, underdog, dabble, parlayplay, sleeper, betr, boom, pick6. Lines ≤ 0
        and moneylines are excluded. Sorted by line_gap desc.
      </p>
    </DocsShell>
  )
}

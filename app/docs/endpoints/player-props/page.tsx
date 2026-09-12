import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  source: 'kashrock',
  sport: 'cs2',
  board: 'all',
  total_groups: 1,
  total: 3,
  groups: [
    {
      player_name: 'donk',
      player_id: 18452,
      canonical_player_id: 'kr_pl_example',
      stat_type: 'CS2_KILLS_MAPS_1_2',
      event_id: 'kr_ev_example',
      team: 'Team Spirit',
      opponent: 'Natus Vincere',
      event_time: '2026-09-12T15:00:00.000Z',
      dfs: [
        {
          book_name: 'PrizePicks',
          sportsbook_name: 'prizepicks',
          line: 40.5,
          direction: 'over',
          stat_type: 'CS2_KILLS_MAPS_1_2',
        },
        {
          book_name: 'Underdog',
          sportsbook_name: 'underdog',
          line: 41.5,
          direction: 'higher',
          stat_type: 'CS2_KILLS_MAPS_1_2',
        },
      ],
      main: [
        {
          book_name: 'Thunderpick',
          sportsbook_name: 'thunderpick',
          line: 39.5,
          direction: 'over',
          odds: -110,
          stat_type: 'CS2_KILLS_MAPS_1_2',
        },
      ],
    },
  ],
}

export default function PlayerPropsPage() {
  return (
    <DocsShell active="player-props">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Player props</h1>
      <p className="text-lg text-zinc-400 mb-8">
        One board for <strong className="text-white font-medium">DFS player props</strong> and{' '}
        <strong className="text-white font-medium">sportsbook named-player props</strong>. Call them together or
        separately. Forward: start from a player. Backward: start from a market / event. Books are always the
        venue names themselves — never an aggregator site label.
      </p>
      <Route path="/v6/esports/{sport}/player-props" />
      <p className="text-sm text-zinc-400 mb-8">
        DFS shortcut stays at{' '}
        <Link href="/docs/endpoints/props" className="text-white underline">
          /{'{sport}'}/props
        </Link>
        . Team mainlines (match / map / totals / handicap) stay on{' '}
        <Link href="/docs/endpoints/lines" className="text-white underline">
          /{'{sport}'}/lines
        </Link>
        . Optional <code className="text-white">include_event_lines=true</code> attaches those team lines onto each
        player group for the same event.
      </p>
      <Params
        rows={[
          { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2, …' },
          {
            name: 'board',
            type: 'string',
            note: 'all (default) | dfs | main — main = sportsbook named-player props (Thunderpick today)',
          },
          { name: 'player', type: 'string', note: 'Forward: nickname / slug contains' },
          { name: 'player_id', type: 'int', note: 'Forward: numeric player id' },
          { name: 'canonical_player_id', type: 'string', note: 'Forward: kr_pl_* id' },
          { name: 'market', type: 'string', note: 'Backward: exact stat_type' },
          { name: 'market_contains', type: 'string', note: 'Backward: substring on stat_type (e.g. KILLS)' },
          { name: 'event_id', type: 'string', note: 'Slice to one event / matchup' },
          { name: 'book', type: 'string', note: 'Filter to one venue key' },
          {
            name: 'include_event_lines',
            type: 'bool',
            note: 'Attach team mainlines for the same events (from /lines venues)',
          },
        ]}
      />
      <Curl path="/v6/esports/cs2/player-props?player=donk&board=all" />
      <Curl path="/v6/esports/cs2/player-props?market_contains=KILLS&board=dfs" />
      <JsonBlock title="200 · grouped" data={SAMPLE} />
      <p className="text-sm text-zinc-400 mt-6">
        Response includes <code className="text-white">groups[]</code> (player + market + event with{' '}
        <code className="text-white">dfs</code> / <code className="text-white">main</code> arrays) and a flat{' '}
        <code className="text-white">props[]</code> for callers that want rows.
      </p>
    </DocsShell>
  )
}

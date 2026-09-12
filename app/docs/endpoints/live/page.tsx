import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const GAMES = {
  sport: 'cs2',
  total: 1,
  games: [
    {
      game_id: '2397756',
      match_id: '2397756',
      blue_code: 'Voca',
      red_code: 'Liquid',
    },
  ],
}

const BOX = {
  sport: 'cs2',
  game_id: '2397756',
  boxscore: {
    map_name: 'Anubis',
    round: 16,
    round_phase: 'bomb',
    round_clock: '0:07',
    blue: { map_score: 10, kills: 69 },
    red: { map_score: 5, kills: 44 },
    players: [
      { nickname: 'Jorko', side: 'blue', kills: 17, deaths: 7, assists: 2, alive: true },
      { nickname: 'dare', side: 'red', kills: 10, deaths: 14, assists: 2, alive: true },
    ],
  },
}

export default function LiveInGamePage() {
  return (
    <DocsShell active="live">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Live in-game</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Mid-map K/D/A, alive state, round clock. Redis-backed telemetry — not the finished-match
        boxscore path. Builder plan. MCP: <code className="text-white">get_live_boxscore</code>.
      </p>

      <h2 className="text-xl font-semibold text-white mb-4">List live games</h2>
      <Route path="/v6/esports/{sport}/live/games" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2, cod, r6, …' },
      ]} />
      <Curl path="/v6/esports/cs2/live/games" />
      <JsonBlock title="200 · live" data={GAMES} />

      <h2 className="text-xl font-semibold text-white mb-4">Live boxscore</h2>
      <Route path="/v6/esports/{sport}/live/{game_id}/boxscore" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'Same sport slugs as matches.' },
        { name: 'game_id', type: 'path', required: true, note: 'From /live/games.' },
      ]} />
      <Curl path="/v6/esports/cs2/live/2397756/boxscore" />
      <JsonBlock title="200 · live" data={BOX} />

      <h2 className="text-xl font-semibold text-white mb-4">Frame & events</h2>
      <p className="text-sm text-zinc-400 mb-4">
        Also: <code className="text-zinc-300">/{'{sport}'}/live/{'{game_id}'}/frames</code>,{' '}
        <code className="text-zinc-300">/{'{sport}'}/live/{'{game_id}'}/events</code>.
      </p>
      <p className="text-sm text-zinc-500">
        Finished series stats stay on{' '}
        <code className="text-zinc-300">/{'{sport}'}/matches/{'{slug}'}/boxscore</code> (MCP{' '}
        <code className="text-zinc-300">get_boxscore</code>).
      </p>

      <h2 className="text-xl font-semibold text-white mb-4 mt-12">WebSocket wire</h2>
      <p className="text-sm text-zinc-400 mb-4">
        Push updates under 2s after Redis write. Builder+. Auth via{' '}
        <code className="text-zinc-300">?api_key=</code> or Bearer on handshake.
      </p>
      <Route path="WS /v6/esports/live/ws" />
      <pre className="p-4 font-mono text-xs text-zinc-300 bg-[#0C0D0F] border border-white/10 rounded-lg overflow-x-auto mb-4">{`{"op":"subscribe","sport":"cs2","game_id":"2397756"}
{"op":"subscribe","sport":"cs2","game_id":"*"}
{"op":"ping"}`}</pre>
      <p className="text-sm text-zinc-500">
        Server sends <code className="text-zinc-300">snapshot</code>, then{' '}
        <code className="text-zinc-300">update</code> / <code className="text-zinc-300">event</code> /
        <code className="text-zinc-300">games_list</code> ticks.
      </p>
    </DocsShell>
  )
}

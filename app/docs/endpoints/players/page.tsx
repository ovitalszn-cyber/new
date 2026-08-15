import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SEARCH = {
  player_id: 18452,
  nickname: 'ZywOo',
  slug: 'zywoo',
  first_name: 'Mathieu',
  last_name: 'Herbaut',
  team_id: 667,
}

export default function PlayersPage() {
  return (
    <DocsShell active="players">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Players</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Search by nickname, load a profile by id or slug, then pull recent map logs.
      </p>

      <h2 className="text-xl font-semibold text-white mb-4">Search</h2>
      <Route path="/v6/esports/{sport}/players/search" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'Sport slug.' },
        { name: 'q', type: 'string', required: true, note: 'Nickname. Alias: search' },
      ]} />
      <Curl path="/v6/esports/cs2/players/search?q=zywoo" />
      <JsonBlock title="200 · live" data={SEARCH} />

      <h2 className="text-xl font-semibold text-white mb-4">Profile</h2>
      <Route path="/v6/esports/{sport}/players/{player_id}" />
      <p className="text-sm text-zinc-500 mb-8">
        <code className="text-zinc-300">player_id</code> can be numeric (<code className="text-zinc-300">18452</code>) or slug (<code className="text-zinc-300">zywoo</code>).
      </p>
      <Curl path="/v6/esports/cs2/players/zywoo" />

      <h2 className="text-xl font-semibold text-white mb-4">Gamelogs</h2>
      <Route path="/v6/esports/{sport}/players/{player_slug}/gamelogs" />
      <Params rows={[
        { name: 'player_slug', type: 'path', required: true, note: 'Nickname or slug.' },
        { name: 'limit', type: 'int', note: 'Max maps. Default 10.' },
      ]} />
      <Curl path="/v6/esports/cs2/players/zywoo/gamelogs?limit=1" />
    </DocsShell>
  )
}

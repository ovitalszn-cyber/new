import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SEARCH = {
  source: 'kashrock',
  sport: 'cs2',
  players: [
    {
      player_id: 18452,
      nickname: 'ZywOo',
      slug: 'zywoo',
      team_id: 667,
      links: {
        player_image: 'https://img.bo3.gg/uploads/player/18452/image/example.webp',
      },
    },
  ],
  total_players: 1,
}

const PROFILE = {
  source: 'kashrock',
  sport: 'cs2',
  player: {
    id: 18452,
    nickname: 'ZywOo',
    slug: 'zywoo',
    team: 'Team Vitality',
    links: {
      player_image: 'https://img.bo3.gg/uploads/player/18452/image/example.webp',
      team_logo: 'https://img.bo3.gg/uploads/team/667/image/example.webp',
    },
  },
}

export default function PlayersPage() {
  return (
    <DocsShell active="players">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Players</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Search by nickname, load a profile by id or slug, then pull recent map logs. Faces and team logos live under{' '}
        <code className="text-white">links</code> — same shape as{' '}
        <Link href="/docs/endpoints/props" className="text-white underline">
          props
        </Link>{' '}
        and{' '}
        <Link href="/docs/endpoints/media" className="text-white underline">
          media
        </Link>
        .
      </p>

      <h2 className="text-xl font-semibold text-white mb-4">Search</h2>
      <Route path="/v6/esports/{sport}/players/search" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'Sport slug.' },
        { name: 'q', type: 'string', required: true, note: 'Nickname. Alias: search' },
      ]} />
      <Curl path="/v6/esports/cs2/players/search?q=zywoo" />
      <p className="text-sm text-zinc-400 mb-4">
        Or list/filter: <code className="text-white">GET /v6/esports/cs2/players?search=zywoo</code> — each row has{' '}
        <code className="text-white">links.player_image</code>.
      </p>
      <JsonBlock title="200 · list/search" data={SEARCH} />

      <h2 className="text-xl font-semibold text-white mb-4 mt-10">Profile</h2>
      <Route path="/v6/esports/{sport}/players/{player_id}" />
      <p className="text-sm text-zinc-500 mb-8">
        <code className="text-zinc-300">player_id</code> can be numeric (<code className="text-zinc-300">18452</code>) or slug (<code className="text-zinc-300">zywoo</code>).
      </p>
      <Curl path="/v6/esports/cs2/players/zywoo" />
      <JsonBlock title="200 · profile" data={PROFILE} />

      <h2 className="text-xl font-semibold text-white mb-4 mt-10">Stats</h2>
      <Route path="/v6/esports/{sport}/players/{player_id}/stats" />
      <p className="text-sm text-zinc-500 mb-4">
        Canonical KPR and related foundation stats for the player.
      </p>
      <Curl path="/v6/esports/cs2/players/zywoo/stats" />

      <h2 className="text-xl font-semibold text-white mb-4 mt-10">Gamelogs</h2>
      <Route path="/v6/esports/{sport}/players/{player_slug}/gamelogs" />
      <Params rows={[
        { name: 'player_slug', type: 'path', required: true, note: 'Nickname or slug.' },
        { name: 'limit', type: 'int', note: 'Max maps. Default 10.' },
      ]} />
      <Curl path="/v6/esports/cs2/players/zywoo/gamelogs?limit=1" />
      <p className="text-sm text-zinc-500 mt-6">Gamelogs require Builder plan.</p>
    </DocsShell>
  )
}

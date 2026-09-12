import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
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
  teams: [
    {
      team_id: 667,
      name: 'Team Vitality',
      slug: 'vitality',
      links: {
        team_logo: 'https://img.bo3.gg/uploads/team/667/image/example.webp',
      },
    },
  ],
  total_players: 1,
  total_teams: 1,
}

export default function MediaPage() {
  return (
    <DocsShell active="media">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Media</h1>
      <p className="text-lg text-zinc-400 mb-8">
        One call for player faces and team logos. Same <code className="text-white">links</code> shape as props —
        do not scrape other endpoints or invent image fields.
      </p>
      <Route path="/v6/esports/{sport}/media" />
      <p className="text-sm text-zinc-400 mb-8">
        Prefer prop boards when you already have props — each row already carries{' '}
        <code className="text-white">links.player_image</code> / <code className="text-white">team_logo</code> /{' '}
        <code className="text-white">opponent_logo</code>. Use this route when you only have a name or id.
        Also on{' '}
        <Link href="/docs/endpoints/players" className="text-white underline">
          players
        </Link>{' '}
        and <code className="text-white">GET /{'{sport}'}/teams</code>.
      </p>
      <Params
        rows={[
          { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2, …' },
          { name: 'player', type: 'string', note: 'Nickname or slug' },
          { name: 'player_id', type: 'int', note: 'Numeric player id' },
          { name: 'team', type: 'string', note: 'Team name or slug' },
          { name: 'team_id', type: 'int', note: 'Numeric team id' },
          { name: 'opponent', type: 'string', note: 'Second team name/slug (same response.teams[])' },
          { name: 'limit', type: 'int', note: 'Max hits per side (default 5, max 25)' },
        ]}
      />
      <Curl path="/v6/esports/cs2/media?player=zywoo&team=vitality" />
      <JsonBlock title="200 · resolve" data={SAMPLE} />
    </DocsShell>
  )
}

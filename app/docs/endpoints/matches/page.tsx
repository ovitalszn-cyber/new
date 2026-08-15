import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const MATCH = {
  source: 'kashrock',
  kr_match_id: 'kr_cs2_imperial-vs-bestia-2026-08-15',
  slug: 'imperial-vs-bestia-2026-08-15',
  sport: 'esports_cs2',
  status: 'not_started',
  event_time: '2026-08-15T20:00:00Z',
}

const FIXTURE = {
  fixture_id: 'fix_1634179',
  kr_match_id: 'kr_cs2_wave-esports-vs-drama-esports-2026-08-14',
  sport: 'esports_cs2',
  discipline: 'cs2',
  status: 'finished',
  slug: 'wave-esports-vs-drama-esports-2026-08-14',
}

export default function MatchesPage() {
  return (
    <DocsShell active="matches">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Matches & fixtures</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Upcoming, live, and finished games. Fixtures is the full schedule board. Matches is the filtered list for one status.
      </p>

      <h2 className="text-xl font-semibold text-white mb-4">Matches</h2>
      <Route path="/v6/esports/{sport}/matches" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2, cod, r6, mlbb, deadlock' },
        { name: 'status', type: 'string', note: 'upcoming (default), live, finished' },
        { name: 'start_date', type: 'date', note: 'YYYY-MM-DD' },
        { name: 'end_date', type: 'date', note: 'YYYY-MM-DD' },
        { name: 'limit', type: 'int', note: 'Page size. Default 50.' },
        { name: 'offset', type: 'int', note: 'Skip N rows.' },
      ]} />
      <Curl path="/v6/esports/cs2/matches?status=upcoming&limit=1" />
      <JsonBlock title="200 · live" data={MATCH} />

      <h2 className="text-xl font-semibold text-white mb-4">Fixtures</h2>
      <Route path="/v6/esports/{sport}/fixtures" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'Same sport slugs as matches.' },
        { name: 'status', type: 'string', note: 'upcoming, live, ended (also accepts not_started / running / finished)' },
        { name: 'start_date', type: 'date', note: 'YYYY-MM-DD' },
        { name: 'end_date', type: 'date', note: 'YYYY-MM-DD' },
      ]} />
      <Curl path="/v6/esports/cs2/fixtures" />
      <JsonBlock title="200 · live" data={FIXTURE} />

      <p className="text-sm text-zinc-500">
        Also: <code className="text-zinc-300">/{'{sport}'}/matches/live</code>,{' '}
        <code className="text-zinc-300">/{'{sport}'}/upcoming/matches</code>,{' '}
        <code className="text-zinc-300">/{'{sport}'}/completed/matches</code>,{' '}
        <code className="text-zinc-300">/{'{sport}'}/schedule</code>,{' '}
        <code className="text-zinc-300">/{'{sport}'}/streams</code>.
      </p>
    </DocsShell>
  )
}

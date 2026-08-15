import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  propId: 'kr_prop_1edea6434599',
  player_name: 'roxesz',
  stat_type: 'CS2_HEADSHOTS_MAPS_1_2',
  line: 9.5,
  direction: 'over',
  grade: 'hit',
  actual_value: 11.0,
  graded_at: '2026-08-15T17:12:46.644703+00:00',
}

export default function ResultsPage() {
  return (
    <DocsShell active="results">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Results</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Settled props for a sport. Grades: hit, miss, push, pending, error. Same <code className="text-white">stat_type</code> as the live board.
      </p>
      <Route path="/v6/esports/{sport}/results" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'Sport slug, or all' },
        { name: 'grade', type: 'string', note: 'hit, miss, push, pending, error' },
      ]} />
      <Curl path="/v6/esports/cs2/results" />
      <JsonBlock title="200 · live" data={SAMPLE} />
    </DocsShell>
  )
}

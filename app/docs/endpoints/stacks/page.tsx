import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, Params, Route } from '@/components/docs/Code'

export default function StacksPage() {
  return (
    <DocsShell active="stacks">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Stacks</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Correlated slips for CS2 and Valorant. Legs carry the book line, the sharp line, and the gap. Filter by book with <code className="text-white">app</code>.
      </p>
      <Route path="/v6/esports/{sport}/stacks" />
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'cs2 or valorant' },
        { name: 'app', type: 'string', note: 'Book slug, e.g. prizepicks' },
        { name: 'archetype', type: 'string', note: 'stomp, bring_back, collapse, cannibalization' },
        { name: 'include_c_tier', type: 'bool', note: 'Include C-tier stacks. Default false.' },
      ]} />
      <Curl path="/v6/esports/cs2/stacks?app=prizepicks" />
      <p className="text-sm text-zinc-500">
        Each leg includes <code className="text-zinc-300">app_line</code>, <code className="text-zinc-300">sharp_line</code>, <code className="text-zinc-300">gap</code>, <code className="text-zinc-300">stat_type</code>, and player identity. Public edge/gap list endpoints are not part of this API — stacks is the product surface.
      </p>
    </DocsShell>
  )
}

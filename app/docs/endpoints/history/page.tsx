import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'

const SAMPLE = {
  prop_id: 'kr_prop_90f5d48848af',
  market_key: 'kr_mk_bb9dc1e03b45f0d4',
  contract: {
    book: 'underdog',
    event_id: 'kr_ev_d2a547772dc4',
    market_definition_id: 'kr_md_lol_kills_maps_1_2_v1',
  },
  quote_tape: [
    {
      side: 'over',
      line: 6.5,
      price_american: -121,
      market_status: 'open',
      is_latest: true,
    },
  ],
}

export default function HistoryPage() {
  return (
    <DocsShell active="history">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">History tape</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Quote tape and settlement for one contract. Vault only — no live source fan-out on the request path.
      </p>
      <Route path="/v6/esports/history/contract" />
      <Params rows={[
        { name: 'market_key', type: 'string', note: 'Canonical market key. Required unless prop_id + book.' },
        { name: 'prop_id', type: 'string', note: 'Use with book when you do not have market_key.' },
        { name: 'book', type: 'string', note: 'Book slug. Required with prop_id.' },
      ]} />
      <Curl path="/v6/esports/history/contract?market_key=kr_mk_bb9dc1e03b45f0d4" />
      <JsonBlock title="200 · live" data={SAMPLE} />
    </DocsShell>
  )
}

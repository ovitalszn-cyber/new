import { DocsShell } from '@/components/docs/DocsShell'
import esportsMarkets from '../../../data/esports_markets.json'

const LINE_MARKETS = [
  {
    id: 'match_winner',
    name: 'Match winner',
    note: 'map and line are null. Full-series moneyline.',
  },
  {
    id: 'map_winner',
    name: 'Map winner',
    note: 'map is 1/2/3…. line is null.',
  },
  {
    id: 'total_maps',
    name: 'Total maps',
    note: 'line required (e.g. 2.5). Same line across venues to join.',
  },
  {
    id: 'map_handicap',
    name: 'Map handicap',
    note: 'line required (e.g. -1.5). Kalshi omitted — not on their board.',
  },
]

export default function MarketsPage() {
  const grouped = esportsMarkets.markets.reduce(
    (acc, market) => {
      if (!acc[market.game]) acc[market.game] = []
      acc[market.game].push(market)
      return acc
    },
    {} as Record<string, typeof esportsMarkets.markets>,
  )

  return (
    <DocsShell active="markets">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Markets</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Canonical <code className="text-white">stat_type</code> values on the live props board, plus consensus{' '}
        <code className="text-white">market</code> keys for{' '}
        <a href="/docs/endpoints/lines" className="text-white underline">
          /lines
        </a>
        .
      </p>

      <h2 className="text-2xl font-semibold text-white mb-4">Consensus line markets</h2>
      <p className="text-sm text-zinc-500 mb-4">
        Pass as <code className="text-white">?market=</code> on{' '}
        <code className="text-white">GET /v6/esports/{'{sport}'}/lines</code>. Omit to return all.
      </p>
      <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-12">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-zinc-500">
            <tr>
              <th className="py-3 px-4">market</th>
              <th className="py-3 px-4">Name</th>
              <th className="py-3 px-4">Notes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {LINE_MARKETS.map((m) => (
              <tr key={m.id}>
                <td className="py-3 px-4 font-mono text-emerald-400 text-xs">{m.id}</td>
                <td className="py-3 px-4 text-zinc-300">{m.name}</td>
                <td className="py-3 px-4 text-zinc-500">{m.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-white mb-4">Props board stat_type</h2>
      <p className="text-sm text-zinc-500 mb-6">
        Use these on props <code className="text-white">market=</code> and research{' '}
        <code className="text-white">market=</code>.
      </p>
      {Object.entries(grouped).map(([game, rows]) => (
        <div key={game} className="mb-12">
          <h3 className="text-xl font-semibold text-white mb-4">{game}</h3>
          <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-zinc-500">
                <tr>
                  <th className="py-3 px-4">Market</th>
                  <th className="py-3 px-4">stat_type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {rows.map((m) => (
                  <tr key={m.id}>
                    <td className="py-3 px-4 text-zinc-300">{m.name}</td>
                    <td className="py-3 px-4 font-mono text-emerald-400 text-xs">{m.canonical_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </DocsShell>
  )
}

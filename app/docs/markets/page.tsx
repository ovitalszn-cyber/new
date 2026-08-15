import { DocsShell } from '@/components/docs/DocsShell'
import esportsMarkets from '../../../data/esports_markets.json'

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
        Canonical <code className="text-white">stat_type</code> values currently on the live board. Use these on props <code className="text-white">market=</code> and research <code className="text-white">market=</code>.
      </p>
      {Object.entries(grouped).map(([game, rows]) => (
        <div key={game} className="mb-12">
          <h2 className="text-xl font-semibold text-white mb-4">{game}</h2>
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

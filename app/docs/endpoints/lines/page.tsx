import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock, Params, Route } from '@/components/docs/Code'
import { API_BASE } from '@/lib/docs'

const SAMPLE = {
  source: 'kashrock',
  sport: 'cs2',
  market: 'match_winner',
  pm_weight: 1.5,
  total_events: 1,
  events: [
    {
      event_id: 'kr_ev_example',
      home_team: 'Team Vitality',
      away_team: 'Lynn Vision',
      event_time: '2026-09-12T15:00:00Z',
      consensus_confidence: 0.91,
      markets: [
        {
          market: 'match_winner',
          map: null,
          line: null,
          consensus_confidence: 0.91,
          sources_used: ['thunderpick', 'kalshi', 'polymarket'],
          outcomes: [
            {
              name: 'team vitality',
              consensus_probability: 0.62,
              sources: [
                {
                  source: 'thunderpick',
                  type: 'sportsbook',
                  probability: 0.58,
                  decimal: 1.65,
                  american: -154,
                },
                {
                  source: 'kalshi',
                  type: 'prediction_market',
                  probability: 0.63,
                  decimal: 1.59,
                  american: -170,
                },
                {
                  source: 'polymarket',
                  type: 'prediction_market',
                  probability: 0.6,
                  decimal: 1.67,
                  american: -150,
                },
              ],
              best_price: {
                source: 'thunderpick',
                type: 'sportsbook',
                decimal: 1.72,
                probability: 0.58,
                edge_pct: 6.64,
              },
            },
          ],
          best_edge: {
            source: 'thunderpick',
            outcome: 'team vitality',
            decimal: 1.72,
            edge_pct: 6.64,
          },
        },
      ],
      best_edge: {
        market: 'match_winner',
        outcome: 'team vitality',
        source: 'thunderpick',
        edge_pct: 6.64,
      },
    },
  ],
}

const FIELDS = [
  { field: 'consensus_probability', meaning: 'De-vigged, venue-weighted fair probability for the outcome' },
  { field: 'best_price', meaning: 'Source with the best payout on the outcome, its decimal, implied prob, and edge_pct' },
  { field: 'edge_pct', meaning: 'EV vs consensus: consensus × decimal − 1. Positive = value' },
  { field: 'consensus_confidence', meaning: '0–1 agreement across venues (higher = tighter)' },
  { field: 'sources[]', meaning: 'Each venue’s price + implied probability + type (sportsbook / prediction_market)' },
  { field: 'best_edge', meaning: 'Highest-edge outcome for the market / event (for card ranking)' },
]

export default function LinesPage() {
  return (
    <DocsShell active="lines">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Lines</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Normalized main lines per event with cross-venue consensus and edge. Thunderpick + Kalshi + Polymarket.
      </p>
      <Route path="/v6/esports/{sport}/lines" />
      <p className="text-sm text-zinc-400 mb-4">
        Auth: <code className="text-white">X-API-Key</code>. Base <code className="text-white">{API_BASE}</code>.
        Builder or Pro plan required.
      </p>
      <Params rows={[
        { name: 'sport', type: 'path', required: true, note: 'cs2, valorant, lol, dota2' },
        { name: 'event_id', type: 'string', note: 'Optional. Canonical event id or matchup key. Omit = all upcoming.' },
        { name: 'market', type: 'string', note: 'match_winner | map_winner | total_maps | map_handicap. Omit = all.' },
        { name: 'pm_weight', type: 'float', note: 'Prediction-market weight vs sportsbook (default 1.5)' },
      ]} />
      <Curl path="/v6/esports/cs2/lines?market=match_winner" />
      <JsonBlock title="200 · consensus" data={SAMPLE} />

      <h2 className="text-2xl font-semibold text-white mt-12 mb-4">Field reference</h2>
      <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-10">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-zinc-500">
            <tr>
              <th className="py-3 px-4">Field</th>
              <th className="py-3 px-4">Meaning</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {FIELDS.map((row) => (
              <tr key={row.field}>
                <td className="py-3 px-4 font-mono text-emerald-400 text-xs whitespace-nowrap">{row.field}</td>
                <td className="py-3 px-4 text-zinc-400">{row.meaning}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-white mb-3">How consensus works</h2>
      <p className="text-sm text-zinc-400 mb-4 leading-relaxed">
        Prediction markets (Kalshi, Polymarket) are read as probabilities directly. The sportsbook is converted American → implied probability, then each source is de-vigged so its outcomes sum to 1.0.
        Consensus is a weighted mean (prediction markets default weight 1.5). Edge is informational EV vs that fair number — not betting advice.
      </p>
      <p className="text-sm text-zinc-400 mb-4 leading-relaxed">
        Hard quality gates before a pick is surfaced in <code className="text-white">top_edges</code>: Kalshi/Polymarket liquidity floors,
        ≥3 sources, max source disagreement ≤12 points, and raw edge capped at 8%. Ranking uses confidence × liquidity × edge (not raw edge).
        Two-source or disagreeing markets stay in <code className="text-white">events</code> with quality flags but are excluded from the top feed.
      </p>
      <p className="text-sm text-zinc-500 mb-8">
        Markets: match winner, map winner, total maps, map handicap. Kalshi has no map handicap on the live board — that source is omitted for handicap only.
        total_maps requires same matchup + same line across venues.
      </p>

      <h2 className="text-2xl font-semibold text-white mb-3">Errors</h2>
      <ul className="text-sm text-zinc-400 space-y-2 mb-8">
        <li><code className="text-white">401</code> — missing / invalid API key</li>
        <li><code className="text-white">403</code> — plan below Builder</li>
        <li><code className="text-white">400</code> — invalid <code className="text-white">market</code></li>
      </ul>
      <p className="text-sm text-zinc-400">
        Related: <Link href="/docs/endpoints/props" className="text-white underline">Props</Link>
        {' · '}
        <Link href="/docs/markets" className="text-white underline">Markets</Link>
      </p>
    </DocsShell>
  )
}

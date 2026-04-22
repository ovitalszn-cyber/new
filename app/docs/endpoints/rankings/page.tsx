import Link from 'next/link';

export default function RankingsEndpointPage() {
  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans">
      <header className="h-16 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md sticky top-0 z-50 flex items-center px-6 justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <img src="/kashrock-logo.svg" alt="KashRock" className="h-5 w-auto" />
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="https://backend.kashrock.com/docs" className="text-sm font-medium text-white">Documentation</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto py-12 px-6">
        <div className="mb-4">
          <Link href="https://backend.kashrock.com/docs" className="text-sm text-zinc-500 hover:text-white">&larr; Back to Docs</Link>
        </div>

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Rankings</h1>
        <p className="text-lg text-zinc-400 mb-8">
          Retrieve player performance rankings with advanced stats sourced from Bo3.gg and PandaScore.
        </p>

        <h2 className="text-xl font-semibold text-white mb-4">API Endpoint</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm mb-8">
          <span className="text-emerald-400">GET</span>
          <span className="text-zinc-300 ml-3">/v6/esports/{'{discipline}'}/rankings</span>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Parameters</h2>
        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                <th className="py-4 px-6">Parameter</th>
                <th className="py-4 px-6">Type</th>
                <th className="py-4 px-6">Required</th>
                <th className="py-4 px-6">Description</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-white/5">
              <tr>
                <td className="py-4 px-6 font-mono text-white">discipline</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6"><span className="text-emerald-400">✓</span></td>
                <td className="py-4 px-6 text-zinc-400">Game slug: <code className="text-white">cs2</code>, <code className="text-white">valorant</code>, <code className="text-white">lol</code>, <code className="text-white">dota-2</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">sort_by</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Sort field: <code className="text-white">rating</code>, <code className="text-white">kills</code>, <code className="text-white">kd_ratio</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">timeframe</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Time range: <code className="text-white">30d</code>, <code className="text-white">90d</code>, <code className="text-white">year</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">limit</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Max results (default: 50, max: 200)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example URLs</h2>
        <div className="space-y-4 mb-8">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">CS2 top players by rating:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/cs2/rankings?sort_by=rating&limit=20
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Valorant rankings last 30 days:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/valorant/rankings?timeframe=30d
            </code>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example Response</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-xs mb-8">
          <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500">
            Response
          </div>
          <pre className="p-4 overflow-x-auto text-zinc-300">
{`[
  {
    "rank": 1,
    "team": "FaZe Clan",
    "points": 1000,
    "change": 0
  },
  {
    "rank": 2,
    "team": "G2 Esports",
    "points": 950,
    "change": 1
  }
]`}
</pre>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Response Fields</h2>
        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                <th className="py-4 px-6">Field</th>
                <th className="py-4 px-6">Type</th>
                <th className="py-4 px-6">Description</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-white/5">
              <tr>
                <td className="py-4 px-6 font-mono text-white">avg_player_rating</td>
                <td className="py-4 px-6 text-zinc-400">float</td>
                <td className="py-4 px-6 text-zinc-400"> HLTV-style rating (6.5+ is elite)</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">avg_kd_rate</td>
                <td className="py-4 px-6 text-zinc-400">float</td>
                <td className="py-4 px-6 text-zinc-400">Average Kill/Death ratio</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">avg_headshot_kills_accuracy</td>
                <td className="py-4 px-6 text-zinc-400">float</td>
                <td className="py-4 px-6 text-zinc-400">Percentage of kills that were headshots</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">multikills_vs_5</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6 text-zinc-400">Total number of Aces (5K) recorded</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">clutches_vs_1</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6 text-zinc-400">Total 1v1 clutches won</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">games_count</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6 text-zinc-400">Total maps/games used for calculation</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="flex gap-4 mt-12">
          <Link href="/docs/endpoints/matches" className="text-sm text-zinc-500 hover:text-white">
            ← Matches
          </Link>
          <Link href="/docs/endpoints/players" className="text-sm text-emerald-400 hover:text-emerald-300">
            Next: Players →
          </Link>
        </div>
      </div>
    </div>
  );
}

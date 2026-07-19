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
            <Link href="/docs" className="text-sm font-medium text-white">Documentation</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto py-12 px-6">
        <div className="mb-4">
          <Link href="/docs" className="text-sm text-zinc-500 hover:text-white">&larr; Back to Docs</Link>
        </div>

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Rankings</h1>
        <p className="text-lg text-zinc-400 mb-8">
          Retrieve player performance rankings with advanced stats sourced from Bo3.gg.
        </p>

        <h2 className="text-xl font-semibold text-white mb-4">API Endpoint</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm mb-8">
          <span className="text-emerald-400">GET</span>
          <span className="text-zinc-300 ml-3">/v6/esports/{'{sport}'}/rankings</span>
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
                <td className="py-4 px-6 font-mono text-white">sport</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6"><span className="text-emerald-400">✓</span></td>
                <td className="py-4 px-6 text-zinc-400">Path slug: <code className="text-white">cs2</code>, <code className="text-white">valorant</code>, <code className="text-white">lol</code>, <code className="text-white">dota2</code>, <code className="text-white">cod</code>, <code className="text-white">r6</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">filter</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Stats window: <code className="text-white">lifetime</code> (default), <code className="text-white">last_3_months</code></td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example URLs</h2>
        <div className="space-y-4 mb-8">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">CS2 lifetime rankings:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/cs2/rankings?filter=lifetime
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Valorant last 3 months:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/valorant/rankings?filter=last_3_months
            </code>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example Response</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-xs mb-8">
          <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500">
            Response
          </div>
          <pre className="p-4 overflow-x-auto text-zinc-300">
{`{
  "source": "kashrock",
  "sport": "cs2",
  "rankings": [
    {
      "rank": 1,
      "id": 18452,
      "player": {
        "id": 18452,
        "slug": "zywoo",
        "nickname": "ZywOo"
      },
      "team": {
        "id": 667,
        "name": "Vitality",
        "slug": "vitality"
      },
      "avg_player_rating": 6.96,
      "avg_kd_rate": 1.42,
      "games_count": 84,
      "avg_headshot_kills_accuracy": 0.51
    }
  ],
  "total": 500
}`}
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
                <td className="py-4 px-6 text-zinc-400">HLTV-style rating (6.5+ is elite)</td>
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

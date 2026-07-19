import Link from 'next/link';

export default function PropsEndpointPage() {
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

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Props</h1>
        <p className="text-lg text-zinc-400 mb-8">
          Real-time player props aggregated from multiple DFS platforms, normalized to our canonical stat system.
        </p>

        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-md p-4 flex gap-4 mb-8">
          <div className="text-emerald-400 shrink-0">✓</div>
          <div>
            <p className="text-sm text-emerald-200/80 mb-2">
              <strong>Canonical Mapping:</strong> All prop labels are normalized across platforms.
            </p>
            <p className="text-sm text-emerald-200/60">
              &quot;Kills Map 1+2&quot; (PrizePicks) = &quot;1st 2 Maps KILLS&quot; (Underdog) = <code className="text-emerald-400">CS2_KILLS_MAPS_1_2</code>
            </p>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">API Endpoint</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm mb-8">
          <span className="text-emerald-400">GET</span>
          <span className="text-zinc-300 ml-3">/v6/esports/props</span>
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
                <td className="py-4 px-6 font-mono text-white">game</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Game slug (default <code className="text-white">cs2</code>): <code className="text-white">cs2</code>, <code className="text-white">valorant</code>, <code className="text-white">lol</code>, <code className="text-white">dota2</code>. Alias: <code className="text-white">discipline</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">book</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Filter by source: <code className="text-white">prizepicks</code>, <code className="text-white">underdog</code>, <code className="text-white">dabble</code>, <code className="text-white">sleeper</code>. Alias: <code className="text-white">sportsbook</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">market</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Exact match on <code className="text-white">stat_type</code>: <code className="text-white">CS2_KILLS_MAPS_1_2</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">market_contains</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Substring match on <code className="text-white">stat_type</code>: <code className="text-white">KILLS</code>, <code className="text-white">HEADSHOTS</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">player_id</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Filter props for a specific player</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example URLs</h2>
        <div className="space-y-4 mb-8">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">All CS2 props from PrizePicks:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/props?game=cs2&book=prizepicks
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Kills props across all platforms:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/props?game=cs2&market_contains=KILLS
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Props for a specific player:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/props?game=cs2&player_id=18452
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
  "sport": "esports_cs2",
  "props": [
    {
      "propId": "kr_prop_f4972484fc50d1c5",
      "book_name": "PrizePicks",
      "player_name": "fear",
      "player_id": 12345,
      "stat_type": "CS2_KILLS_MAPS_1_2",
      "line": 25.5,
      "direction": "over",
      "odds": -110,
      "team": "Fnatic",
      "opponent": "G2",
      "event_time": "2026-07-10T13:30:00Z",
      "links": {
        "player_image": "https://...",
        "team_logo": "https://..."
      }
    }
  ],
  "total_props": 952,
  "books": ["dabble", "prizepicks", "sleeper", "underdog"]
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
                <td className="py-4 px-6 font-mono text-white">propId</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-400">Canonical KashRock prop id</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">stat_type</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-400">Normalized market identifier</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">line</td>
                <td className="py-4 px-6 text-zinc-400">float</td>
                <td className="py-4 px-6 text-zinc-400">The prop line (e.g., 24.5 kills)</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">book_name</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-400">Source platform display name</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">direction</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-400"><code className="text-white">over</code> or <code className="text-white">under</code></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 flex gap-4 mb-8">
          <div className="text-blue-400 shrink-0">ℹ️</div>
          <p className="text-sm text-blue-200/80">
            See the full list of canonical markets in the <Link href="/docs/markets" className="text-white hover:underline">Active Markets</Link> reference.
          </p>
        </div>

        <div className="flex gap-4 mt-12">
          <Link href="/docs/endpoints/players" className="text-sm text-zinc-500 hover:text-white">
            ← Players
          </Link>
          <Link href="/docs/markets" className="text-sm text-emerald-400 hover:text-emerald-300">
            Next: Active Markets →
          </Link>
        </div>
      </div>
    </div>
  );
}

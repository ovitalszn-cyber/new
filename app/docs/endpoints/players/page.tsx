import Link from 'next/link';

export default function PlayersEndpointPage() {
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

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Players</h1>
        <p className="text-lg text-zinc-400 mb-8">
          Retrieve detailed player profiles with career stats, team history, and recent match performance.
        </p>

        <h2 className="text-xl font-semibold text-white mb-4">API Endpoints</h2>
        
        <div className="space-y-4 mb-8">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm">
            <span className="text-emerald-400">GET</span>
            <span className="text-zinc-300 ml-3">/v6/esports/{'{discipline}'}/players/{'{player_id}'}</span>
            <p className="text-zinc-500 text-xs mt-2 font-sans">Get single player by ID</p>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm">
            <span className="text-emerald-400">GET</span>
            <span className="text-zinc-300 ml-3">/v6/esports/{'{discipline}'}/players/search</span>
            <p className="text-zinc-500 text-xs mt-2 font-sans">Search players by name</p>
          </div>
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
                <td className="py-4 px-6 font-mono text-white">player_id</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6"><span className="text-emerald-400">✓</span></td>
                <td className="py-4 px-6 text-zinc-400">Player ID from rankings or search</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">q</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Search query for player name (search endpoint)</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">include_gamelogs</td>
                <td className="py-4 px-6 text-zinc-400">boolean</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Include recent match-by-match stats (default: false)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example URLs</h2>
        <div className="space-y-4 mb-8">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Get player by ID:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/cs2/players/18452
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Search for player:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/cs2/players/search?q=zywoo
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Get player with recent gamelogs:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/cs2/players/18452?include_gamelogs=true
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
  "player": {
    "id": 12345,
    "slug": "fear",
    "name": "fear",
    "first_name": "Fear",
    "last_name": "Fear",
    "role": "player",
    "image_url": "https://example.com/player.png",
    "current_team": {
        "id": 678,
        "name": "Example Team",
        "slug": "example-team"
    }
  }
}`}
</pre>
        </div>

        <div className="flex gap-4 mt-12">
          <Link href="/docs/endpoints/rankings" className="text-sm text-zinc-500 hover:text-white">
            ← Rankings
          </Link>
          <Link href="/docs/endpoints/props" className="text-sm text-emerald-400 hover:text-emerald-300">
            Next: Props →
          </Link>
        </div>
      </div>
    </div>
  );
}

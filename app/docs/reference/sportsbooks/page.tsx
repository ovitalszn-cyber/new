import Link from 'next/link';

const sportsbooks = [
  {
    id: 'prizepicks',
    name: 'PrizePicks',
    type: 'DFS',
    props: true,
    description: 'Daily fantasy sports platform with player props.',
  },
  {
    id: 'underdog',
    name: 'Underdog Fantasy',
    type: 'DFS',
    props: true,
    description: 'DFS with pick\'em style player props.',
  },
  {
    id: 'dabble',
    name: 'Dabble',
    type: 'DFS',
    props: true,
    description: 'Social betting and DFS platform.',
  },
  {
    id: 'betr',
    name: 'Betr',
    type: 'DFS',
    props: true,
    description: 'Micro-betting and props platform.',
  },
  {
    id: 'parlayplay',
    name: 'ParlayPlay',
    type: 'DFS',
    props: true,
    description: 'Parlay-focused DFS platform.',
  },
];

export default function SportsbooksPage() {
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

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Sportsbooks</h1>
        <p className="text-lg text-zinc-400 mb-2">
          KashRock aggregates esports props from the following platforms. Use the <code className="bg-zinc-800 text-emerald-400 px-1.5 py-0.5 rounded font-mono text-sm">sportsbook</code> parameter to filter by source.
        </p>

        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-md p-4 flex gap-4 mb-12">
          <div className="text-emerald-400 shrink-0">✓</div>
          <p className="text-sm text-emerald-200/80">
            All prop lines are normalized to our canonical stat system for cross-platform comparison.
          </p>
        </div>

        <h2 className="text-xl font-semibold text-white mb-6">Supported Platforms</h2>

        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                <th className="py-4 px-6">ID</th>
                <th className="py-4 px-6">Name</th>
                <th className="py-4 px-6">Type</th>
                <th className="py-4 px-6">Props</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-white/5">
              {sportsbooks.map((sb) => (
                <tr key={sb.id} className="hover:bg-white/[0.02]">
                  <td className="py-4 px-6">
                    <code className="text-emerald-400 bg-emerald-400/10 border border-emerald-500/20 px-2 py-1 rounded font-mono text-xs">
                      {sb.id}
                    </code>
                  </td>
                  <td className="py-4 px-6 text-white font-medium">{sb.name}</td>
                  <td className="py-4 px-6">
                    <span className={`px-2 py-1 rounded text-xs ${
                      sb.type === 'DFS' ? 'bg-purple-500/20 text-purple-300' :
                      sb.type === 'Sportsbook' ? 'bg-blue-500/20 text-blue-300' :
                      'bg-zinc-500/20 text-zinc-300'
                    }`}>
                      {sb.type}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    {sb.props ? (
                      <span className="text-emerald-400">✓</span>
                    ) : (
                      <span className="text-zinc-600">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mt-12 mb-6">Example: Filter by Sportsbook</h2>

        <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-sm mb-8">
          <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between">
            <span>Request</span>
            <span className="text-[10px] uppercase">GET</span>
          </div>
          <div className="p-4 overflow-x-auto">
            <code className="text-zinc-300">
              curl "https://backend.kashrock.com/v6/props?sportsbook=<span className="text-emerald-400">prizepicks</span>&discipline=cs2"
            </code>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-white mt-12 mb-6">Platform Details</h2>

        <div className="space-y-4">
          {sportsbooks.map((sb) => (
            <div key={sb.id} className="bg-[#0C0D0F] border border-white/5 rounded-lg p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-white font-medium">{sb.name}</h3>
                <code className="text-zinc-500 text-xs font-mono">{sb.id}</code>
              </div>
              <p className="text-zinc-400 text-sm">{sb.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

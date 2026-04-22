import Link from 'next/link';

const disciplines = [
  {
    id: 'cs2',
    name: 'Counter-Strike 2',
    slug: 'cs2',
    icon: '',
    description: 'Tactical FPS. 5v5 bomb defusal.',
    stats: ['kills', 'deaths', 'assists', 'headshots', 'awp_kills', 'rating'],
  },
  {
    id: 'valorant',
    name: 'Valorant',
    slug: 'valorant',
    icon: '',
    description: 'Tactical shooter with agent abilities.',
    stats: ['kills', 'deaths', 'assists', 'first_bloods', 'plants', 'defuses'],
  },
  {
    id: 'lol',
    name: 'League of Legends',
    slug: 'lol',
    icon: '',
    description: 'MOBA. 5v5 on Summoner\'s Rift.',
    stats: ['kills', 'deaths', 'assists', 'cs', 'gold', 'damage'],
  },
  {
    id: 'dota-2',
    name: 'Dota 2',
    slug: 'dota-2',
    icon: '',
    description: 'MOBA with deep hero mechanics.',
    stats: ['kills', 'deaths', 'assists', 'last_hits', 'denies', 'gpm'],
  },
];

export default function DisciplinesPage() {
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

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Disciplines</h1>
        <p className="text-lg text-zinc-400 mb-2">
          KashRock supports the following esports titles. Use the <code className="bg-zinc-800 text-emerald-400 px-1.5 py-0.5 rounded font-mono text-sm">discipline</code> parameter in API requests.
        </p>

        <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 flex gap-4 mb-12">
          <div className="text-blue-400 shrink-0">ℹ️</div>
          <p className="text-sm text-blue-200/80">
            All endpoints accept the discipline slug (e.g., <code className="text-white">cs2</code>) as a path parameter.
          </p>
        </div>

        <h2 className="text-xl font-semibold text-white mb-6">Supported Disciplines</h2>

        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                <th className="py-4 px-6">ID</th>
                <th className="py-4 px-6">Name</th>
                <th className="py-4 px-6">Description</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-white/5">
              {disciplines.map((d) => (
                <tr key={d.id} className="hover:bg-white/[0.02]">
                  <td className="py-4 px-6">
                    <code className="text-emerald-400 bg-emerald-400/10 border border-emerald-500/20 px-2 py-1 rounded font-mono text-xs">
                      {d.id}
                    </code>
                  </td>
                  <td className="py-4 px-6 text-white font-medium">
                    <span className="mr-2">{d.icon}</span>{d.name}
                  </td>
                  <td className="py-4 px-6 text-zinc-400">{d.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mt-12 mb-6">Example Usage</h2>

        <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-sm mb-8">
          <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between">
            <span>Request</span>
            <span className="text-[10px] uppercase">GET</span>
          </div>
          <div className="p-4 overflow-x-auto">
            <code className="text-zinc-300">
              curl "https://backend.kashrock.com/v6/esports/<span className="text-emerald-400">cs2</span>/matches"
            </code>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-white mt-12 mb-6">Available Stats by Discipline</h2>

        <div className="space-y-6">
          {disciplines.map((d) => (
            <div key={d.id} className="bg-[#0C0D0F] border border-white/5 rounded-lg p-6">
              <h3 className="text-white font-medium mb-3">{d.icon} {d.name}</h3>
              <div className="flex flex-wrap gap-2">
                {d.stats.map((stat) => (
                  <span key={stat} className="bg-zinc-800 border border-white/10 px-2 py-1 rounded text-xs text-zinc-300 font-mono">
                    {stat}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

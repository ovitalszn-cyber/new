import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'API Reference | KashRock',
  description: 'Detailed API reference for KashRock endpoints, schemas, and models.',
};

export default function ApiReferencePage() {
  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans">
      {/* Navigation */}
      <nav className="h-14 border-b border-white/5 bg-[#050505] flex items-center px-6 justify-between sticky top-0 z-50">
        <div className="flex items-center gap-6">
          <Link href="https://backend.kashrock.com/docs" className="text-zinc-500 hover:text-white transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <span className="text-sm font-medium">API Reference</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-full border border-emerald-500/20 font-medium">v6.0.4 Stable</span>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto flex">
        {/* API Sidebar */}
        <aside className="w-72 hidden lg:block border-r border-white/5 h-[calc(100vh-56px)] sticky top-14 bg-[#050505]/50 overflow-y-auto custom-scrollbar">
          <div className="p-6">
            <div className="mb-8">
              <h3 className="text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em] mb-4">Endpoints</h3>
              <div className="space-y-1">
                <a href="#get-matches" className="group flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">
                  <span className="text-[10px] font-bold text-emerald-500 group-hover:text-emerald-400 transition-colors">GET</span>
                  Matches
                </a>
                <a href="#get-rankings" className="group flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">
                  <span className="text-[10px] font-bold text-emerald-500 group-hover:text-emerald-400 transition-colors">GET</span>
                  Rankings
                </a>
                <a href="#get-players" className="group flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">
                  <span className="text-[10px] font-bold text-emerald-500 group-hover:text-emerald-400 transition-colors">GET</span>
                  Players
                </a>
                <a href="#get-props" className="group flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">
                  <span className="text-[10px] font-bold text-emerald-500 group-hover:text-emerald-400 transition-colors">GET</span>
                  Props
                </a>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em] mb-4">Models</h3>
              <div className="space-y-1">
                <a href="#model-player" className="flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">Player</a>
                <a href="#model-match" className="flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">Match</a>
                <a href="#model-prop" className="flex items-center gap-3 px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 rounded-sm transition-all">Prop</a>
              </div>
            </div>
          </div>
        </aside>

        {/* API Docs Content */}
        <main className="flex-1 min-w-0">
          <div className="grid grid-cols-1 xl:grid-cols-2 divide-x divide-white/5">
            {/* Left Column: Documentation */}
            <div className="p-8 lg:p-12 space-y-24 pb-32">
              <section id="get-matches" className="scroll-mt-24">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs font-bold bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-sm border border-emerald-500/20">GET</span>
                  <h2 className="text-2xl font-semibold text-white tracking-tight">/v6/esports/matches</h2>
                </div>
                <p className="text-zinc-400 leading-relaxed mb-6">
                  Returns a list of matches for a specific discipline. Results include team names, scores, live status, and stream links.
                </p>
                
                <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-4">Query Parameters</h4>
                <div className="space-y-4">
                  <div className="flex gap-4 pb-4 border-b border-white/5">
                    <div className="w-32 shrink-0">
                      <code className="text-sm text-white">discipline</code>
                      <div className="text-[10px] text-zinc-600 uppercase mt-1">Required</div>
                    </div>
                    <div>
                      <div className="text-sm text-zinc-300">Target game title.</div>
                      <div className="mt-2 flex flex-wrap gap-2 text-[10px] font-mono">
                        {['cs2', 'valorant', 'lol', 'dota2'].map(d => (
                          <span key={d} className="px-1.5 py-0.5 bg-white/5 text-zinc-400 border border-white/5 rounded-sm">{d}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-4 pb-4">
                    <div className="w-32 shrink-0">
                      <code className="text-sm text-white">start_date</code>
                      <div className="text-[10px] text-zinc-600 uppercase mt-1">Optional</div>
                    </div>
                    <div className="text-sm text-zinc-300">
                      UTC date in <code className="text-white">YYYY-MM-DD</code> format. Defaults to current day.
                    </div>
                  </div>
                </div>
              </section>

              <section id="get-rankings" className="scroll-mt-24">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs font-bold bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-sm border border-emerald-500/20">GET</span>
                  <h2 className="text-2xl font-semibold text-white tracking-tight">/v6/esports/&#123;discipline&#125;/rankings</h2>
                </div>
                <p className="text-zinc-400 leading-relaxed mb-6">
                  Global player leaderboards powered by the KashRock Rating system.
                </p>
              </section>

              <section id="get-props" className="scroll-mt-24">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-xs font-bold bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-sm border border-emerald-500/20">GET</span>
                  <h2 className="text-2xl font-semibold text-white tracking-tight">/v6/props</h2>
                </div>
                <p className="text-zinc-400 leading-relaxed mb-6">
                  The primary endpoint for retrieving real-time betting props. Features unified statutory naming.
                </p>
              </section>
            </div>

            {/* Right Column: Code Samples (Sticky) */}
            <div className="bg-[#050505] p-8 lg:p-12 relative hidden xl:block">
              <div className="sticky top-28 space-y-12">
                <div>
                  <h4 className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-4">Sample Response (Match)</h4>
                  <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-6 font-mono text-[11px] leading-relaxed">
                    <pre className="text-emerald-400">
{`{
  "matches": [
    {
      "id": "kr_cs2_9941",
      "kr_match_id": "kr_cs2_9941",
      "discipline": "cs2",
      "team1": {
        "name": "Team Spirit",
        "acronym": "SPIRIT"
      },
      "team2": {
        "name": "FaZe Clan",
        "acronym": "FAZE"
      },
      "status": "upcoming",
      "start_time": "2026-04-21T18:00:00Z"
    }
  ]
}`}
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest mb-4">Integration Example</h4>
                  <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-6 font-mono text-[11px] leading-relaxed">
                    <pre className="text-zinc-400">
{`const response = await fetch(
  'backend.kashrock.com/v6/props?sport=cs2', 
  {
    headers: {
      'Authorization': 'Bearer ' + API_KEY
    }
  }
);

const data = await response.json();
console.log(data.props[0].kr_stat_type);
// Output: "CS2_KILLS_MAPS_1_2"`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

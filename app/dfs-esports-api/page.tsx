import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Enterprise Esports Data Analytics API | KashRock',
  description: 'KashRock is an enterprise esports data analytics API — normalized event schedules, market props, player game logs, outcome verification, and media with stable IDs.',
  alternates: {
    canonical: 'https://www.kashrock.com/dfs-esports-api',
  },
  keywords: [
    'esports data API',
    'DFS esports API',
    'esports player props API',
    'CS2 data API',
    'esports analytics platform',
    'esports data provider',
    'esports betting data',
    'normalized esports data',
    'esports market props',
    'player game logs API',
    'outcome verification esports',
    'esports sportsbook data',
    'KashRock API',
    'esports fixture data',
  ],
  openGraph: {
    title: 'Enterprise Esports Data Analytics API | KashRock',
    description: 'KashRock provides normalized esports analytics data: event schedules, market props, player game logs, outcome verification, and media with stable IDs.',
    url: 'https://www.kashrock.com/dfs-esports-api',
    siteName: 'KashRock',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Enterprise Esports Data Analytics API | KashRock',
    description: 'Normalized esports analytics: event schedules, market props, player game logs, outcome verification, and media with stable IDs.',
  },
};

export default function DFSEsportsAPIPage() {
  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans selection:bg-white/20">
      <div className="max-w-4xl mx-auto px-6 py-24">

        {/* Hero */}
        <div className="mb-20">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-sm text-emerald-400 text-xs font-medium mb-6">
            Enterprise Grade Infrastructure
          </div>
          <h1 className="text-4xl font-semibold tracking-tight text-white mb-6">
            The Source of Truth for Esports Data.
          </h1>
          <p className="text-lg text-zinc-400 leading-relaxed max-w-2xl mb-10">
            KashRock isn&apos;t just an aggregator. We are a high-throughput normalization engine that transforms fragmented sportsbook and provider data into a single, deterministic stream of truth.
          </p>
          <div className="flex gap-3">
            <a href="/console" className="px-4 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors">
              Get API Key
            </a>
            <a href="/docs" className="px-4 py-2 bg-[#0C0D0F] border border-white/10 text-[#E3E5E7] text-sm font-medium rounded-sm hover:bg-white/5 transition-colors">
              Read Docs
            </a>
          </div>
        </div>

        <hr className="border-white/5 mb-20" />

        {/* Core Pillars */}
        <section id="features" className="mb-20 scroll-mt-24">
          <h2 className="text-2xl font-semibold text-white mb-2">Infrastructure</h2>
          <p className="text-sm text-zinc-500 mb-8">The three layers that make KashRock reliable at scale.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-6 bg-[#0C0D0F] border border-white/5 rounded-md">
              <div className="h-8 w-8 bg-emerald-500/10 border border-emerald-500/20 rounded-sm flex items-center justify-center text-emerald-500 mb-4">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
              </div>
              <h3 className="text-sm font-semibold text-white mb-2">Deterministic IDs</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Our <code className="text-emerald-400">kr_</code> ID system uses cryptographic hashing so a FaZe vs NaVi match is identified identically across every book and provider. No duplicate fixtures.
              </p>
            </div>

            <div className="p-6 bg-[#0C0D0F] border border-white/5 rounded-md">
              <div className="h-8 w-8 bg-emerald-500/10 border border-emerald-500/20 rounded-sm flex items-center justify-center text-emerald-500 mb-4">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <h3 className="text-sm font-semibold text-white mb-2">Live Scoring Pipeline</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Round-by-round ingestion from multiple primary sources. Player stats update faster than most broadcast streams can keep up with.
              </p>
            </div>

            <div className="p-6 bg-[#0C0D0F] border border-white/5 rounded-md">
              <div className="h-8 w-8 bg-emerald-500/10 border border-emerald-500/20 rounded-sm flex items-center justify-center text-emerald-500 mb-4">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
              </div>
              <h3 className="text-sm font-semibold text-white mb-2">Unified Props Registry</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                1,000+ stat types normalized into one schema. Filter by player, book, or stat across PrizePicks, Underdog, Sleeper, and more.
              </p>
            </div>
          </div>
        </section>

        <hr className="border-white/5 mb-20" />

        {/* Verification Engine */}
        <section id="verification" className="mb-20 scroll-mt-24">
          <h2 className="text-2xl font-semibold text-white mb-2">Outcome Verification Engine</h2>
          <p className="text-sm text-zinc-500 mb-8">
            KashRock automates the full lifecycle of a prop: scheduled &rarr; live &rarr; completed &rarr; verified.
          </p>

          <div className="bg-[#0C0D0F] border border-white/5 rounded-md overflow-hidden">
            <div className="grid grid-cols-1 lg:grid-cols-2">
              <div className="p-8 border-b lg:border-b-0 lg:border-r border-white/5">
                <ul className="space-y-4">
                  {[
                    "Anti-fraud validation on final scores",
                    "Deterministic Push logic for retired/DNP players",
                    "Canonical stat mapping (Kills + Assists + Deaths)",
                    "Sub-second verification on match completion",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-3 text-sm text-zinc-300">
                      <span className="text-emerald-500 mt-0.5 shrink-0">—</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-8 space-y-3">
                <div className="bg-[#08090A] border border-white/5 rounded-md p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-mono text-zinc-500">eventId: kr_event_3910</span>
                    <span className="px-2 py-0.5 bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 text-[10px] font-medium rounded-sm">LIVE</span>
                  </div>
                  <div className="text-sm font-medium text-white">FaZe vs NaVi</div>
                  <div className="text-xs text-zinc-500 mt-0.5">Current Score: 12 — 9</div>
                </div>
                <div className="bg-[#08090A] border border-emerald-500/20 rounded-md p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-mono text-zinc-500">propId: kr_prop_5992</span>
                    <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-medium rounded-sm">HIT</span>
                  </div>
                  <div className="flex justify-between items-end">
                    <div>
                      <div className="text-sm text-white">s1mple — Over 21.5 Kills</div>
                      <div className="text-xs text-zinc-500 mt-0.5">Actual: 24</div>
                    </div>
                    <div className="text-emerald-400 text-xs font-mono font-medium">VERIFIED</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <hr className="border-white/5 mb-20" />

        {/* API Response */}
        <section id="api" className="mb-20 scroll-mt-24">
          <div className="flex flex-col md:flex-row gap-4 items-start justify-between mb-8">
            <div>
              <h2 className="text-2xl font-semibold text-white mb-2">Player Props Endpoint</h2>
              <p className="text-sm text-zinc-500">Full lifecycle player prop data with hit/miss tracking built in.</p>
            </div>
            <span className="px-3 py-1 bg-white/5 border border-white/5 rounded-sm text-xs font-mono text-zinc-400 shrink-0">GET /v6/esports/&#123;discipline&#125;/props</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <div className="lg:col-span-3">
              <div className="bg-[#0C0D0F] border border-white/5 rounded-md overflow-hidden">
                <div className="bg-white/5 px-4 py-2 border-b border-white/5 flex justify-between items-center">
                  <span className="text-zinc-500 text-xs">JSON</span>
                  <span className="text-[10px] font-mono text-zinc-600">response_v6_props.json</span>
                </div>
                <div className="p-6 font-mono text-xs overflow-x-auto leading-loose">
                  <pre>
                    <code>{`{
  "source": `}<span className="text-emerald-400">&quot;kashrock&quot;</span>{`,
  "sport": `}<span className="text-emerald-400">&quot;cs2&quot;</span>{`,
  "props": [
    {
      "prop_id": `}<span className="text-emerald-400">&quot;kr_prop_5992b0df9d7afc33&quot;</span>{`,
      "player_name": `}<span className="text-emerald-400">&quot;fear&quot;</span>{`,
      "stat_type": `}<span className="text-emerald-400">&quot;ESPORTS_KILLS_MAPS_1_2&quot;</span>{`,
      "prop_value": 25.5,
      "direction": `}<span className="text-emerald-400">&quot;over&quot;</span>{`,
      "actual_value": 28,
      "status": `}<span className="text-emerald-400 font-semibold">&quot;hit&quot;</span>{`,
      "team": `}<span className="text-emerald-400">&quot;Fnatic&quot;</span>{`,
      "opponent": `}<span className="text-emerald-400">&quot;G2&quot;</span>{`,
      "event_time": `}<span className="text-emerald-400">&quot;2026-04-21T13:30:00Z&quot;</span>{`,
      "verification_id": `}<span className="text-emerald-400">&quot;v_94401a&quot;</span>{`
    }
  ]
}`}</code>
                  </pre>
                </div>
              </div>
            </div>

            <div className="lg:col-span-2 space-y-4">
              <div className="p-5 bg-[#0C0D0F] border border-white/5 rounded-md">
                <h4 className="text-sm font-semibold text-white mb-2">Why it matters</h4>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Raw provider APIs only show active markets. KashRock tracks a prop through its entire lifecycle, so you can build bet-trackers and leaderboards without writing your own scoring engine.
                </p>
              </div>
              <div className="p-5 bg-[#0C0D0F] border border-white/5 rounded-md">
                <h4 className="text-sm font-semibold text-white mb-2">Historical Backfilling</h4>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Every prop is indexed against our player game logs. Query the last 2 years of props for any player to build hit-rate benchmarks or predictive models.
                </p>
              </div>
            </div>
          </div>
        </section>

        <hr className="border-white/5 mb-20" />

        {/* FAQ */}
        <section className="mb-20">
          <h2 className="text-2xl font-semibold text-white mb-8">Frequently asked questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { q: "Which esports games are supported?", a: "All major Tier-1 titles including CS2, League of Legends, Dota 2, and Valorant, along with emerging titles like Rainbow Six and Apex Legends." },
              { q: "How fast is the verification?", a: "Verification finalizes within 60–120 seconds of match completion, as soon as official scores are confirmed by our primary providers." },
              { q: "Can I filter by sportsbook source?", a: "Yes. Every projection includes provider metadata, so you can filter by PrizePicks, Underdog, Sleeper, and 10+ other sources." },
              { q: "Do you provide player headshots and team logos?", a: "Yes. Every player and team in our database has media assets served from our CDN — no scraping or third-party image hosting required." }
            ].map((faq) => (
              <div key={faq.q} className="bg-[#0C0D0F] border border-white/5 rounded-md p-6 hover:bg-white/[0.02] transition-colors">
                <h3 className="text-sm font-semibold text-white mb-2">{faq.q}</h3>
                <p className="text-sm text-zinc-500 leading-relaxed">{faq.a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="bg-[#0C0D0F] border border-white/5 rounded-md p-10 text-center">
          <h2 className="text-2xl font-semibold text-white mb-3">Start building on truth.</h2>
          <p className="text-sm text-zinc-400 mb-8 max-w-md mx-auto">
            Get your production API key and stop worrying about data normalization.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a href="/console" className="px-6 py-2.5 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors">
              Get API Key
            </a>
            <a href="/docs" className="px-6 py-2.5 bg-[#08090A] border border-white/10 text-[#E3E5E7] text-sm font-medium rounded-sm hover:bg-white/5 transition-colors">
              Explore Reference
            </a>
          </div>
        </section>

      </div>
    </div>
  );
}


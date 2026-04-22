import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'API Documentation | KashRock',
  description: 'Official API documentation for KashRock esports data and unified props.',
};

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans selection:bg-white/20">
      {/* Navigation Header */}
      <header className="h-16 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md sticky top-0 z-50 flex items-center px-6 justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <img src="/kashrock-logo.svg" alt="KashRock" className="h-5 w-auto" />
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="/console" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Console</Link>
            <span className="text-sm font-medium text-zinc-600 cursor-default">Products</span>
          </nav>
        </div>
        <Link href="/console" className="text-xs bg-white text-black px-3 py-1.5 rounded-sm font-medium hover:bg-zinc-200 transition-colors">
          Get Started
        </Link>
      </header>

      <div className="max-w-7xl mx-auto flex">
        {/* Sidebar */}
        <aside className="w-64 hidden lg:block border-r border-white/5 h-[calc(100vh-64px)] sticky top-16 p-6 overflow-y-auto">
          <div className="space-y-8">
            <section>
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Introduction</h3>
              <ul className="space-y-3">
                <li><a href="#quick-start" className="text-sm text-white hover:text-white transition-colors">Quick Start</a></li>
                <li><a href="#authentication" className="text-sm text-zinc-400 hover:text-white transition-colors">Authentication</a></li>
              </ul>
            </section>
            
            <section>
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Endpoints</h3>
              <ul className="space-y-3">
                <li><Link href="/docs/endpoints/matches" className="text-sm text-zinc-400 hover:text-white transition-colors">Matches</Link></li>
                <li><Link href="/docs/endpoints/rankings" className="text-sm text-zinc-400 hover:text-white transition-colors">Rankings</Link></li>
                <li><Link href="/docs/endpoints/players" className="text-sm text-zinc-400 hover:text-white transition-colors">Players</Link></li>
                <li><Link href="/docs/endpoints/props" className="text-sm text-zinc-400 hover:text-white transition-colors">Props</Link></li>
              </ul>
            </section>

            <section>
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Reference</h3>
              <ul className="space-y-3">
                <li><Link href="/docs/reference/disciplines" className="text-sm text-zinc-400 hover:text-white transition-colors">Disciplines</Link></li>
                <li><Link href="/docs/reference/sportsbooks" className="text-sm text-zinc-400 hover:text-white transition-colors">Sportsbooks</Link></li>
                <li><Link href="/docs/markets" className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors">Active Markets</Link></li>
              </ul>
            </section>

            <section>
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Resources</h3>
              <ul className="space-y-3">
                <li><a href="#id-system" className="text-sm text-zinc-400 hover:text-white transition-colors">ID System</a></li>
                <li><a href="#errors" className="text-sm text-zinc-400 hover:text-white transition-colors">Error Codes</a></li>
              </ul>
            </section>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 px-6 lg:px-12 py-12 max-w-4xl">
          <div className="mb-12">
            <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Esports Data Analytics API</h1>
            <p className="text-lg text-zinc-400 leading-relaxed mb-8">
              KashRock is an enterprise esports data analytics platform — normalized event schedules, market props, player game logs, outcome verification, and media with stable IDs.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
              <div>
                <h3 className="text-white font-semibold mb-2">Event Schedules</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">Upcoming, live, and completed esports event schedules with normalized data structures.</p>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-2">Market Props</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">Normalized statistical metrics and market props across all major esports titles and data providers.</p>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-2">Player Game Logs</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">Comprehensive player statistics and historical performance data.</p>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-2">Outcome Verification</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">Automated data integrity checks (verified/unmatched/push) for all statistical props with result processing.</p>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-2">Player headshots + team logos</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">High-quality media assets for all players and teams across every supported title.</p>
              </div>
            </div>
          </div>

          <hr className="border-white/5 mb-16" />

          {/* Quick Start */}
          <section id="quick-start" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Quick Start</h2>
            <p className="text-zinc-400 mb-6">Use any standard HTTP client to access our endpoints. All requests must be made over HTTPS.</p>
            
            <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-sm">
              <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between items-center">
                <span>cURL</span>
                <span className="text-[10px] uppercase">GET</span>
              </div>
              <div className="p-4 overflow-x-auto">
                <code className="text-zinc-300">
                  curl -H "Authorization: Bearer <span className="text-white">YOUR_API_KEY</span>" \<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"https://backend.kashrock.com/v6/esports/matches?discipline=cs2"
                </code>
              </div>
            </div>
          </section>

          {/* Authentication */}
          <section id="authentication" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Authentication</h2>
            <p className="text-zinc-400 mb-6">
              KashRock uses API keys to authenticate requests. You can view and manage your API keys in the 
              <Link href="/console/keys" className="text-white hover:underline underline-offset-4 mx-1">Console</Link>.
            </p>
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-md p-4 flex gap-4">
              <div className="text-blue-500 shrink-0">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm text-blue-200/80 leading-relaxed">
                Your API keys carry significant privileges. Please keep them secure and do not share them in publicly accessible areas such as GitHub or client-side code.
              </p>
            </div>
          </section>

          {/* Fixtures */}
          <section id="fixtures" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Fixtures</h2>
            <p className="text-zinc-400 mb-6">Retrieve live and scheduled fixtures across all supported esports disciplines.</p>

            <div className="overflow-x-auto mb-8 border border-white/5 rounded-lg">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500 font-medium">
                  <tr>
                    <th className="px-4 py-3 border-b border-white/5">Param</th>
                    <th className="px-4 py-3 border-b border-white/5">Type</th>
                    <th className="px-4 py-3 border-b border-white/5">Description</th>
                  </tr>
                </thead>
                <tbody className="text-zinc-400 divide-y divide-white/5">
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">sport</td>
                    <td className="px-4 py-3 italic">string</td>
                    <td className="px-4 py-3">One of: <code className="text-white">cs2</code>, <code className="text-white">valorant</code>, <code className="text-white">lol</code>, <code className="text-white">dota2</code></td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">status</td>
                    <td className="px-4 py-3 italic">string</td>
                    <td className="px-4 py-3">Filter by status: <code className="text-white">upcoming</code>, <code className="text-white">live</code>, <code className="text-white">finished</code></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden">
              <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between items-center text-xs">
                <span>GET /v6/esports/cs2/fixtures</span>
                <span className="text-[10px] uppercase">200 OK</span>
              </div>
              <div className="p-5 font-mono text-xs leading-relaxed overflow-x-auto">
                <code><span className="text-white">{"{"}</span>{`
`}  <span className="token-key">"source"</span>: <span className="token-string">"kashrock"</span>,{`
`}  <span className="token-key">"sport"</span>: <span className="token-string">"cs2"</span>,{`
`}  <span className="token-key">"fixtures"</span>: <span className="text-white">[</span>{`
`}    <span className="text-white">{"{"}</span>{`
`}      <span className="token-key">"fixture_id"</span>: <span className="token-string">"fix_1447265"</span>,{`
`}      <span className="token-key">"discipline"</span>: <span className="token-string">"cs2"</span>,{`
`}      <span className="token-key">"status"</span>: <span className="token-string">"finished"</span>,{`
`}      <span className="token-key">"event_time"</span>: <span className="token-string">"2026-04-19T21:03:37Z"</span>,{`
`}      <span className="token-key">"competition"</span>: <span className="token-string">"CCT South America"</span>,{`
`}      <span className="token-key">"team1"</span>: <span className="token-string">"Vasco Esports"</span>,{`
`}      <span className="token-key">"team2"</span>: <span className="token-string">"UNO MILLE"</span>,{`
`}      <span className="token-key">"score1"</span>: <span className="token-number">0</span>,{`
`}      <span className="token-key">"score2"</span>: <span className="token-number">2</span>,{`
`}      <span className="token-key">"best_of"</span>: <span className="token-number">3</span>,{`
`}      <span className="token-key">"has_streams"</span>: <span className="token-boolean">true</span>,{`
`}      <span className="token-key">"streams"</span>: <span className="text-white">[</span>{`
`}        <span className="text-white">{"{"}</span>{`
`}          <span className="token-key">"language"</span>: <span className="token-string">"en"</span>,{`
`}          <span className="token-key">"raw_url"</span>: <span className="token-string">"https://kick.com/cct_cs6"</span>,{`
`}          <span className="token-key">"official"</span>: <span className="token-boolean">true</span>{`
`}        <span className="text-white">{"}"}</span>{`
`}      <span className="text-white">]</span>{`
`}    <span className="text-white">{"}"}</span>{`
`}  <span className="text-white">]</span>{`
`}<span className="text-white">{"}"}</span></code>
              </div>
            </div>
          </section>

          {/* Rankings */}
          <section id="rankings" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Rankings</h2>
            <p className="text-zinc-400 mb-6">Current player rankings for a given discipline, sourced and normalized by KashRock.</p>

            <div className="overflow-x-auto mb-8 border border-white/5 rounded-lg">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500 font-medium">
                  <tr>
                    <th className="px-4 py-3 border-b border-white/5">Param</th>
                    <th className="px-4 py-3 border-b border-white/5">Type</th>
                    <th className="px-4 py-3 border-b border-white/5">Description</th>
                  </tr>
                </thead>
                <tbody className="text-zinc-400 divide-y divide-white/5">
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">sport</td>
                    <td className="px-4 py-3 italic">string</td>
                    <td className="px-4 py-3">Required. e.g. <code className="text-white">cs2</code>, <code className="text-white">valorant</code></td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">limit</td>
                    <td className="px-4 py-3 italic">integer</td>
                    <td className="px-4 py-3">Max results to return (default 50)</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden">
              <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between items-center text-xs">
                <span>GET /v6/esports/cs2/rankings</span>
                <span className="text-[10px] uppercase">200 OK</span>
              </div>
              <div className="p-5 font-mono text-xs leading-relaxed overflow-x-auto">
                <code><span className="text-white">{"{"}</span>{`
`}  <span className="token-key">"source"</span>: <span className="token-string">"kashrock"</span>,{`
`}  <span className="token-key">"sport"</span>: <span className="token-string">"cs2"</span>,{`
`}  <span className="token-key">"rankings"</span>: <span className="text-white">[</span>{`
`}    <span className="text-white">{"{"}</span>{`
`}      <span className="token-key">"rank"</span>: <span className="token-number">1</span>,{`
`}      <span className="token-key">"player_id"</span>: <span className="token-number">3</span>,{`
`}      <span className="token-key">"nickname"</span>: <span className="token-string">"s1mple"</span>,{`
`}      <span className="token-key">"team"</span>: <span className="token-string">"NAVI"</span>,{`
`}      <span className="token-key">"rating"</span>: <span className="token-number">1.31</span>,{`
`}      <span className="token-key">"maps_played"</span>: <span className="token-number">84</span>,{`
`}      <span className="token-key">"country"</span>: <span className="token-string">"UA"</span>{`
`}    <span className="text-white">{"}"}</span>{`
`}  <span className="text-white">]</span>,{`
`}  <span className="token-key">"total"</span>: <span className="token-number">50</span>,{`
`}  <span className="token-key">"generated_at"</span>: <span className="token-string">"2026-04-20T19:00:52Z"</span>{`
`}<span className="text-white">{"}"}</span></code>
              </div>
            </div>
          </section>

          {/* Player Profile */}
          <section id="players" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Player Profile</h2>
            <p className="text-zinc-400 mb-6">Fetch a player&apos;s profile including team, performance rating, and social links.</p>

            <div className="overflow-x-auto mb-8 border border-white/5 rounded-lg">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500 font-medium">
                  <tr>
                    <th className="px-4 py-3 border-b border-white/5">Param</th>
                    <th className="px-4 py-3 border-b border-white/5">Type</th>
                    <th className="px-4 py-3 border-b border-white/5">Description</th>
                  </tr>
                </thead>
                <tbody className="text-zinc-400 divide-y divide-white/5">
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">sport</td>
                    <td className="px-4 py-3 italic">string</td>
                    <td className="px-4 py-3">Required. e.g. <code className="text-white">cs2</code></td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">limit</td>
                    <td className="px-4 py-3 italic">integer</td>
                    <td className="px-4 py-3">Max results to return</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden">
              <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between items-center text-xs">
                <span>GET /v6/esports/cs2/bo3gg/players</span>
                <span className="text-[10px] uppercase">200 OK</span>
              </div>
              <div className="p-5 font-mono text-xs leading-relaxed overflow-x-auto">
                <code><span className="text-white">{"{"}</span>{`
`}  <span className="token-key">"source"</span>: <span className="token-string">"kashrock"</span>,{`
`}  <span className="token-key">"players"</span>: <span className="text-white">[</span>{`
`}    <span className="text-white">{"{"}</span>{`
`}      <span className="token-key">"player_id"</span>: <span className="token-number">17497</span>,{`
`}      <span className="token-key">"nickname"</span>: <span className="token-string">"FalleN"</span>,{`
`}      <span className="token-key">"first_name"</span>: <span className="token-string">"Gabriel"</span>,{`
`}      <span className="token-key">"last_name"</span>: <span className="token-string">"Toledo"</span>,{`
`}      <span className="token-key">"slug"</span>: <span className="token-string">"fallen"</span>,{`
`}      <span className="token-key">"team_id"</span>: <span className="token-number">648</span>,{`
`}      <span className="token-key">"rank"</span>: <span className="token-number">86</span>,{`
`}      <span className="token-key">"six_month_avg_rating"</span>: <span className="token-number">5.51</span>,{`
`}      <span className="token-key">"country_id"</span>: <span className="token-number">14</span>,{`
`}      <span className="token-key">"social"</span>: <span className="text-white">{"{"}</span>{`
`}        <span className="token-key">"twitter"</span>: <span className="token-string">"@FalleNCS"</span>,{`
`}        <span className="token-key">"twitch"</span>: <span className="token-string">"gafallen"</span>,{`
`}        <span className="token-key">"instagram"</span>: <span className="token-string">"fallen"</span>{`
`}      <span className="text-white">{"}"}</span>{`
`}    <span className="text-white">{"}"}</span>{`
`}  <span className="text-white">]</span>{`
`}<span className="text-white">{"}"}</span></code>
              </div>
            </div>
          </section>

          {/* Props */}
          <section id="props" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Props</h2>
            <p className="text-zinc-400 mb-6">Normalized market props across 10+ sportsbooks into a single canonical system with hit/miss tracking.</p>

            <div className="overflow-x-auto mb-8 border border-white/5 rounded-lg">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500 font-medium">
                  <tr>
                    <th className="px-4 py-3 border-b border-white/5">Param</th>
                    <th className="px-4 py-3 border-b border-white/5">Type</th>
                    <th className="px-4 py-3 border-b border-white/5">Description</th>
                  </tr>
                </thead>
                <tbody className="text-zinc-400 divide-y divide-white/5">
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">sport</td>
                    <td className="px-4 py-3 italic">string</td>
                    <td className="px-4 py-3">Required. e.g. <code className="text-white">cs2</code>, <code className="text-white">valorant</code></td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">limit</td>
                    <td className="px-4 py-3 italic">integer</td>
                    <td className="px-4 py-3">Max props to return</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden mb-8">
              <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between items-center text-xs">
                <span>GET /v6/esports/props?game=cs2&date=today</span>
                <span className="text-[10px] uppercase">200 OK</span>
              </div>
              <div className="p-5 font-mono text-xs leading-relaxed overflow-x-auto">
                <code><span className="text-white">{"{"}</span>{`
`}  <span className="token-key">"source"</span>: <span className="token-string">"kashrock"</span>,{`
`}  <span className="token-key">"sport"</span>: <span className="token-string">"cs2"</span>,{`
`}  <span className="token-key">"props"</span>: <span className="text-white">[</span>{`
`}    <span className="text-white">{"{"}</span>{`
`}      <span className="token-key">"prop_id"</span>: <span className="token-string">"kr_prop_5992b0df9d7afc33"</span>,{`
`}      <span className="token-key">"player_name"</span>: <span className="token-string">"fear"</span>,{`
`}      <span className="token-key">"stat_type"</span>: <span className="token-string">"ESPORTS_KILLS_MAPS_1_2"</span>,{`
`}      <span className="token-key">"prop_value"</span>: <span className="token-number">25.5</span>,{`
`}      <span className="token-key">"direction"</span>: <span className="token-string">"over"</span>,{`
`}      <span className="token-key">"actual_value"</span>: <span className="token-number">28</span>,{`
`}      <span className="token-key">"status"</span>: <span className="token-string">"hit"</span>,{`
`}      <span className="token-key">"team"</span>: <span className="token-string">"Fnatic"</span>,{`
`}      <span className="token-key">"opponent"</span>: <span className="token-string">"G2"</span>,{`
`}      <span className="token-key">"event_time"</span>: <span className="token-string">"2026-04-21T13:30:00Z"</span>,{`
`}      <span className="token-key">"links"</span>: <span className="text-white">{"{"}</span>{`
`}        <span className="token-key">"bet"</span>: <span className="token-string">"https://app.prizepicks.com/"</span>{`
`}      <span className="text-white">{"}"}</span>{`
`}    <span className="text-white">{"}"}</span>{`
`}  <span className="text-white">]</span>{`
`}<span className="text-white">{"}"}</span></code>
              </div>
            </div>

            <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-5 flex items-start gap-4">
              <div className="shrink-0 mt-0.5 text-emerald-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              </div>
              <div>
                <p className="text-sm font-medium text-white mb-1">Active Markets Dictionary</p>
                <p className="text-sm text-zinc-400 mb-3">An exhaustive list of all officially supported stat canonicalization mappings. Use <code className="text-white">stat_type</code> identifiers when filtering props.</p>
                <Link href="/docs/markets" className="inline-flex items-center gap-1.5 text-sm text-emerald-400 hover:text-emerald-300 transition-colors font-medium">
                  View Active Markets
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                </Link>
              </div>
            </div>
          </section>

          {/* ID System */}
          <section id="id-system" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-2">ID System</h2>
            <p className="text-zinc-400 mb-8">Every prop response contains five IDs. Each operates at a different layer and serves a distinct purpose.</p>

            <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/5 text-zinc-500 font-medium">
                  <tr>
                    <th className="px-4 py-3 border-b border-white/5">Field</th>
                    <th className="px-4 py-3 border-b border-white/5">Example</th>
                    <th className="px-4 py-3 border-b border-white/5">Layer</th>
                    <th className="px-4 py-3 border-b border-white/5">Purpose</th>
                  </tr>
                </thead>
                <tbody className="text-zinc-400 divide-y divide-white/5">
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">eventId</td>
                    <td className="px-4 py-3 font-mono text-xs text-emerald-400">kr_event_dd6a...</td>
                    <td className="px-4 py-3">Match</td>
                    <td className="px-4 py-3">Canonical ID for a game. Identical across every book offering that same match — use this to group or deduplicate by event.</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">propId</td>
                    <td className="px-4 py-3 font-mono text-xs text-emerald-400">kr_prop_5992...</td>
                    <td className="px-4 py-3">Market</td>
                    <td className="px-4 py-3">Canonical ID for a player market (player + stat + line). Shared by the Over and Under — use this to compare the same bet across multiple books.</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">offerId</td>
                    <td className="px-4 py-3 font-mono text-xs text-emerald-400">kr_prop_5992..._2_over</td>
                    <td className="px-4 py-3">Selection</td>
                    <td className="px-4 py-3">Unique per book + direction. Use this as the key when tracking a specific bet selection or building a bet slip.</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">source_event_id</td>
                    <td className="px-4 py-3 font-mono text-xs text-zinc-500">evt_646491...</td>
                    <td className="px-4 py-3">Provider</td>
                    <td className="px-4 py-3">The raw event ID from the upstream provider (e.g. PrizePicks, Underdog). Useful for debugging or cross-referencing against a provider's own API.</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 font-mono text-white">source_prop_id</td>
                    <td className="px-4 py-3 font-mono text-xs text-zinc-500">prop_b60b2e...</td>
                    <td className="px-4 py-3">Provider</td>
                    <td className="px-4 py-3">The raw prop ID from the upstream provider. Allows tracing a KashRock prop back to its original source record.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-5">
              <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-3">How they relate</p>
              <p className="text-sm text-zinc-400 leading-relaxed">One <code className="text-white">eventId</code> maps to many <code className="text-white">propId</code>s (one per player market in that match). One <code className="text-white">propId</code> maps to many <code className="text-white">offerId</code>s (one per book × direction). The <code className="text-white">kr_</code> IDs are deterministic hashes, so the same match will always produce the same <code className="text-white">eventId</code> regardless of which book surfaced it.</p>
            </div>
          </section>

          {/* Error Codes */}
          <section id="errors" className="mb-20 scroll-mt-24">
            <h2 className="text-2xl font-semibold text-white mb-6">Error Codes</h2>
            <p className="text-zinc-400 mb-6">All API errors return standard HTTP status codes with a JSON body containing a <code className="text-white">detail</code> field.</p>
            <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                    <th className="py-4 px-6">Status</th>
                    <th className="py-4 px-6">Name</th>
                    <th className="py-4 px-6">Description</th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-white/5">
                  <tr>
                    <td className="py-4 px-6 font-mono text-white">401</td>
                    <td className="py-4 px-6 text-zinc-300">Unauthorized</td>
                    <td className="py-4 px-6 text-zinc-400">Missing or invalid Bearer token. Verify your API key.</td>
                  </tr>
                  <tr>
                    <td className="py-4 px-6 font-mono text-white">403</td>
                    <td className="py-4 px-6 text-zinc-300">Forbidden</td>
                    <td className="py-4 px-6 text-zinc-400">Your API key does not have permission to access this resource.</td>
                  </tr>
                  <tr>
                    <td className="py-4 px-6 font-mono text-white">422</td>
                    <td className="py-4 px-6 text-zinc-300">Validation Error</td>
                    <td className="py-4 px-6 text-zinc-400">A required parameter is missing or has an invalid value.</td>
                  </tr>
                  <tr>
                    <td className="py-4 px-6 font-mono text-white">429</td>
                    <td className="py-4 px-6 text-zinc-300">Rate Limited</td>
                    <td className="py-4 px-6 text-zinc-400">Too many requests. Slow down and retry after a short delay.</td>
                  </tr>
                  <tr>
                    <td className="py-4 px-6 font-mono text-white">503</td>
                    <td className="py-4 px-6 text-zinc-300">Service Unavailable</td>
                    <td className="py-4 px-6 text-zinc-400">Workers are re-indexing live data. Retry in 60 seconds.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Footer */}
          <footer className="mt-32 pt-12 border-t border-white/5 text-center pb-24">
            <p className="text-sm text-zinc-500">
              © 2026 KashRock Properties. Unified Data Solutions.
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}

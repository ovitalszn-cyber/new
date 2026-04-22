'use client';

import Script from 'next/script';
import { useEffect } from 'react';

export default function LandingPage() {
  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, []);

  return (
    <>
      <Script src="https://unpkg.com/lucide@latest" strategy="beforeInteractive" />
      
      <div className="antialiased selection:bg-white/20 selection:text-white" style={{ 
        fontFamily: 'Inter, sans-serif',
        backgroundColor: '#08090A',
        color: '#E3E5E7'
      }}>
        <style jsx global>{`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
          
          body { font-family: 'Inter', sans-serif; background-color: #08090A; color: #E3E5E7; }
          .glass-nav { background: rgba(8, 9, 10, 0.7); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.08); }
          .gradient-text { background: linear-gradient(to right, #ffffff, #a1a1aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
          .grid-bg { background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 40px 40px; }
          
          @keyframes marquee {
              0% { transform: translateX(0); }
              100% { transform: translateX(-50%); }
          }
          .animate-marquee {
            display: flex;
            width: max-content;
            animation: marquee 25s linear infinite;
          }
          .animate-marquee:hover {
            animation-play-state: paused;
          }
          
          .token-key { color: #A5B4FC; }
          .token-string { color: #86EFAC; }
          .token-number { color: #FCA5A5; }
          
          ::-webkit-scrollbar { width: 8px; }
          ::-webkit-scrollbar-track { background: #08090A; }
          ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
          ::-webkit-scrollbar-thumb:hover { background: #555; }
        `}</style>

        
        {/* Navbar */}
        <nav className="fixed top-0 w-full z-50 glass-nav transition-all duration-300">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center">
              <img src="/kashrock-logo.svg" alt="KashRock" className="h-10 w-auto" />
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">How it works</a>
              <a href="#pricing" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Pricing</a>
              <a href="http://localhost:3000/docs" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Docs</a>
            </div>
            <div className="flex items-center gap-4">
              <a href="/login" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">
                Log in
              </a>
              <a href="#pricing" className="bg-white text-black px-4 py-2 text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors">
                Get API Key
              </a>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative pt-24 pb-20 md:pt-40 md:pb-32 overflow-hidden">
          <div className="absolute inset-0 grid-bg opacity-30 pointer-events-none"></div>
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[100px] rounded-full pointer-events-none"></div>

          <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 mb-6 backdrop-blur-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="text-sm font-normal text-zinc-300">v6.0 Now Live: Enhanced Esports Analytics</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
              The Enterprise Infrastructure<br />
              <span className="gradient-text">for Esports Data.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
              High-performance, normalized event analytics and software licensing for developers and researchers. Stable IDs, media assets, and comprehensive coverage — no scraping required.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a href="#pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200 transition-all flex items-center justify-center gap-2">
                Get API Key <i data-lucide="arrow-right" className="w-4 h-4"></i>
              </a>
              <a href="http://localhost:3000/docs" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900 transition-all flex items-center justify-center gap-2">
                <i data-lucide="file-text" className="w-4 h-4"></i> Read Documentation
              </a>
            </div>

            <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">CS2 • LoL • Dota 2</span>
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">Live + historical matches</span>
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">Player game logs</span>
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">Outcome verification</span>
            </div>

            <div className="mt-16 text-sm text-zinc-500 font-normal">
              Multiple primary data sources + event providers supported
            </div>

            <div className="mt-8 text-center">
              <a href="/esports-data-api" className="inline-flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                Explore the Esports Data Analytics API →
              </a>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section id="features" className="py-24 max-w-7xl mx-auto px-6">
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">Everything normalized. <br /><span className="text-zinc-500">One schema to rule them all.</span></h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="col-span-1 md:col-span-2 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="relative z-10">
                <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                  <i data-lucide="globe" className="w-5 h-5 text-white"></i>
                </div>
                <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Esports Data Coverage</h3>
                <p className="text-base text-zinc-400 max-w-md leading-relaxed">
                  Event schedules, market props, and player statistical metrics for esports — unified into one normalized schema.
                </p>
              </div>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="zap" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Near-Real-Time + Historical</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                Sub-5-second refresh cycles on live match data. Pull upcoming, live, and completed matches — including box scores and game logs for any date.
              </p>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="fingerprint" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Canonical IDs (Esports)</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                Players/teams/matches are normalized across naming differences so your app never breaks.
              </p>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="bar-chart-2" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Granular Stat Depth</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                Not just &quot;who won.&quot; Map-specific kill rates, first-blood percentages, round-by-round performance — the stats pro researchers actually need.
              </p>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="brain-circuit" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Model-Ready Data</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                Clean, structured data optimized for machine learning and predictive modeling. Historical performance metrics with consistent timestamps and identifiers.
              </p>
            </div>

            <div className="col-span-1 md:col-span-2 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors flex flex-col md:flex-row gap-8 items-start md:items-center">
              <div className="flex-1">
                <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                  <i data-lucide="trending-up" className="w-5 h-5 text-white"></i>
                </div>
                <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Outcome Verification</h3>
                <p className="text-base text-zinc-400 leading-relaxed">
                  Automatically verify statistical props (matched/unmatched/push) from final stats — perfect for dashboards and model validation.
                </p>
              </div>
              <div className="w-full md:w-64 bg-[#08090A] border border-white/10 rounded-sm p-4 font-mono text-xs">
                <div className="flex justify-between mb-2 pb-2 border-b border-white/5">
                  <span className="text-zinc-500">Example</span>
                  <span className="text-zinc-500">Result</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-zinc-300">s1mple o 21.5 Kills</span>
                  <span className="text-emerald-400">VERIFIED</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-zinc-300">faker o 6.5 Assists</span>
                  <span className="text-red-400">UNMATCHED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-300">Team Total Rounds</span>
                  <span className="text-yellow-400">PUSH</span>
                </div>
              </div>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="shield-check" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">API Reliability</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                99.9% uptime with automatic failover across data sources. Built-in rate limiting and caching to protect your integrations.
              </p>
            </div>
          </div>
        </section>

        {/* Technical/Code Section */}
        <section id="how-it-works" className="py-24 bg-[#050505] border-y border-white/5">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex flex-col lg:flex-row gap-16 items-center">
              <div className="flex-1">
                <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">Built for shipping, <br />not parsing strings.</h2>
                <p className="text-lg text-zinc-500 mb-6">Consistent esports analytics schema across event schedules, market props, stats, and outcome verification.</p>
                <ul className="space-y-6">
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center shrink-0 mt-1">
                      <i data-lucide="check" className="w-3.5 h-3.5 text-white"></i>
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white">Standardized JSON</h4>
                      <p className="text-base text-zinc-500 mt-1">Consistent response shape regardless of the source provider or esports title.</p>
                    </div>
                  </li>

                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center shrink-0 mt-1">
                      <i data-lucide="check" className="w-3.5 h-3.5 text-white"></i>
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white">Cross-Source Mapping</h4>
                      <p className="text-base text-zinc-500 mt-1">Canonical IDs across players, teams, and matches for stable esports analytics.</p>
                    </div>
                  </li>
                </ul>
              </div>
              
              <div className="flex-1 w-full max-w-2xl">
                <div className="bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden shadow-2xl">
                  <div className="flex items-center px-4 py-3 border-b border-white/5 bg-white/[0.02]">
                    <div className="flex gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/50"></div>
                      <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                      <div className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/50"></div>
                    </div>
                    <div className="ml-4 text-xs font-mono text-zinc-500">GET /v6/esports/cs2/props</div>
                  </div>
                  <div className="p-5">
                    <pre className="font-mono text-xs leading-normal"><code><span className="text-white">{`{`}</span>{`
`}  <span className="token-key">"source"</span>: <span className="token-string">"kashrock"</span>,{`
`}  <span className="token-key">"sport"</span>: <span className="token-string">"cs2"</span>,{`
`}  <span className="token-key">"props"</span>: <span className="text-white">[</span>{`
`}    <span className="text-white">{`{`}</span>{`
`}      <span className="token-key">"propId"</span>: <span className="token-string">"kr_prop_5992b0df9d7afc33"</span>,{`
`}      <span className="token-key">"player_name"</span>: <span className="token-string">"fear"</span>,{`
`}      <span className="token-key">"stat_type"</span>: <span className="token-string">"ESPORTS_KILLS_MAPS_1_2"</span>,{`
`}      <span className="token-key">"line"</span>: <span className="token-number">25.5</span>,{`
`}      <span className="token-key">"odds"</span>: <span className="token-number">-118</span>,{`
`}      <span className="token-key">"direction"</span>: <span className="token-string">"over"</span>,{`
`}      <span className="token-key">"team"</span>: <span className="token-string">"Fnatic"</span>,{`
`}      <span className="token-key">"book_name"</span>: <span className="token-string">"PrizePicks"</span>,{`
`}      <span className="token-key">"event_time"</span>: <span className="token-string">"2026-04-21T13:30:00Z"</span>,{`
`}      <span className="token-key">"links"</span>: <span className="text-white">{`{`}</span>{`
`}        <span className="token-key">"market"</span>: <span className="token-string">"https://app.prizepicks.com/"</span>{`
`}      <span className="text-white">{`}`}</span>{`
`}    <span className="text-white">{`}`}</span>{`
`}  <span className="text-white">]</span>{`
`}<span className="text-white">{`}`}</span></code></pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Competitive Comparison Section */}
        <section className="py-24 max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">Why developers choose KashRock</h2>
            <p className="text-lg text-zinc-500">The granular data the big players miss, with pricing you can actually see.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-4 px-6 text-zinc-400 font-normal w-1/3">Feature</th>
                  <th className="text-center py-4 px-6 text-zinc-400 font-normal">
                    <img src="https://abiosgaming.com/img/abios-footer-logo.webp" alt="Abios" className="h-4 opacity-50 mx-auto" />
                  </th>
                  <th className="text-center py-4 px-6 text-white font-medium bg-white/[0.03] border-x border-white/10">
                    <img src="/kashrock-logo.svg" alt="KashRock" className="h-4 mx-auto" />
                  </th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Pricing', 'Opaque. "Contact Us." £10k+ quotes.', 'Transparent, flat-rate. Starts free.'],
                  ['Onboarding', 'Long sales calls + manual vetting.', 'Instant API key. Sandbox in 60 seconds.'],
                  ['Data Quality', 'Raw pass-through. Official API bugs surface in your app.', 'Normalized + validated. Multi-source fallback. Bugs caught before you see them.'],
                  ['Stat Depth', 'Surface-level: "who won."', 'Map-specific, first-blood %, round-by-round — pro-depth data.'],
                  ['Latency', 'Batch updates. Sometimes 10s+ delay.', 'Sub-5-second refresh cycles on live data.'],
                ].map(([feature, legacy, kr]) => (
                  <tr key={feature} className="border-b border-white/5 hover:bg-white/[0.01] transition-colors">
                    <td className="py-4 px-6 text-zinc-300 font-medium">{feature}</td>
                    <td className="py-4 px-6 text-zinc-500 text-center">{legacy}</td>
                    <td className="py-4 px-6 text-emerald-400 text-center bg-white/[0.02] border-x border-white/5">{kr}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-24 max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">Pricing</h2>
            <p className="text-lg text-zinc-500">Transparent, flat-rate pricing. No sales calls. Start with a free sandbox and ship when you're ready.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-white/10 bg-[#0C0D0F]">
            
            {/* Sandbox */}
            <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-zinc-700 text-zinc-200 text-xs font-medium rounded-full whitespace-nowrap">
                Free Forever
              </div>
              <div className="mb-4 mt-2">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Sandbox</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-medium text-white">$0</span>
                  <span className="text-zinc-500">/mo</span>
                </div>
                <p className="text-sm font-bold text-zinc-300 mt-2">2 requests / minute</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">CS2 data only</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Verify the schema before committing</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">No credit card required</span>
                </li>
              </ul>
              <div className="mt-auto">
                <a href="https://buy.stripe.com/00w9AT0rA8b982jas3dby04" className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block">
                  Get Sandbox Key
                </a>
              </div>
            </div>
            <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col">
              <div className="mb-4">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Hobby</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-medium text-white">$29</span>
                  <span className="text-zinc-500">/mo</span>
                </div>
                <p className="text-sm font-bold text-zinc-300 mt-2">50 requests / minute</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Esports analytics: event schedules + market props</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Player images + team logos included</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Live + historical match access</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Email support</span>
                </li>
              </ul>
              <div className="mt-auto">
                <a href="https://buy.stripe.com/6oUeVd3DMcrp5Ub8jVdby03" className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block">
                  Subscribe
                </a>
              </div>
            </div>
            
            {/* Builder - Most Popular */}
            <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-500 text-white text-xs font-medium rounded-full">
                Most Popular
              </div>
              <div className="mb-4 mt-2">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Builder</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-medium text-white">$99</span>
                  <span className="text-zinc-500">/mo</span>
                </div>
                <p className="text-sm font-bold text-zinc-300 mt-2">100 requests / minute</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Everything in Hobby</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Player game logs + box scores</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Outcome verification (verified/unmatched/push)</span>
                </li>
              </ul>
              <div className="mt-auto">
                <a href="https://buy.stripe.com/aFa3cv4HQdvt2HZcAbdby01" className="w-full px-6 py-3 bg-white text-black rounded-sm hover:bg-zinc-200 transition-colors text-center block">
                  Subscribe
                </a>
              </div>
            </div>

            {/* Pro */}
            <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col">
              <div className="mb-4">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Pro</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-medium text-white">$249</span>
                  <span className="text-zinc-500">/mo</span>
                </div>
                <p className="text-sm font-bold text-zinc-300 mt-2">250 requests / minute</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Everything in Builder</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Highest throughput for production apps</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Early access to new esports expansions</span>
                </li>
              </ul>
              <div className="mt-auto">
                <a href="https://buy.stripe.com/9B6eVdeiq0IHfuL2ZBdby02" className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block">
                  Subscribe
                </a>
              </div>
            </div>

          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/5 bg-[#050505] pt-16 pb-12">
          <div className="max-w-7xl mx-auto px-6 mb-16">
            <div className="col-span-2">
              <div className="flex items-center mb-6">
                <img src="/kashrock-logo.svg" alt="KashRock" className="h-8 w-auto" />
              </div>
              <p className="text-base text-zinc-500 max-w-sm">
                The enterprise infrastructure layer for esports data analytics and software licensing.
              </p>
              <p className="text-xs text-zinc-600 max-w-sm mt-4 leading-relaxed">
                KashRock is a Data-as-a-Service (DaaS) provider. We provide research tools and data analytics for informational purposes. We are not a gambling operator and do not facilitate wagering.
              </p>
            </div>
          </div>
          <div className="max-w-7xl mx-auto px-6 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-600">© 2026 KashRock Inc. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <a href="/esports-data-api" className="text-sm text-zinc-600 hover:text-white transition-colors">Esports Data API</a>
              <a href="/legal" className="text-sm text-zinc-600 hover:text-white transition-colors">Privacy Policy</a>
              <a href="/legal?tab=terms" className="text-sm text-zinc-600 hover:text-white transition-colors">Terms of Service</a>
              <a href="https://www.instagram.com/kashrockapi/" target="_blank" rel="noopener noreferrer" className="text-zinc-600 hover:text-white transition-colors"><i data-lucide="instagram" className="w-5 h-5"></i></a>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

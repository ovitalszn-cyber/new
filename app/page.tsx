'use client';

import EsportsSocialProof from '@/components/EsportsSocialProof';
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

        {/* Public Beta Banner */}
        <div className="sticky top-0 w-full z-50 bg-gradient-to-r from-violet-600/10 via-purple-600/10 to-violet-600/10 border-b border-purple-500/20">
          <div className="max-w-7xl mx-auto px-4 md:px-6 py-2 flex flex-col md:flex-row items-center justify-center gap-1 md:gap-3">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 rounded-full">
              <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-pulse"></span>
              <span className="text-[10px] font-medium text-purple-300 uppercase tracking-wider">Public Beta</span>
            </span>
            <span className="text-xs text-zinc-400 text-center">Public Beta (Esports-first) — rapid updates weekly.</span>
          </div>
        </div>

        {/* Navbar */}
        <nav className="fixed top-[36px] w-full z-50 glass-nav transition-all duration-300">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center">
              <img src="/kashrock-logo.svg" alt="KashRock" className="h-10 w-auto" />
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">How it works</a>
              <a href="#pricing" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Pricing</a>
              <a href="https://api.kashrock.com/docs" target="_blank" rel="noopener noreferrer" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Docs</a>
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
        <section className="relative pt-40 pb-20 md:pt-56 md:pb-32 overflow-hidden">
          <div className="absolute inset-0 grid-bg opacity-30 pointer-events-none"></div>
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[100px] rounded-full pointer-events-none"></div>

          <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 mb-6 backdrop-blur-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-sm font-normal text-zinc-300">v6.0 Now Live: Enhanced Esports Projections</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
              Esports DFS API — <br />
              <span className="gradient-text">slates, props, results + grading</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
              Normalized esports data with stable IDs and media included. Build bots, dashboards, and models without scraping. Our DFS esports API provides everything you need.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a href="#pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200 transition-all flex items-center justify-center gap-2">
                Get API Key <i data-lucide="arrow-right" className="w-4 h-4"></i>
              </a>
              <a href="https://api.kashrock.com/docs" target="_blank" rel="noopener noreferrer" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900 transition-all flex items-center justify-center gap-2">
                <i data-lucide="file-text" className="w-4 h-4"></i> Read Documentation
              </a>
            </div>

            <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">CS2 • LoL • Dota 2</span>
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">Live + historical matches</span>
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">Player game logs</span>
              <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-zinc-300">Hit/Miss grading</span>
            </div>

            <div className="mt-16 text-sm text-zinc-500 font-normal">
              DFS platforms + books supported
            </div>

            <div className="mt-8 text-center">
              <a href="/dfs-esports-api" className="inline-flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                Looking for a DFS esports API? →
              </a>
            </div>
          </div>
        </section>

        {/* Logo Section */}
        <section className="border-y border-white/5 bg-[#0A0B0C] py-10">
          <div className="flex items-center justify-center gap-16 px-8">
            <img src="/logos/prizepicks.png" alt="PrizePicks" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
            <img src="/logos/underdog.png" alt="Underdog" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
            <img src="/logos/parlayplay.png" alt="ParlayPlay" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
            <img src="/logos/dabble.png" alt="Dabble" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
          </div>
        </section>

        {/* Esports Social Proof */}
        <EsportsSocialProof />

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
                <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Esports DFS Coverage</h3>
                <p className="text-base text-zinc-400 max-w-md leading-relaxed">
                  Slates, props, and player stat lines for esports DFS — unified into one schema.
                </p>
              </div>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="zap" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Live + Historical Backfill</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                Pull upcoming, live, and completed matches — including box scores and game logs for any date.
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

            <div className="col-span-1 md:col-span-2 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors flex flex-col md:flex-row gap-8 items-start md:items-center">
              <div className="flex-1">
                <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                  <i data-lucide="trending-up" className="w-5 h-5 text-white"></i>
                </div>
                <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Results Grading</h3>
                <p className="text-base text-zinc-400 leading-relaxed">
                  Automatically grade props (hit/miss/push) from final stats — perfect for dashboards and model validation.
                </p>
              </div>
              <div className="w-full md:w-64 bg-[#08090A] border border-white/10 rounded-sm p-4 font-mono text-xs">
                <div className="flex justify-between mb-2 pb-2 border-b border-white/5">
                  <span className="text-zinc-500">Example</span>
                  <span className="text-zinc-500">Result</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-zinc-300">s1mple o 21.5 Kills</span>
                  <span className="text-emerald-400">HIT</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-zinc-300">faker o 6.5 Assists</span>
                  <span className="text-red-400">MISS</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-300">Team Total Rounds</span>
                  <span className="text-yellow-400">PUSH</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Technical/Code Section */}
        <section id="how-it-works" className="py-24 bg-[#050505] border-y border-white/5">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex flex-col lg:flex-row gap-16 items-center">
              <div className="flex-1">
                <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">Built for shipping, <br />not parsing strings.</h2>
                <p className="text-lg text-zinc-500 mb-6">Consistent esports DFS schema across slates, props, stats, and grading.</p>
                <ul className="space-y-6">
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center shrink-0 mt-1">
                      <i data-lucide="check" className="w-3.5 h-3.5 text-white"></i>
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white">Standardized JSON</h4>
                      <p className="text-base text-zinc-500 mt-1">Consistent response shape regardless of the source book or sport.</p>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center shrink-0 mt-1">
                      <i data-lucide="check" className="w-3.5 h-3.5 text-white"></i>
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white">Smart Caching</h4>
                      <p className="text-base text-zinc-500 mt-1">Intelligent cache-control headers let you optimize your own polling logic.</p>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center shrink-0 mt-1">
                      <i data-lucide="check" className="w-3.5 h-3.5 text-white"></i>
                    </div>
                    <div>
                      <h4 className="text-lg font-medium text-white">Cross-Book Mapping</h4>
                      <p className="text-base text-zinc-500 mt-1">Canonical IDs across players/teams/matches for stable esports data.</p>
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
                    <div className="ml-4 text-xs font-mono text-zinc-500">GET /v6/esports/props?game=cs2&date=today&book=prizepicks</div>
                  </div>
                  <div className="p-5">
                    <pre className="font-mono text-xs leading-normal"><code><span className="text-white">{`{`}</span>{`
`}  <span className="token-key">"source"</span>: <span className="token-string">"kashrock"</span>,{`
`}  <span className="token-key">"sport"</span>: <span className="token-string">"cs2"</span>,{`
`}  <span className="token-key">"projections"</span>: <span className="text-white">[</span>{`
`}    <span className="text-white">{`{`}</span>{`
`}      <span className="token-key">"projection_id"</span>: <span className="token-string">"proj_233510"</span>,{`
`}      <span className="token-key">"player_name"</span>: <span className="token-string">"Mol011"</span>,{`
`}      <span className="token-key">"stat_type"</span>: <span className="token-string">"CS2_MAPS_1-2_KILLS"</span>,{`
`}      <span className="token-key">"line"</span>: <span className="token-number">26.5</span>,{`
`}      <span className="token-key">"direction"</span>: <span className="token-string">"over"</span>,{`
`}      <span className="token-key">"team"</span>: <span className="token-string">"AaB Elite"</span>,{`
`}      <span className="token-key">"opponent"</span>: <span className="token-string">"AMKAL"</span>,{`
`}      <span className="token-key">"event_time"</span>: <span className="token-string">"2025-11-30T09:00:00Z"</span>,{`
`}      <span className="token-key">"status"</span>: <span className="token-string">"pre_game"</span>,{`
`}      <span className="token-key">"links"</span>: <span className="text-white">{`{`}</span>{`
`}        <span className="token-key">"bet"</span>: <span className="token-string">"[redacted]"</span>{`
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

        {/* Pricing Section */}
        <section id="pricing" className="py-24 max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">Pricing</h2>
            <p className="text-lg text-zinc-500">No free plans. No trials. KashRock is for builders who are ready to ship.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-white/10 bg-[#0C0D0F]">
            
            {/* Hobby */}
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
                  <span className="text-zinc-300">Esports DFS: slates + props</span>
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
                  <span className="text-zinc-300">Results grading (hit/miss/push)</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Priority support</span>
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
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Faster support response</span>
                </li>
              </ul>
              <div className="mt-auto">
                <a href="https://buy.stripe.com/9B6eVdeiq0IHfuL2ZBdby02" className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block">
                  Subscribe
                </a>
              </div>
            </div>

            {/* Enterprise */}
            <div className="p-8 md:p-6 hover:bg-white/[0.02] transition-colors flex flex-col">
              <div className="mb-4">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Enterprise</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-medium text-white">Contact us</span>
                </div>
                <p className="text-sm text-zinc-300 mt-2">Custom limits + SLA</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Custom RPM + burst strategy</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Dedicated support + onboarding</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Contract + invoicing</span>
                </li>
                <li className="flex items-start gap-3">
                  <i data-lucide="check" className="w-5 h-5 text-emerald-500 mt-0.5 shrink-0"></i>
                  <span className="text-zinc-300">Data/licensing requests</span>
                </li>
              </ul>
              <div className="mt-auto">
                <a href="mailto:support@kashrock.com" className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block">
                  Contact
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
                The esports DFS infrastructure layer. Built for the next generation of betting tools.
              </p>
            </div>
          </div>
          <div className="max-w-7xl mx-auto px-6 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-600">© 2025 KashRock Inc. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <a href="/dfs-esports-api" className="text-sm text-zinc-600 hover:text-white transition-colors">DFS Esports API</a>
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

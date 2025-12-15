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
              0% { transform: translateX(0%); }
              100% { transform: translateX(-100%); }
          }
          .animate-marquee {
            display: flex;
            animation: marquee 20s linear infinite;
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
        <div className="fixed top-0 w-full z-50 bg-gradient-to-r from-violet-600/10 via-purple-600/10 to-violet-600/10 border-b border-purple-500/20">
          <div className="max-w-7xl mx-auto px-6 py-2 flex items-center justify-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 rounded-full">
              <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-pulse"></span>
              <span className="text-[10px] font-medium text-purple-300 uppercase tracking-wider">Public Beta</span>
            </span>
            <span className="text-xs text-zinc-400">We&apos;re in public beta — expect rapid improvements and new features weekly.</span>
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
              <a href="https://kashrock-production.up.railway.app/docs#/" target="_blank" rel="noopener noreferrer" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Docs</a>
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
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 mb-8 backdrop-blur-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-sm font-normal text-zinc-300">v6.0 Now Live: Enhanced Esports Projections</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
              The infrastructure for <br />
              <span className="gradient-text">sports betting products.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
              Aggregated odds, normalized markets, and actionable EV data. <br className="hidden md:block" />
              Build bots, dashboards, and betting apps without the data wrangling.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a href="#pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200 transition-all flex items-center justify-center gap-2">
                Start Building <i data-lucide="arrow-right" className="w-4 h-4"></i>
              </a>
              <a href="https://kashrock-production.up.railway.app/docs#/" target="_blank" rel="noopener noreferrer" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900 transition-all flex items-center justify-center gap-2">
                <i data-lucide="file-text" className="w-4 h-4"></i> Read Documentation
              </a>
            </div>

            <div className="mt-16 text-sm text-zinc-500 font-normal">
              Trusted by developers shipping tools for
            </div>
          </div>
        </section>

        {/* Logo Marquee */}
        <section className="border-y border-white/5 bg-[#0A0B0C] py-10 relative overflow-hidden">
          <div className="absolute inset-0 z-10 pointer-events-none" style={{ background: 'linear-gradient(90deg, #0A0B0C 0%, transparent 10%, transparent 90%, #0A0B0C 100%)' }}></div>
          <div className="animate-marquee">
            <div className="flex items-center gap-16 px-8 shrink-0 min-w-max">
              <img src="/logos/bet365.png" alt="bet365" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/draftkings.png" alt="DraftKings" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/fanduel.png" alt="FanDuel" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/caesars.png" alt="Caesars" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/betmgm.png" alt="BetMGM" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/pinnacle.png" alt="Pinnacle" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/hardrock.png" alt="Hard Rock" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/prizepicks.png" alt="PrizePicks" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
            </div>
            <div className="flex items-center gap-16 px-8 shrink-0 min-w-max">
              <img src="/logos/bet365.png" alt="bet365" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/draftkings.png" alt="DraftKings" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/fanduel.png" alt="FanDuel" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/caesars.png" alt="Caesars" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/betmgm.png" alt="BetMGM" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/pinnacle.png" alt="Pinnacle" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/hardrock.png" alt="Hard Rock" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
              <img src="/logos/prizepicks.png" alt="PrizePicks" className="h-10 w-10 object-contain opacity-60 hover:opacity-100 transition-opacity" />
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section id="features" className="py-24 max-w-7xl mx-auto px-6">
          <div className="mb-16">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">Everything normalized. <br /><span className="text-zinc-500">One schema to rule them all.</span></h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="col-span-1 md:col-span-2 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-40 transition-opacity">
                <i data-lucide="network" className="w-48 h-48 text-white"></i>
              </div>
              <div className="relative z-10">
                <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                  <i data-lucide="globe" className="w-5 h-5 text-white"></i>
                </div>
                <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Universal Aggregation</h3>
                <p className="text-base text-zinc-400 max-w-md leading-relaxed">
                  We ingest odds and player props from over 110+ books including offshore and US regulated markets. Access every line through a single endpoint.
                </p>
              </div>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="zap" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Sub-second Latency</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                Built on edge networks with aggressive caching. Get updates as fast as the books publish them.
              </p>
            </div>

            <div className="col-span-1 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors">
              <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                <i data-lucide="fingerprint" className="w-5 h-5 text-white"></i>
              </div>
              <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Canonical Identity</h3>
              <p className="text-base text-zinc-400 leading-relaxed">
                &quot;LeBron James&quot; on one book and &quot;L. James&quot; on another are automatically mapped to a single generic ID.
              </p>
            </div>

            <div className="col-span-1 md:col-span-2 bg-[#0C0D0F] border border-white/10 rounded-sm p-8 group hover:border-white/20 transition-colors flex flex-col md:flex-row gap-8 items-start md:items-center">
              <div className="flex-1">
                <div className="w-10 h-10 bg-white/5 rounded-sm flex items-center justify-center mb-6 border border-white/10">
                  <i data-lucide="trending-up" className="w-5 h-5 text-white"></i>
                </div>
                <h3 className="text-xl font-medium text-white mb-2 tracking-tight">Decision Layers &amp; EV</h3>
                <p className="text-base text-zinc-400 leading-relaxed">
                  Don&apos;t just get the odds. Get the edge. We pre-calculate Expected Value (EV) against sharp books like Pinnacle, so you can filter for profitable opportunities instantly.
                </p>
              </div>
              <div className="w-full md:w-64 bg-[#08090A] border border-white/10 rounded-sm p-4 font-mono text-xs">
                <div className="flex justify-between mb-2 pb-2 border-b border-white/5">
                  <span className="text-zinc-500">Market</span>
                  <span className="text-zinc-500">EV%</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-zinc-300">Curry o24.5 Pts</span>
                  <span className="text-emerald-400">+4.2%</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-zinc-300">Mahomes u2.5 TD</span>
                  <span className="text-emerald-400">+2.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-300">Jokic Triple Dbl</span>
                  <span className="text-emerald-400">+1.5%</span>
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
                      <p className="text-base text-zinc-500 mt-1">Player IDs link across books instantly for arbitrage finding.</p>
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
                    <div className="ml-4 text-xs font-mono text-zinc-500">GET /v6/props?sport=americanfootball_nfl</div>
                  </div>
                  <div className="p-5">
                    <pre className="font-mono text-xs leading-normal"><code><span className="text-white">{`{`}</span>{`
`}  <span className="token-key">&quot;source&quot;</span>: <span className="token-string">&quot;kashrock&quot;</span>,{`
`}  <span className="token-key">&quot;book_id&quot;</span>: <span className="token-number">2</span>,{`
`}  <span className="token-key">&quot;book_name&quot;</span>: <span className="token-string">&quot;DraftKings&quot;</span>,{`
`}  <span className="token-key">&quot;eventId&quot;</span>: <span className="token-string">&quot;evt_278811f43eb683e3&quot;</span>,{`
`}  <span className="token-key">&quot;propId&quot;</span>: <span className="token-string">&quot;prop_9585bdf0c70c4b54&quot;</span>,{`
`}  <span className="token-key">&quot;player_name&quot;</span>: <span className="token-string">&quot;Jay Huff&quot;</span>,{`
`}  <span className="token-key">&quot;stat_type&quot;</span>: <span className="token-string">&quot;NBA_ASSISTS&quot;</span>,{`
`}  <span className="token-key">&quot;line&quot;</span>: <span className="token-number">1.5</span>,{`
`}  <span className="token-key">&quot;odds&quot;</span>: <span className="token-number">112</span>,{`
`}  <span className="token-key">&quot;direction&quot;</span>: <span className="token-string">&quot;under&quot;</span>,{`
`}  <span className="token-key">&quot;sport&quot;</span>: <span className="token-string">&quot;basketball_nba&quot;</span>,{`
`}  <span className="token-key">&quot;team&quot;</span>: <span className="token-string">&quot;Indiana Pacers&quot;</span>,{`
`}  <span className="token-key">&quot;opponent&quot;</span>: <span className="token-string">&quot;Washington Wizards&quot;</span>,{`
`}  <span className="token-key">&quot;event_time&quot;</span>: <span className="token-string">&quot;Sun, 14 Dec 2025 20:10:00 GMT&quot;</span>,{`
`}  <span className="token-key">&quot;links&quot;</span>: <span className="text-white">{`{`}</span>{`
`}    <span className="token-key">&quot;bet&quot;</span>: <span className="token-string">&quot;https://sportsbook.draftkings.com/...&quot;</span>{`
`}  <span className="text-white">{`}`}</span>{`
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
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">KashRock Pricing</h2>
            <p className="text-lg text-zinc-500">Start for free, scale as your traffic grows.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-white/10 bg-[#0C0D0F]">
            
            <div className="p-8 md:p-10 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col">
              <div className="mb-4">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Free</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-normal text-white">$0</span>
                  <span className="text-zinc-500 text-base">/month</span>
                </div>
              </div>
              <p className="text-base text-zinc-400 mb-8">Built for testing and early integration.</p>
              <ul className="space-y-4 mb-8 flex-1">
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> 10 requests/min
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> Odds + Props (all leagues)
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="x" className="w-4 h-4 text-zinc-600 mt-1 shrink-0"></i> <span className="text-zinc-500">Does NOT include: Bet365, Pinnacle, EV props, Projections</span>
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> Discord Support
                </li>
              </ul>
              <a href="https://buy.stripe.com/aFaeVdeiq3UT6Yf57Jdby00" className="w-full py-3 border border-white/20 text-white font-medium text-sm text-center hover:bg-white hover:text-black transition-colors rounded-none">Start Free</a>
            </div>

            <div className="p-8 md:p-10 border-b md:border-b-0 md:border-r border-white/10 bg-white/[0.02] relative flex flex-col">
              <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent"></div>
              <div className="mb-4">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Starter</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-normal text-white">$99</span>
                  <span className="text-zinc-500 text-base">/month</span>
                </div>
              </div>
              <p className="text-base text-zinc-400 mb-8">Full access for serious builders.</p>
              <ul className="space-y-4 mb-8 flex-1">
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-white mt-1 shrink-0"></i> 100 requests/min
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-white mt-1 shrink-0"></i> Everything (all books incl. Bet365, all leagues, all markets, alt lines, combos)
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-white mt-1 shrink-0"></i> EV props + Projections
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-white mt-1 shrink-0"></i> Priority email/Discord support
                </li>
              </ul>
              <a href="https://buy.stripe.com/aFa3cv4HQdvt2HZcAbdby01" className="w-full py-3 bg-white text-black font-medium text-sm text-center hover:bg-zinc-200 transition-colors rounded-none">Get Started</a>
            </div>

            <div className="p-8 md:p-10 hover:bg-white/[0.02] transition-colors flex flex-col">
              <div className="mb-4">
                <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Pro</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-normal text-white">$249</span>
                  <span className="text-zinc-500 text-base">/month</span>
                </div>
              </div>
              <p className="text-base text-zinc-400 mb-8">High volume with top-tier support.</p>
              <ul className="space-y-4 mb-8 flex-1">
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> 250 requests/min
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> Everything (same as Starter)
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> EV props + Projections
                </li>
                <li className="flex items-start gap-3 text-base text-zinc-300">
                  <i data-lucide="check" className="w-4 h-4 text-zinc-500 mt-1 shrink-0"></i> Highest priority support
                </li>
              </ul>
              <a href="https://buy.stripe.com/9B6eVdeiq0IHfuL2ZBdby02" className="w-full py-3 border border-white/20 text-white font-medium text-sm text-center hover:bg-white hover:text-black transition-colors rounded-none">Get Started</a>
            </div>

          </div>
        </section>

        {/* FAQ Section */}
        <section className="py-24 max-w-3xl mx-auto px-6">
          <h2 className="text-3xl font-medium tracking-tight text-white mb-10">Common Questions</h2>
          <div className="space-y-4">
            <details className="group bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 list-none">
                <span className="text-lg font-medium text-zinc-200">Do you support Bet365 and all major books?</span>
                <span className="transition group-open:rotate-180">
                  <i data-lucide="chevron-down" className="w-5 h-5 text-zinc-500"></i>
                </span>
              </summary>
              <div className="text-zinc-400 px-6 pb-6 pt-0 text-base leading-relaxed">
                Yes. Paid plans include all books (including Bet365, Pinnacle, sharp/international, and DFS). The Free plan restricts premium books (like Bet365/Pinnacle/sharp) so you can test integration without full production access.
              </div>
            </details>
            <details className="group bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 list-none">
                <span className="text-lg font-medium text-zinc-200">How do request limits work?</span>
                <span className="transition group-open:rotate-180">
                  <i data-lucide="chevron-down" className="w-5 h-5 text-zinc-500"></i>
                </span>
              </summary>
              <div className="text-zinc-400 px-6 pb-6 pt-0 text-base leading-relaxed">
                1 API call = 1 request. Free is hard-limited (low RPM). Paid plans are not content-limited—only RPM increases by tier. If you exceed RPM you get HTTP 429 and retry after the reset.
              </div>
            </details>
            <details className="group bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 list-none">
                <span className="text-lg font-medium text-zinc-200">Are times shown in my timezone?</span>
                <span className="transition group-open:rotate-180">
                  <i data-lucide="chevron-down" className="w-5 h-5 text-zinc-500"></i>
                </span>
              </summary>
              <div className="text-zinc-400 px-6 pb-6 pt-0 text-base leading-relaxed">
                No. KashRock returns UTC (ISO-8601 with &quot;Z&quot;) for all timestamps. Your app converts to the user&apos;s local timezone for display.
              </div>
            </details>
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
                The betting infrastructure layer for the internet. Building the tools for the next generation of sports analytics.
              </p>
            </div>
            
          </div>
          <div className="max-w-7xl mx-auto px-6 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-600">© 2025 KashRock Inc. All rights reserved.</p>
            <div className="flex items-center gap-6">
              <a href="/legal" className="text-sm text-zinc-600 hover:text-white transition-colors">Privacy Policy</a>
              <a href="/legal?tab=terms" className="text-sm text-zinc-600 hover:text-white transition-colors">Terms of Service</a>
              <a href="https://x.com/kashrockapi" target="_blank" rel="noopener noreferrer" className="text-zinc-600 hover:text-white transition-colors"><i data-lucide="twitter" className="w-5 h-5"></i></a>
              <a href="https://www.instagram.com/kashrockapi/" target="_blank" rel="noopener noreferrer" className="text-zinc-600 hover:text-white transition-colors"><i data-lucide="instagram" className="w-5 h-5"></i></a>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

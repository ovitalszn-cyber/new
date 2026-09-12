'use client';

import Script from 'next/script';
import { useEffect, useState } from 'react';
import LandingAuthNav from '@/components/LandingAuthNav';
import BookMarquee from '@/components/BookMarquee';
import PricingPlans from '@/components/PricingPlans';
import { LiveCs2PropsPane } from '@/components/landing/LiveCs2PropsPane';
import { SportLogoRow } from '@/components/seo/SportLogoRow';

export default function LandingPage() {
  const [form, setForm] = useState({ fullName: '', email: '', message: '' });
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: { 'stroke-width': 1.5 }
      });
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    try {
      const res = await fetch('/api/contact', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(form) });
      const data = await res.json();
      if (res.ok) { setSent(true); setForm({ fullName:'', email:'', message:'' }); }
      else { alert(data.error || 'Something went wrong.'); }
    } catch { alert('Failed to send. Please try again.'); }
    finally { setSending(false); }
  };

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
              <a href="/features" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Features</a>
              <a href="/how-it-works" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">How it works</a>
              <a href="/pricing" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Pricing</a>
              <a href="/mcp" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">MCP</a>
              <a href="https://www.kashrock.com/docs" className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">Docs</a>
            </div>
            <div className="flex items-center gap-4">
              <LandingAuthNav />
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative pt-24 pb-8 md:pt-40 md:pb-10 overflow-hidden">
          <div className="absolute inset-0 grid-bg opacity-30 pointer-events-none"></div>
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[100px] rounded-full pointer-events-none"></div>

          <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
            
            
            <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
              Serious Esports Data.<br />
              <span className="gradient-text">Without Enterprise Pricing.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
              Pull normalized esports props, lines, match data, and player stats across CS2, League of Legends, Dota 2, and more — through one API.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a href="/pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200 transition-all flex items-center justify-center gap-2">
                Get API Key <i data-lucide="arrow-right" className="w-4 h-4"></i>
              </a>
              <a href="https://www.kashrock.com/docs" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900 transition-all flex items-center justify-center gap-2">
                <i data-lucide="file-text" className="w-4 h-4"></i> Read Documentation
              </a>
            </div>

            <BookMarquee />

            <SportLogoRow />
            
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
                  CS2, Valorant, League of Legends, Dota 2, Call of Duty, Rainbow Six, Mobile Legends, and Deadlock — normalized across event schedules, market props, player metrics, and verified outcomes.
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
                    <LiveCs2PropsPane />
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

        {/* Pricing Section — keep id for secondary in-page scroll; primary nav uses /pricing */}
        <section id="pricing" className="py-24 max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">Pricing</h2>
            <p className="text-lg text-zinc-500">Start free with CS2 props. Upgrade when you need full esports coverage, including League of Legends, Dota 2, live/historical matches, and production-scale API usage.</p>
          </div>
          <PricingPlans />
        </section>


        <footer className="border-t border-white/5 bg-[#050505] pt-16 pb-12">
          <div className="max-w-7xl mx-auto px-6 mb-10">
            <div className="flex flex-col lg:flex-row gap-12 items-start">
              <div className="flex-1 min-w-0">
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
              <div className="w-full lg:w-[460px] flex-shrink-0">
                <div className="bg-[#0C0D0F] border border-white/10 rounded-sm p-6">
                  <h3 className="text-base font-medium text-white">Contact us</h3>
                  <p className="text-sm text-zinc-500 mt-1">Building with esports data? Tell us your game, feeds, and scale — we’ll point you to the right coverage.</p>
                  <form onSubmit={handleSubmit} className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <input required className="bg-[#08090A] border border-white/10 rounded-sm px-3 py-2 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-white/20" placeholder="Full name" value={form.fullName} onChange={e => setForm({...form, fullName: e.target.value})} />
                    <input required type="email" className="bg-[#08090A] border border-white/10 rounded-sm px-3 py-2 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-white/20" placeholder="Work email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
                    <textarea required rows={2} className="sm:col-span-2 bg-[#08090A] border border-white/10 rounded-sm px-3 py-2 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-white/20 resize-none" placeholder="What are you building?" value={form.message} onChange={e => setForm({...form, message: e.target.value})} />
                    <div className="sm:col-span-2 flex items-center gap-3">
                      <button type="submit" disabled={sending} className="px-5 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors disabled:opacity-50">
                        {sending ? 'Sending...' : 'Send message'}
                      </button>
                      <span className="text-xs text-zinc-600">We reply within 2 business days.</span>
                      {sent && <span className="text-xs text-emerald-400">Sent — check your inbox.</span>}
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
          <div className="max-w-7xl mx-auto px-6 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-600">© 2026 KashRock Inc. All rights reserved.</p>
            <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
              <a href="/build-esports-app" className="text-sm text-zinc-600 hover:text-white transition-colors">Build an esports app</a>
              <a href="/quickstart" className="text-sm text-zinc-600 hover:text-white transition-colors">Quickstart</a>
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

import React from 'react';
import Link from 'next/link';
import esportsMarkets from '../../../data/esports_markets.json';

export default function MarketsPage() {
  const { markets } = esportsMarkets;

  const groupedMarkets = markets.reduce((acc, market) => {
    const game = market.game === "ESPORTS" ? "General / CS2" : market.game;
    if (!acc[game]) acc[game] = [];
    acc[game].push(market);
    return acc;
  }, {} as Record<string, typeof markets>);

  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans selection:bg-white/20">
      {/* Navigation Header */}
      <header className="h-16 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md sticky top-0 z-50 flex items-center px-6 justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <img src="/kashrock-logo.svg" alt="KashRock" className="h-5 w-auto" />
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="https://backend.kashrock.com/docs" className="text-sm font-medium text-white transition-colors">Documentation</Link>
            <Link href="/console" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">Console</Link>
            <span className="text-sm font-medium text-zinc-600 cursor-default">Products</span>
          </nav>
        </div>
        <Link href="/console" className="text-xs bg-white text-black px-3 py-1.5 rounded-sm font-medium hover:bg-zinc-200 transition-colors">
          Get Started
        </Link>
      </header>

      <div className="max-w-6xl mx-auto py-12 px-6 lg:px-12 flex gap-12">
        
        {/* Main Content */}
        <main className="flex-1">
          <div className="mb-10">
            <div className="flex items-center gap-4 mb-2">
              <Link href="https://backend.kashrock.com/docs" className="text-sm text-zinc-500 hover:text-white">&larr; Back to Docs</Link>
            </div>
            <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Active Markets Dictionary</h1>
            <p className="text-lg text-zinc-400 leading-relaxed max-w-2xl">
              An exhaustive list of all officially supported stat canonicalization mappings available in our Esports API. 
              Use these <code className="bg-zinc-800 text-emerald-400 px-1.5 py-0.5 rounded font-mono text-sm">canonical_name</code> identifiers when requesting odds and player props.
            </p>
          </div>

          <hr className="border-white/5 mb-12" />

          {Object.entries(groupedMarkets).map(([game, gameMarkets]) => (
            <div key={game} className="mb-16">
              <h2 className="text-2xl font-semibold text-white mb-6 tracking-tight flex items-center gap-3">
                <div className="w-1.5 h-6 bg-emerald-500 rounded-full"></div>
                {game} Props
              </h2>
              
              <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                      <th className="py-4 px-6 font-medium whitespace-nowrap">Market Name</th>
                      <th className="py-4 px-6 font-medium whitespace-nowrap">Canonical Identifier</th>
                      <th className="py-4 px-6 font-medium">Underlying Sportsbook Keys</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm divide-y divide-white/5">
                    {gameMarkets.map((market) => (
                      <tr key={market.id} className="hover:bg-white/[0.02] transition-colors">
                        <td className="py-4 px-6 align-top text-zinc-300 font-medium whitespace-nowrap">
                          {market.name}
                        </td>
                        <td className="py-4 px-6 align-top">
                          <code className="text-emerald-400 bg-emerald-400/10 border border-emerald-500/20 px-2 py-1 rounded font-mono text-[11px] whitespace-nowrap">
                            {market.canonical_name}
                          </code>
                        </td>
                        <td className="py-4 px-6 align-top text-zinc-400">
                          <div className="flex flex-wrap gap-2">
                            {market.sportsbooks.length > 0 ? market.sportsbooks.map(sb => (
                              <span key={sb} className="bg-[#121316] border border-white/10 px-2 py-1 rounded text-[11px] truncate max-w-xs inline-block">
                                {sb}
                              </span>
                            )) : <span className="text-zinc-600 italic">No external aliases mapped</span>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </main>
      </div>
    </div>
  );
}

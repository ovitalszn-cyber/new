'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useSession } from 'next-auth/react';

export default function UsagePage() {
  const { data: session } = useSession();
  const userName = session?.user?.name || 'User';

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
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <nav className="flex items-center text-sm font-medium text-zinc-500">
            <span className="hover:text-zinc-300 transition-colors cursor-pointer">{userName}</span>
            <span className="mx-2 text-zinc-700">/</span>
            <span className="text-white">Usage & Limits</span>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-zinc-400 hover:text-white transition-colors">
            <i data-lucide="help-circle" className="w-5 h-5"></i>
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-5xl mx-auto space-y-8">
          
          {/* Page Header */}
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Usage & Limits</h1>
              <p className="text-sm text-zinc-500">Monitor your API usage and rate limits across all endpoints.</p>
            </div>
            <div className="flex items-center gap-2">
              <select className="bg-[#0C0D0F] border border-white/5 rounded-sm px-3 py-1.5 text-xs text-white focus:outline-none focus:border-zinc-500">
                <option>Last 30 days</option>
                <option>Last 7 days</option>
                <option>Last 24 hours</option>
              </select>
            </div>
          </div>

          {/* Usage Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Total Requests</h3>
              <div className="text-2xl font-semibold text-white">42,593</div>
              <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
                <i data-lucide="trending-up" className="w-3 h-3"></i> +12.5% from last month
              </div>
            </div>
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Success Rate</h3>
              <div className="text-2xl font-semibold text-white">99.98%</div>
              <div className="text-xs text-zinc-500 mt-1">8 failed requests</div>
            </div>
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Avg Latency</h3>
              <div className="text-2xl font-semibold text-white">48ms</div>
              <div className="text-xs text-zinc-500 mt-1">P99: 156ms</div>
            </div>
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Rate Limit</h3>
              <div className="text-2xl font-semibold text-white">100/min</div>
              <div className="text-xs text-zinc-500 mt-1">Starter plan limit</div>
            </div>
          </div>

          {/* Usage Chart */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-medium text-white">Daily Request Volume</h3>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-white rounded-sm"></div>
                  <span className="text-zinc-400">Successful</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
                  <span className="text-zinc-400">Failed</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-end gap-1 h-40 w-full mb-4">
              {[40, 30, 55, 45, 75, 60, 85, 65, 90, 70, 50, 80, 95, 75, 60].map((height, i) => (
                <div key={i} className="flex-1 flex flex-col gap-0.5">
                  <div 
                    className="bg-zinc-800/50 hover:bg-zinc-600 rounded-sm transition-colors cursor-pointer" 
                    style={{ height: `${height}%` }}
                  ></div>
                  {i === 3 && <div className="bg-red-500/50 rounded-sm h-[2%]"></div>}
                </div>
              ))}
            </div>
            <div className="flex justify-between text-[10px] text-zinc-600 font-mono uppercase">
              <span>Dec 01</span>
              <span>Dec 08</span>
              <span>Dec 15</span>
            </div>
          </div>

          {/* Endpoint Breakdown */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-sm font-medium text-white">Usage by Endpoint</h3>
            </div>
            
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.02] border-b border-white/5">
                <tr>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Endpoint</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Requests</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Avg Latency</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Error Rate</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-48">Distribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-zinc-300">/v6/odds</td>
                  <td className="px-6 py-4 text-white">18,234</td>
                  <td className="px-6 py-4 text-zinc-400">42ms</td>
                  <td className="px-6 py-4 text-emerald-400">0.01%</td>
                  <td className="px-6 py-4">
                    <div className="w-full bg-zinc-800 rounded-full h-2">
                      <div className="bg-white h-2 rounded-full" style={{ width: '43%' }}></div>
                    </div>
                  </td>
                </tr>
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-zinc-300">/v6/props</td>
                  <td className="px-6 py-4 text-white">12,847</td>
                  <td className="px-6 py-4 text-zinc-400">56ms</td>
                  <td className="px-6 py-4 text-emerald-400">0.02%</td>
                  <td className="px-6 py-4">
                    <div className="w-full bg-zinc-800 rounded-full h-2">
                      <div className="bg-white h-2 rounded-full" style={{ width: '30%' }}></div>
                    </div>
                  </td>
                </tr>
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-zinc-300">/v6/ev</td>
                  <td className="px-6 py-4 text-white">8,156</td>
                  <td className="px-6 py-4 text-zinc-400">89ms</td>
                  <td className="px-6 py-4 text-emerald-400">0.00%</td>
                  <td className="px-6 py-4">
                    <div className="w-full bg-zinc-800 rounded-full h-2">
                      <div className="bg-white h-2 rounded-full" style={{ width: '19%' }}></div>
                    </div>
                  </td>
                </tr>
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-zinc-300">/v6/events</td>
                  <td className="px-6 py-4 text-white">3,356</td>
                  <td className="px-6 py-4 text-zinc-400">34ms</td>
                  <td className="px-6 py-4 text-orange-400">0.12%</td>
                  <td className="px-6 py-4">
                    <div className="w-full bg-zinc-800 rounded-full h-2">
                      <div className="bg-white h-2 rounded-full" style={{ width: '8%' }}></div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Rate Limits */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
            <h3 className="text-sm font-medium text-white mb-4">Rate Limits</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-black/30 border border-white/5 rounded-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-zinc-400">Requests per minute</span>
                  <span className="text-sm text-white">100 / min</span>
                </div>
                <div className="w-full bg-zinc-800 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
                <div className="text-xs text-zinc-500 mt-2">Current: ~45 req/min</div>
              </div>
              <div className="p-4 bg-black/30 border border-white/5 rounded-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-zinc-400">Monthly quota</span>
                  <span className="text-sm text-white">100,000 / mo</span>
                </div>
                <div className="w-full bg-zinc-800 rounded-full h-2">
                  <div className="bg-white h-2 rounded-full" style={{ width: '42.5%' }}></div>
                </div>
                <div className="text-xs text-zinc-500 mt-2">42,593 used • 57,407 remaining</div>
              </div>
            </div>
          </div>

          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link>
          </div>

        </div>
      </div>
    </>
  );
}

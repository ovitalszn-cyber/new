'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getUsageSummary, getRequestLogs } from '@/lib/api';

export default function ConsolePage() {
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [copied, setCopied] = useState(false);
  const [userName, setUserName] = useState('User');
  const [usage, setUsage] = useState<any>(null);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getUser = async () => {
      const { supabase } = await import('@/lib/supabase');
      if (!supabase) return;
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user?.user_metadata?.full_name) {
        setUserName(session.user.user_metadata.full_name);
      }
    };
    getUser();
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [usageData, logsData] = await Promise.all([
        getUsageSummary('30d'),
        getRequestLogs({ limit: 3, offset: 0 })
      ]);
      setUsage(usageData);
      setRecentLogs(logsData.logs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, [usage, recentLogs]);

  const handleCopyKey = () => {
    navigator.clipboard.writeText('pk_live_8392xk29d8f7g3h2j4k5l6m7n8p9q0r1s2t3u4v5w6x7y8z9d2a');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <nav className="flex items-center text-sm font-medium text-zinc-500">
            <span className="hover:text-zinc-300 transition-colors cursor-pointer">{userName}</span>
            <span className="mx-2 text-zinc-700">/</span>
            <span className="text-white">Overview</span>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
            <span className="text-xs font-medium text-emerald-400">All Systems Operational</span>
          </div>
          <button className="text-zinc-400 hover:text-white transition-colors relative">
            <i data-lucide="bell" className="w-5 h-5"></i>
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border-2 border-[#08090A]"></span>
          </button>
          <button className="text-zinc-400 hover:text-white transition-colors">
            <i data-lucide="help-circle" className="w-5 h-5"></i>
          </button>
        </div>
      </header>

      {/* Scrollable Dashboard Area */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          
          {/* Welcome / Context */}
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Overview</h1>
              <p className="text-sm text-zinc-500">Manage your API keys, monitor usage, and track data consumption.</p>
            </div>
            <div className="flex gap-3">
              <span className="text-xs text-zinc-500 self-center mr-2">Cycle resets in 16 days</span>
              <a href="/#pricing" className="px-3 py-1.5 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors">
                Upgrade Plan
              </a>
            </div>
          </div>

          {/* API Key Section */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-1 flex flex-col sm:flex-row items-center gap-4 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-white"></div>
            <div className="p-4 flex-1">
              <h3 className="text-sm font-medium text-white mb-1">Live API Key</h3>
              <p className="text-xs text-zinc-500">Used for production requests. Keep this secret.</p>
            </div>
            <div className="flex items-center gap-2 pr-4 w-full sm:w-auto">
              <div className="bg-black/50 border border-white/5 rounded-sm px-3 py-2 font-mono text-sm text-zinc-300 w-full sm:w-64 flex justify-between items-center">
                <span>{apiKeyVisible ? 'pk_live_8392xk29d8f7...9d2a' : 'pk_live_8392...9d2a'}</span>
                <span className="text-xs text-zinc-600">{apiKeyVisible ? 'VISIBLE' : 'HIDDEN'}</span>
              </div>
              <button 
                onClick={handleCopyKey}
                className="p-2 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-transparent hover:border-white/10" 
                title="Copy Key"
              >
                {copied ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
              </button>
              <button 
                onClick={() => setApiKeyVisible(!apiKeyVisible)}
                className="p-2 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-transparent hover:border-white/10" 
                title={apiKeyVisible ? 'Hide Key' : 'Show Key'}
              >
                <i data-lucide={apiKeyVisible ? 'eye-off' : 'eye'} className="w-4 h-4"></i>
              </button>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Usage Card */}
            <div className="col-span-1 md:col-span-2 bg-[#0C0D0F] border border-white/5 rounded-sm p-6 flex flex-col justify-between h-64">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-sm font-medium text-zinc-400">API Usage (This Month)</h3>
                  <div className="mt-2 flex items-baseline gap-2">
                    <span className="text-3xl font-semibold tracking-tight text-white">
                      {loading ? '...' : usage ? usage.total_requests.toLocaleString() : '0'}
                    </span>
                    <span className="text-sm text-zinc-500">
                      {loading ? '...' : usage ? `/ ${usage.monthly_limit || '100,000'}` : '/ 0'}
                    </span>
                  </div>
                </div>
                <div className="px-2 py-1 bg-white/5 border border-white/5 rounded-sm text-xs text-zinc-400">
                  {loading ? '...' : usage ? (usage.plan || 'Starter') : 'Unknown'}
                </div>
              </div>

              {/* Chart */}
              <div className="flex-1 flex flex-col justify-end">
                <div className="flex items-end gap-1 h-24 w-full mb-2 border-b border-white/5 pb-1">
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[40%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">2.4k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[30%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">1.8k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[55%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">3.2k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[45%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">2.9k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[75%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">4.1k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[60%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">3.5k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[85%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">5.2k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm h-[65%] chart-bar group relative">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">3.8k</div>
                  </div>
                  <div className="flex-1 bg-white hover:bg-white rounded-sm h-[90%] chart-bar group relative shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity">5.8k</div>
                  </div>
                  <div className="flex-1 bg-zinc-800/50 border border-dashed border-zinc-700/50 rounded-sm h-[50%] opacity-50"></div>
                </div>
                <div className="flex justify-between text-[10px] text-zinc-600 font-mono uppercase">
                  <span>Dec 01</span>
                  <span>Dec 15</span>
                </div>
              </div>
            </div>

            {/* Right Column Stack */}
            <div className="col-span-1 space-y-4">
              {/* Success Rate */}
              <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6 relative overflow-hidden">
                <div className="absolute right-0 top-0 p-6 opacity-5">
                  <i data-lucide="activity" className="w-16 h-16 text-white"></i>
                </div>
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Success Rate</h3>
                <div className="flex items-end gap-2">
                  <span className="text-3xl font-semibold tracking-tight text-white">
                    {loading ? '...' : usage ? 
                      (usage.total_requests > 0 ? ((usage.successful_requests / usage.total_requests) * 100).toFixed(2) : '100') + '%' 
                      : '0%'}
                  </span>
                  <span className="text-xs text-emerald-400 mb-1.5 flex items-center">
                    <i data-lucide="arrow-up-right" className="w-3 h-3 mr-0.5"></i> 0.01%
                  </span>
                </div>
                <div className="mt-4 w-full bg-zinc-800 rounded-full h-1">
                  <div className="bg-emerald-500 h-1 rounded-full w-[99%]"></div>
                </div>
              </div>

              {/* Latency */}
              <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6 relative overflow-hidden">
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Avg. Latency</h3>
                <div className="flex items-end gap-2">
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-semibold tracking-tight text-white">
                      {loading ? '...' : usage ? (usage.avg_latency_ms || '0') : '0'}
                    </span>
                    <span className="text-lg text-zinc-500 mb-1">ms</span>
                  </div>
                </div>
                <p className="text-xs text-zinc-500 mt-2">Global edge average</p>
              </div>
            </div>
          </div>

          {/* Recent Logs Table */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-white">Recent Requests</h2>
              <div className="flex gap-2">
                <div className="relative">
                  <i data-lucide="search" className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2"></i>
                  <input type="text" placeholder="Filter logs..." className="bg-[#0C0D0F] border border-white/5 rounded-sm pl-9 pr-3 py-1.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-500 w-48 transition-colors" />
                </div>
                <button className="px-3 py-1.5 bg-[#0C0D0F] border border-white/5 text-zinc-400 hover:text-white text-xs font-medium rounded-sm transition-colors flex items-center gap-2">
                  <i data-lucide="filter" className="w-3.5 h-3.5"></i> Filter
                </button>
              </div>
            </div>

            <div className="border border-white/5 rounded-sm overflow-hidden bg-[#0C0D0F]">
              <table className="w-full text-left text-sm">
                <thead className="bg-white/[0.02] border-b border-white/5">
                  <tr>
                    <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-24">Method</th>
                    <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Endpoint</th>
                    <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-32">Status</th>
                    <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-32 text-right">Latency</th>
                    <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-48 text-right">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-zinc-500 text-sm">
                        Loading...
                      </td>
                    </tr>
                  ) : error ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-red-400 text-sm">
                        {error}
                      </td>
                    </tr>
                  ) : recentLogs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-zinc-500 text-sm">
                        No recent requests
                      </td>
                    </tr>
                  ) : (
                    recentLogs.map((log, i) => (
                      <tr key={log.id} className="group hover:bg-white/[0.02] transition-colors">
                        <td className="px-6 py-3 whitespace-nowrap">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                            {log.method || 'GET'}
                          </span>
                        </td>
                        <td className="px-6 py-3 font-mono text-xs text-zinc-300">
                          {log.endpoint || '/v1/unknown'}
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap">
                          <div className="flex items-center gap-1.5">
                            <div className={`w-1.5 h-1.5 rounded-full ${
                              log.status_code >= 200 && log.status_code < 300 ? 'bg-emerald-500' : 
                              log.status_code === 429 ? 'bg-orange-500' : 'bg-red-500'
                            }`}></div>
                            <span className="text-xs text-zinc-400">
                              {log.status_code || '200'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap text-right text-xs text-zinc-400 font-mono">
                          {log.latency_ms || '0'}ms
                        </td>
                        <td className="px-6 py-3 whitespace-nowrap text-right text-xs text-zinc-500">
                          {i === 0 ? 'Just now' : i === 1 ? '1 min ago' : '2 mins ago'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
              <div className="px-6 py-3 border-t border-white/5 bg-white/[0.01] flex justify-center">
                <Link href="/console/logs" className="text-xs text-zinc-500 hover:text-white transition-colors">View all logs</Link>
              </div>
            </div>
          </div>

          {/* Footer Area */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 pt-8 border-t border-white/5">
            <div className="bg-gradient-to-br from-[#0C0D0F] to-[#08090A] border border-white/5 rounded-sm p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-purple-500/10 rounded-sm border border-purple-500/20">
                  <i data-lucide="zap" className="w-4 h-4 text-purple-400"></i>
                </div>
                <h3 className="text-sm font-medium text-white">Integration Guide</h3>
              </div>
              <p className="text-sm text-zinc-500 mb-4">Learn how to calculate Expected Value (EV) using our pre-computed edge endpoints.</p>
              <a href="https://api.kashrock.com/docs" target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-white hover:text-zinc-300 transition-colors flex items-center gap-1">
                Read Documentation <i data-lucide="arrow-right" className="w-3 h-3"></i>
              </a>
            </div>
            <div className="bg-gradient-to-br from-[#0C0D0F] to-[#08090A] border border-white/5 rounded-sm p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-blue-500/10 rounded-sm border border-blue-500/20">
                  <i data-lucide="gamepad-2" className="w-4 h-4 text-blue-400"></i>
                </div>
                <h3 className="text-sm font-medium text-white">New: Enhanced Esports Projections</h3>
              </div>
              <p className="text-sm text-zinc-500 mb-4">v6.0 brings CS:GO and LoL player props normalized across 12 major books.</p>
              <a href="/#features" className="text-xs font-medium text-white hover:text-zinc-300 transition-colors flex items-center gap-1">
                View Features <i data-lucide="arrow-right" className="w-3 h-3"></i>
              </a>
            </div>
          </div>
          
          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link> • <a href="/support" className="hover:text-zinc-400">Support</a>
          </div>

        </div>
      </div>
    </>
  );
}

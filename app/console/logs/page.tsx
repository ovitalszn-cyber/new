'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';

export default function LogsPage() {
  const { data: session } = useSession();
  const userName = session?.user?.name || 'User';
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, []);

  const logs = [
    { method: 'GET', endpoint: '/v6/props?sport=basketball_nba&player=curry', status: 200, latency: 42, time: 'Just now' },
    { method: 'GET', endpoint: '/v6/odds?sport=americanfootball_nfl&market=futures', status: 200, latency: 156, time: '1 min ago' },
    { method: 'GET', endpoint: '/v6/props?sport=esports_lol&market=projections', status: 200, latency: 89, time: '2 mins ago' },
    { method: 'POST', endpoint: '/v6/webhooks/subscribe', status: 429, latency: 12, time: '14 mins ago' },
    { method: 'GET', endpoint: '/v6/ev?sport=basketball_nba', status: 200, latency: 203, time: '18 mins ago' },
    { method: 'GET', endpoint: '/v6/odds?sport=hockey_nhl', status: 200, latency: 67, time: '23 mins ago' },
    { method: 'GET', endpoint: '/v6/props?sport=baseball_mlb&player=ohtani', status: 200, latency: 54, time: '31 mins ago' },
    { method: 'GET', endpoint: '/v6/events?sport=soccer_epl', status: 500, latency: 2034, time: '45 mins ago' },
    { method: 'GET', endpoint: '/v6/odds?sport=basketball_nba&book=draftkings', status: 200, latency: 38, time: '52 mins ago' },
    { method: 'GET', endpoint: '/v6/ev?sport=americanfootball_nfl', status: 200, latency: 178, time: '1 hour ago' },
  ];

  const filteredLogs = filter === 'all' ? logs : 
    filter === 'success' ? logs.filter(l => l.status === 200) :
    logs.filter(l => l.status !== 200);

  return (
    <>
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <nav className="flex items-center text-sm font-medium text-zinc-500">
            <span className="hover:text-zinc-300 transition-colors cursor-pointer">{userName}</span>
            <span className="mx-2 text-zinc-700">/</span>
            <span className="text-white">Logs</span>
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
        <div className="max-w-6xl mx-auto space-y-6">
          
          {/* Page Header */}
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Request Logs</h1>
              <p className="text-sm text-zinc-500">View and filter all API requests made with your keys.</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 bg-[#0C0D0F] border border-white/5 text-zinc-400 hover:text-white text-xs font-medium rounded-sm transition-colors flex items-center gap-2">
                <i data-lucide="download" className="w-3.5 h-3.5"></i> Export
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-md">
              <i data-lucide="search" className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2"></i>
              <input 
                type="text" 
                placeholder="Search by endpoint, status, or method..." 
                className="w-full bg-[#0C0D0F] border border-white/5 rounded-sm pl-10 pr-4 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-500 transition-colors" 
              />
            </div>
            <div className="flex items-center gap-1 bg-[#0C0D0F] border border-white/5 rounded-sm p-1">
              <button 
                onClick={() => setFilter('all')}
                className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${filter === 'all' ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'}`}
              >
                All
              </button>
              <button 
                onClick={() => setFilter('success')}
                className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${filter === 'success' ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'}`}
              >
                Success
              </button>
              <button 
                onClick={() => setFilter('errors')}
                className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${filter === 'errors' ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'}`}
              >
                Errors
              </button>
            </div>
            <select className="bg-[#0C0D0F] border border-white/5 rounded-sm px-3 py-2 text-xs text-white focus:outline-none focus:border-zinc-500">
              <option>Last 24 hours</option>
              <option>Last 7 days</option>
              <option>Last 30 days</option>
            </select>
          </div>

          {/* Logs Table */}
          <div className="border border-white/5 rounded-sm overflow-hidden bg-[#0C0D0F]">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.02] border-b border-white/5">
                <tr>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-24">Method</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Endpoint</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-32">Status</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-32 text-right">Latency</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-40 text-right">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredLogs.map((log, i) => (
                  <tr key={i} className="group hover:bg-white/[0.02] transition-colors cursor-pointer">
                    <td className="px-6 py-3 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                        log.method === 'GET' 
                          ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                      }`}>
                        {log.method}
                      </span>
                    </td>
                    <td className="px-6 py-3 font-mono text-xs text-zinc-300">
                      {log.endpoint}
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${
                          log.status === 200 ? 'bg-emerald-500' : 
                          log.status === 429 ? 'bg-orange-500' : 'bg-red-500'
                        }`}></div>
                        <span className="text-xs text-zinc-400">
                          {log.status === 200 ? '200 OK' : 
                           log.status === 429 ? '429 Limit' : '500 Error'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-3 whitespace-nowrap text-right text-xs text-zinc-400 font-mono">{log.latency}ms</td>
                    <td className="px-6 py-3 whitespace-nowrap text-right text-xs text-zinc-500">{log.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            <div className="px-6 py-4 border-t border-white/5 bg-white/[0.01] flex items-center justify-between">
              <span className="text-xs text-zinc-500">Showing {filteredLogs.length} of {logs.length} requests</span>
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 bg-white/5 border border-white/5 text-zinc-400 text-xs font-medium rounded-sm transition-colors hover:text-white disabled:opacity-50" disabled>
                  Previous
                </button>
                <button className="px-3 py-1.5 bg-white/5 border border-white/5 text-zinc-400 text-xs font-medium rounded-sm transition-colors hover:text-white">
                  Next
                </button>
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

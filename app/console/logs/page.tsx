'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api, LogEntry } from '@/lib/api-client';


export default function LogsPage() {
  const [userName, setUserName] = useState('User');
  const [filter, setFilter] = useState<'all' | 'success' | 'error'>('all');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;

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
    fetchLogs();
  }, [filter, offset]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const status = filter === 'all' ? undefined : filter as 'success' | 'error';
      const data = await api.getLogs({ limit, offset, status });
      setLogs(data.logs);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load logs');
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
  }, [logs, loading]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

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
                onClick={() => { setFilter('all'); setOffset(0); }}
                className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${filter === 'all' ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'}`}
              >
                All
              </button>
              <button 
                onClick={() => { setFilter('success'); setOffset(0); }}
                className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${filter === 'success' ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'}`}
              >
                Success
              </button>
              <button 
                onClick={() => { setFilter('error'); setOffset(0); }}
                className={`px-3 py-1.5 text-xs font-medium rounded-sm transition-colors ${filter === 'error' ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'}`}
              >
                Errors
              </button>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-sm p-4 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
            </div>
          )}

          {/* Logs Table */}
          {!loading && (
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
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-zinc-500 text-sm">
                      No logs found
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="group hover:bg-white/[0.02] transition-colors cursor-pointer">
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
                            log.status_code >= 200 && log.status_code < 300 ? 'bg-emerald-500' : 
                            log.status_code === 429 ? 'bg-orange-500' : 'bg-red-500'
                          }`}></div>
                          <span className="text-xs text-zinc-400">
                            {log.status_code}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-3 whitespace-nowrap text-right text-xs text-zinc-400 font-mono">{log.latency_ms}ms</td>
                      <td className="px-6 py-3 whitespace-nowrap text-right text-xs text-zinc-500">{formatTime(log.timestamp)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
            
            <div className="px-6 py-4 border-t border-white/5 bg-white/[0.01] flex items-center justify-between">
              <span className="text-xs text-zinc-500">Showing {logs.length} of {total} requests</span>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0}
                  className="px-3 py-1.5 bg-white/5 border border-white/5 text-zinc-400 text-xs font-medium rounded-sm transition-colors hover:text-white disabled:opacity-50"
                >
                  Previous
                </button>
                <button 
                  onClick={() => setOffset(offset + limit)}
                  disabled={offset + limit >= total}
                  className="px-3 py-1.5 bg-white/5 border border-white/5 text-zinc-400 text-xs font-medium rounded-sm transition-colors hover:text-white disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
          )}

          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link>
          </div>

        </div>
      </div>
    </>
  );
}

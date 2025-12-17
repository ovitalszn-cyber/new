'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { api, UsageSummary } from '@/lib/api-client';

interface UsageData {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_latency_ms: number;
  requests_by_endpoint: Record<string, number>;
  requests_by_day: Array<{ date: string; count: number }>;
}

export default function UsagePage() {
  const [userName, setUserName] = useState('User');
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [range, setRange] = useState<'24h' | '7d' | '30d'>('7d');

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
    fetchUsage();
  }, [range]);

  const fetchUsage = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('[Usage Page] Fetching usage summary for range:', range);
      const data = await api.getUsageSummary(range);
      console.log('[Usage Page] Received data:', data);
      setUsage(data);
    } catch (err) {
      console.error('[Usage Page] Error fetching usage summary:', err);
      // Try to get basic usage data as fallback
      try {
        console.log('[Usage Page] Trying fallback to basic usage endpoint');
        const basicUsage = await api.getUsage();
        console.log('[Usage Page] Basic usage data:', basicUsage);
        // Convert basic usage to summary format
        setUsage({
          total_requests: basicUsage.requests_this_month || 0,
          error_count: 0,
          error_rate: 0,
          top_endpoints: [],
          requests_per_day: [],
          range: range
        });
      } catch (fallbackErr) {
        console.error('[Usage Page] Fallback also failed:', fallbackErr);
        setError(err instanceof Error ? err.message : 'Failed to load usage data');
      }
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
  }, [usage, loading]);

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
              <select 
                value={range}
                onChange={(e) => setRange(e.target.value as '24h' | '7d' | '30d')}
                className="bg-[#0C0D0F] border border-white/5 rounded-sm px-3 py-1.5 text-xs text-white focus:outline-none focus:border-zinc-500"
              >
                <option value="30d">Last 30 days</option>
                <option value="7d">Last 7 days</option>
                <option value="24h">Last 24 hours</option>
              </select>
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

          {/* Usage Overview */}
          {!loading && usage && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Total Requests</h3>
              <div className="text-2xl font-semibold text-white">
                {usage.total_requests != null ? usage.total_requests.toLocaleString() : '0'}
              </div>
              <div className="text-xs text-zinc-500 mt-1">{range === '24h' ? 'Last 24 hours' : range === '7d' ? 'Last 7 days' : 'Last 30 days'}</div>
            </div>
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Success Rate</h3>
              <div className="text-2xl font-semibold text-white">
                {usage.total_requests && usage.total_requests > 0
                  ? (((usage.total_requests - usage.error_count) / usage.total_requests) * 100).toFixed(2)
                  : '0'}%
              </div>
              <div className="text-xs text-zinc-500 mt-1">{usage.error_count} failed requests</div>
            </div>
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Error Rate</h3>
              <div className="text-2xl font-semibold text-white">{usage.error_rate.toFixed(2)}%</div>
              <div className="text-xs text-zinc-500 mt-1">Failed request rate</div>
            </div>
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
              <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Rate Limit</h3>
              <div className="text-2xl font-semibold text-white">100/min</div>
              <div className="text-xs text-zinc-500 mt-1">Starter plan limit</div>
            </div>
          </div>
          )}

          {/* Usage Chart */}
          {!loading && usage && usage.requests_per_day && usage.requests_per_day.length > 0 && (
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-medium text-white">Daily Request Volume</h3>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-white rounded-sm"></div>
                  <span className="text-zinc-400">Requests</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-end gap-1 h-40 w-full mb-4">
              {usage.requests_per_day.map((day: any, i: number) => {
                const maxCount = Math.max(...usage.requests_per_day.map((d: any) => d.requests));
                const height = maxCount > 0 ? (day.requests / maxCount) * 100 : 0;
                return (
                  <div key={i} className="flex-1 flex flex-col gap-0.5">
                    <div 
                      className="bg-zinc-800/50 hover:bg-zinc-600 rounded-sm transition-colors cursor-pointer" 
                      style={{ height: `${height}%` }}
                      title={`${day.date}: ${day.requests} requests`}
                    ></div>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between text-[10px] text-zinc-600 font-mono uppercase">
              <span>{usage.requests_per_day[0]?.date}</span>
              <span>{usage.requests_per_day[Math.floor(usage.requests_per_day.length / 2)]?.date}</span>
              <span>{usage.requests_per_day[usage.requests_per_day.length - 1]?.date}</span>
            </div>
          </div>
          )}

          {/* Endpoint Breakdown */}
          {!loading && usage && usage.top_endpoints && usage.top_endpoints.length > 0 && (
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-sm font-medium text-white">Usage by Endpoint</h3>
            </div>
            
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.02] border-b border-white/5">
                <tr>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Endpoint</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Requests</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider w-48">Distribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {usage.top_endpoints.slice(0, 5).map((item: any) => {
                  const percentage = usage.total_requests > 0 ? (item.count / usage.total_requests) * 100 : 0;
                  return (
                    <tr key={item.endpoint} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4 font-mono text-xs text-zinc-300">{item.endpoint}</td>
                      <td className="px-6 py-4 text-white">{item.count.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <div className="w-full bg-zinc-800 rounded-full h-2">
                          <div className="bg-white h-2 rounded-full" style={{ width: `${percentage}%` }}></div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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

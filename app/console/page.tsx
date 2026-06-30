'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, UsageSummary, Usage, LogEntry, ApiKey } from '@/lib/api-client';
import { loadSessionTokens } from '@/lib/auth-storage';

export default function ConsolePage() {
  const router = useRouter();
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [copied, setCopied] = useState(false);
  const [userName, setUserName] = useState('User');
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [recentLogs, setRecentLogs] = useState<LogEntry[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [newlyCreatedPlainKey, setNewlyCreatedPlainKey] = useState<string | null>(null);
  const [keyGenerationLoading, setKeyGenerationLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [summaryResult, usageResult, logsResult, keysResult] = await Promise.allSettled([
        api.getUsageSummary('30d'),
        api.getUsage(),
        api.getLogs({ limit: 3 }),
        api.listApiKeys()
      ]);

      if (summaryResult.status === 'fulfilled') {
        setUsageSummary(summaryResult.value);
      } else {
        console.warn('[Console] Usage summary failed:', summaryResult.reason);
      }

      if (usageResult.status === 'fulfilled') {
        setUsage(usageResult.value);
      } else {
        console.warn('[Console] Usage failed:', usageResult.reason);
      }

      if (logsResult.status === 'fulfilled') {
        setRecentLogs(logsResult.value.logs || []);
      } else {
        console.warn('[Console] Logs failed:', logsResult.reason);
        setRecentLogs([]);
      }

      if (keysResult.status === 'fulfilled') {
        setApiKeys(keysResult.value.keys || []);
      } else {
        console.warn('[Console] API Keys failed:', keysResult.reason);
        setApiKeys([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const checkAuth = () => {
      const session = loadSessionTokens();
      const legacyToken = localStorage.getItem('google_id_token');
      if (!session?.accessToken && !legacyToken) {
        router.push('/login');
      }
    };
    checkAuth();
  }, [router]);

  useEffect(() => {
    const getUser = () => {
      const session = loadSessionTokens();
      const token = session?.accessToken || localStorage.getItem('google_id_token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          if (payload.name) {
            setUserName(payload.name);
          } else if (payload.email) {
            setUserName(payload.email.split('@')[0]);
          }
        } catch (e) {
          console.error('Failed to decode token:', e);
        }
      }
    };
    getUser();
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const initialKey = sessionStorage.getItem('initial_api_key');
    if (initialKey) {
      setNewlyCreatedPlainKey(initialKey);
      sessionStorage.removeItem('initial_api_key');
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const params = new URLSearchParams(window.location.search);
    const checkout = params.get('checkout');
    const sessionId = params.get('session_id');
    if (checkout !== 'success' || !sessionId) return;

    window.history.replaceState({}, document.title, '/console');

    let attempts = 0;
    const poll = async () => {
      try {
        const status = await api.getCheckoutSessionStatus(sessionId);
        if (status.api_key) {
          setNewlyCreatedPlainKey(status.api_key);
          await fetchData();
          return;
        }
        if (status.payment_status === 'paid' || status.status === 'complete') {
          await fetchData();
          return;
        }
      } catch (err) {
        console.warn('[Console] Checkout status poll failed:', err);
      }

      attempts += 1;
      if (attempts < 10) {
        setTimeout(poll, 2000);
      }
    };

    poll();
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, [usage, recentLogs, newlyCreatedPlainKey, apiKeys, keyGenerationLoading]);

  const handleCopyKey = () => {
    const firstKey = apiKeys.find(k => k.status === 'active');
    if (firstKey) {
      navigator.clipboard.writeText(firstKey.key_prefix + '...');
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleGenerateKey = async () => {
    const confirmMsg = apiKeys.length > 0
      ? "Are you sure you want to rotate your API key? Your current key will be revoked immediately."
      : "Are you sure you want to generate a new API key?";
    
    if (!window.confirm(confirmMsg)) return;

    try {
      setKeyGenerationLoading(true);
      setError(null);
      
      // Revoke any existing active keys first (normal key rotation behavior)
      const activeKeys = apiKeys.filter(k => k.status === 'active');
      for (const key of activeKeys) {
        await api.revokeApiKey(key.id);
      }
      
      // Create new key
      const result = await api.createApiKey('Default Key');
      setNewlyCreatedPlainKey(result.api_key);
      
      // Refresh key list
      const keysResult = await api.listApiKeys();
      setApiKeys(keysResult.keys || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate key');
    } finally {
      setKeyGenerationLoading(false);
    }
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
              <a href="/#pricing" className="px-3 py-1.5 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors">
                Upgrade Plan
              </a>
            </div>
          </div>

          {/* Newly Generated API Key Alert */}
          {newlyCreatedPlainKey && (
            <div className="bg-[#0f1d19] border border-emerald-500/30 rounded-sm p-5 relative overflow-hidden shadow-lg animate-in fade-in slide-in-from-top-4 duration-300">
              <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
              <div className="flex items-start justify-between">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <i data-lucide="shield-check" className="w-5 h-5 text-emerald-400"></i>
                    <h4 className="text-sm font-semibold text-emerald-400">API Key Successfully Generated!</h4>
                  </div>
                  <p className="text-xs text-zinc-400">
                    Copy this key and save it in a secure place. For security reasons, <span className="text-emerald-400 font-medium">you will not be able to see it again</span>.
                  </p>
                  <div className="bg-black/60 border border-white/10 rounded-sm px-3 py-2 font-mono text-sm text-zinc-300 w-full max-w-xl flex justify-between items-center mt-2 group/key">
                    <span className="break-all select-all font-medium text-emerald-300">{newlyCreatedPlainKey}</span>
                    <button 
                      onClick={() => {
                        navigator.clipboard.writeText(newlyCreatedPlainKey);
                        setCopied(true);
                        setTimeout(() => setCopied(false), 2000);
                      }}
                      className="p-1.5 ml-2 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-transparent hover:border-white/10 flex items-center justify-center"
                      title="Copy Key to Clipboard"
                    >
                      {copied ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
                    </button>
                  </div>
                </div>
                <button 
                  onClick={() => setNewlyCreatedPlainKey(null)}
                  className="text-zinc-500 hover:text-white p-1 hover:bg-white/5 rounded transition-colors"
                >
                  <i data-lucide="x" className="w-4.5 h-4.5"></i>
                </button>
              </div>
            </div>
          )}

          {/* API Key Section */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-1 flex flex-col sm:flex-row items-center gap-4 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-white"></div>
            <div className="p-4 flex-1">
              <h3 className="text-sm font-medium text-white mb-1">Live API Key</h3>
              <p className="text-xs text-zinc-500">Used for production requests. Keep this secret.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2.5 pr-4 w-full sm:w-auto">
              <div className="bg-black/50 border border-white/5 rounded-sm px-3 py-2 font-mono text-sm text-zinc-300 w-full sm:w-64 flex justify-between items-center">
                <span>{apiKeys.length > 0 ? (apiKeyVisible ? apiKeys[0].key_prefix : `${apiKeys[0].key_prefix.substring(0, 12)}...`) : 'No API key yet'}</span>
                <span className="text-xs text-zinc-600">{apiKeyVisible ? 'VISIBLE' : 'HIDDEN'}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button 
                  onClick={handleCopyKey}
                  disabled={apiKeys.length === 0}
                  className="p-2 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-transparent hover:border-white/10 disabled:opacity-30 disabled:cursor-not-allowed" 
                  title="Copy Key Prefix"
                >
                  {copied ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
                </button>
                <button 
                  onClick={() => setApiKeyVisible(!apiKeyVisible)}
                  disabled={apiKeys.length === 0}
                  className="p-2 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-transparent hover:border-white/10 disabled:opacity-30 disabled:cursor-not-allowed" 
                  title={apiKeyVisible ? 'Hide Key' : 'Show Key'}
                >
                  <i data-lucide={apiKeyVisible ? 'eye-off' : 'eye'} className="w-4 h-4"></i>
                </button>
                <button 
                  onClick={handleGenerateKey}
                  disabled={keyGenerationLoading}
                  className="ml-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white rounded-sm text-xs font-medium border border-white/10 hover:border-white/20 transition-all flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  title={apiKeys.length > 0 ? "Rotate API Key" : "Generate API Key"}
                >
                  <i data-lucide="refresh-cw" className={`w-3.5 h-3.5 ${keyGenerationLoading ? 'animate-spin' : ''}`}></i>
                  {keyGenerationLoading ? 'Processing...' : (apiKeys.length > 0 ? 'Rotate Key' : 'Generate Key')}
                </button>
              </div>
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
                      {loading ? '...' : usage?.requests_this_month != null ? usage.requests_this_month.toLocaleString() : '0'}
                    </span>
                    <span className="text-sm text-zinc-500">
                      {loading ? '...' : usage?.limit_month != null ? `/ ${usage.limit_month.toLocaleString()}` : '/ 0'}
                    </span>
                  </div>
                </div>
                <div className="px-2 py-1 bg-white/5 border border-white/5 rounded-sm text-xs text-zinc-400">
                  {loading ? '...' : usage ? (usage.plan || 'Free') : 'Unknown'}
                </div>
              </div>

              {/* Chart */}
              <div className="flex-1 flex flex-col justify-end">
                <div className="flex items-end gap-1 h-24 w-full mb-2 border-b border-white/5 pb-1">
                  {usageSummary && usageSummary.requests_per_day && usageSummary.requests_per_day.length > 0 ? (
                    usageSummary.requests_per_day.map((day, idx) => {
                      const maxRequests = Math.max(...usageSummary.requests_per_day.map(d => d.requests), 10);
                      const heightPercent = Math.max(5, (day.requests / maxRequests) * 100);
                      const isLast = idx === usageSummary.requests_per_day.length - 1;
                      const barClass = isLast
                        ? "flex-1 bg-white hover:bg-white rounded-sm chart-bar group relative shadow-[0_0_15px_rgba(255,255,255,0.3)]"
                        : "flex-1 bg-zinc-800/50 hover:bg-zinc-600 rounded-sm chart-bar group relative";
                      
                      return (
                        <div 
                          key={day.date} 
                          className={barClass} 
                          style={{ height: `${heightPercent}%` }}
                        >
                          <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-30">
                            {day.requests.toLocaleString()} ({new Date(day.date + 'T00:00:00Z').toLocaleDateString([], { month: 'short', day: '2-digit' })})
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-zinc-500 text-xs w-full text-center pb-4">No usage data in this range</div>
                  )}
                </div>
                <div className="flex justify-between text-[10px] text-zinc-600 font-mono uppercase">
                  <span>{usageSummary?.requests_per_day?.[0] ? new Date(usageSummary.requests_per_day[0].date + 'T00:00:00Z').toLocaleDateString([], { month: 'short', day: '2-digit' }) : 'Start'}</span>
                  <span>{usageSummary?.requests_per_day?.[usageSummary.requests_per_day.length - 1] ? new Date(usageSummary.requests_per_day[usageSummary.requests_per_day.length - 1].date + 'T00:00:00Z').toLocaleDateString([], { month: 'short', day: '2-digit' }) : 'End'}</span>
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
                    {loading ? '...' : usageSummary && usageSummary.total_requests > 0
                      ? `${(((usageSummary.total_requests - usageSummary.error_count) / usageSummary.total_requests) * 100).toFixed(2)}%`
                      : '0%'}
                  </span>
                </div>
                <div className="mt-4 w-full bg-zinc-800 rounded-full h-1">
                  <div className="bg-emerald-500 h-1 rounded-full" style={{ width: `${usageSummary && usageSummary.total_requests > 0 ? ((usageSummary.total_requests - usageSummary.error_count) / usageSummary.total_requests) * 100 : 0}%` }}></div>
                </div>
              </div>

              {/* Latency */}
              <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6 relative overflow-hidden">
                <h3 className="text-sm font-medium text-zinc-400 mb-2">Requests Today</h3>
                <div className="flex items-end gap-2">
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-semibold tracking-tight text-white">
                      {loading ? '...' : usage?.requests_today != null ? usage.requests_today.toLocaleString() : '0'}
                    </span>
                    <span className="text-lg text-zinc-500 mb-1"></span>
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
                  ) : !Array.isArray(recentLogs) || recentLogs.length === 0 ? (
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
                          {log.timestamp ? new Date(log.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : 'Just now'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Footer Area */}
          <div className="text-center text-xs text-zinc-600 mt-12 pt-8 border-t border-white/5 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link> • <a href="/support" className="hover:text-zinc-400">Support</a>
          </div>

        </div>
      </div>
    </>
  );
}

'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';

type DateRange = 'today' | '7days' | '30days' | 'custom';

interface AuthUser {
  id: string;
  email: string;
  name?: string | null;
  plan: string;
  status: string;
}

interface DashboardSession {
  token: string;
  user: AuthUser;
}

interface UsageMetrics {
  totalRequests: number;
  successfulRequests: number;
  errorRate: number;
  tier: string;
  requestsRemaining: number;
  dailyLimit: number;
  monthlyQuota: number;
}

interface EndpointUsage {
  endpoint: string;
  count: number;
  percentage: number;
}

interface RecentRequest {
  id: string;
  timestamp: string;
  endpoint: string;
  method: string;
  statusCode: number;
  latency?: number | null;
  keyId?: string;
  keyPreview?: string;
  creditsUsed?: number;
}

export default function UsagePage() {
  const router = useRouter();
  const [dateRange, setDateRange] = useState<DateRange>('7days');
  const [session, setSession] = useState<DashboardSession | null>(null);
  const [usageMetrics, setUsageMetrics] = useState<UsageMetrics | null>(null);
  const [endpointUsage, setEndpointUsage] = useState<EndpointUsage[]>([]);
  const [recentRequests, setRecentRequests] = useState<RecentRequest[]>([]);
  const [loadingUsage, setLoadingUsage] = useState(false);
  const [usageError, setUsageError] = useState<string | null>(null);

  const apiBase = useMemo(() => process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000', []);

  const dateRangeOptions: { value: DateRange; label: string }[] = [
    { value: 'today', label: 'Today' },
    { value: '7days', label: 'Last 7 Days' },
    { value: '30days', label: 'Last 30 Days' },
    { value: 'custom', label: 'Custom Range' },
  ];

  const getStatusColor = (code: number) => {
    if (!Number.isFinite(code)) return 'text-[#635F69] bg-[#EFEBF5]';
    if (code >= 200 && code < 300) return 'text-[#10B981] bg-[#10B981]/10';
    if (code >= 400 && code < 500) return 'text-[#F59E0B] bg-[#F59E0B]/10';
    return 'text-[#EF4444] bg-[#EF4444]/10';
  };

  const signOut = useCallback(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('kashrock_dashboard_session');
    }
    setSession(null);
    router.push('/dashboard');
  }, [router]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = window.localStorage.getItem('kashrock_dashboard_session');
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed?.access_token && parsed?.user) {
        setSession({ token: parsed.access_token as string, user: parsed.user as AuthUser });
      }
    } catch {
      // ignore corrupted storage
    }
  }, []);

  const fetchUsage = useCallback(
    async (rangeValue: DateRange) => {
      if (!session?.token) return;
      setLoadingUsage(true);
      setUsageError(null);
      try {
        const res = await fetch(`${apiBase}/v1/dashboard/usage?range=${rangeValue}`, {
          headers: { Authorization: `Bearer ${session.token}` },
        });
        const data = await res.json();
        if (!res.ok) {
          if (res.status === 401) {
            signOut();
            throw new Error('Session expired. Please sign in again.');
          }
          throw new Error(data?.detail || 'Failed to load usage data');
        }
        setUsageMetrics(data?.metrics ?? null);
        setEndpointUsage(Array.isArray(data?.endpointUsage) ? data.endpointUsage : []);
        setRecentRequests(Array.isArray(data?.recentRequests) ? data.recentRequests : []);
      } catch (err: any) {
        setUsageError(err?.message || 'Failed to load usage data');
      } finally {
        setLoadingUsage(false);
      }
    },
    [apiBase, session?.token, signOut],
  );

  useEffect(() => {
    if (!session?.token) return;
    fetchUsage(dateRange);
  }, [fetchUsage, session?.token, dateRange]);

  const renderAuthGuard = () => (
    <div className="max-w-md mx-auto mt-8 clay-card shadow-clay-card p-8 text-center">
      <h2
        className="text-2xl font-black text-[#332F3A] mb-3"
        style={{ fontFamily: 'Nunito, sans-serif' }}
      >
        Sign in to view usage
      </h2>
      <p className="text-sm text-[#635F69]">
        Go back to the main dashboard and complete Google Sign-In to access usage analytics.
      </p>
      <a
        href="/dashboard"
        className="inline-flex items-center justify-center mt-6 px-5 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all"
      >
        Go to Dashboard
      </a>
    </div>
  );

  const metricsDisplay = usageMetrics
    ? {
        totalRequests: usageMetrics.totalRequests.toLocaleString(),
        successfulRequests: usageMetrics.successfulRequests.toLocaleString(),
        errorRate: `${usageMetrics.errorRate.toFixed(2)}%`,
        requestsRemaining: usageMetrics.requestsRemaining.toLocaleString(),
        dailyLimit: usageMetrics.dailyLimit.toLocaleString(),
        tier: usageMetrics.tier,
      }
    : {
        totalRequests: '—',
        successfulRequests: '—',
        errorRate: '—',
        requestsRemaining: '—',
        dailyLimit: '—',
        tier: '—',
      };

  const renderUsageContent = () => (
    <>
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1
            className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            Usage
          </h1>
          <p className="text-[#635F69]">
            Monitor your API usage and performance metrics.
          </p>
        </div>

        {/* Date Range Selector */}
        <div className="flex gap-2">
          {dateRangeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setDateRange(option.value)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                dateRange === option.value
                  ? 'bg-[#7C3AED] text-white shadow-clay-button'
                  : 'bg-white text-[#635F69] shadow-clay-card hover:text-[#7C3AED]'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {usageError && (
        <div className="mb-6 px-4 py-3 rounded-xl bg-[#FEE2E2] text-[#B91C1C] text-sm">
          {usageError}
        </div>
      )}

      {loadingUsage && (
        <div className="mb-6 px-4 py-3 rounded-xl bg-[#EFEBF5] text-[#635F69] text-sm">
          Loading usage data…
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Requests"
          value={metricsDisplay.totalRequests}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
          color="purple"
        />
        <MetricCard
          title="Successful"
          value={metricsDisplay.successfulRequests}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          }
          color="green"
        />
        <MetricCard
          title="Error Rate"
          value={metricsDisplay.errorRate}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          }
          color="yellow"
        />
        <MetricCard
          title="Remaining Today"
          value={metricsDisplay.requestsRemaining}
          subtitle={
            usageMetrics
              ? `of ${usageMetrics.dailyLimit.toLocaleString()} (daily)`
              : undefined
          }
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="blue"
        />
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Request Trend - placeholder */}
        <div className="clay-card shadow-clay-card p-6">
          <h3 className="font-bold text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
            Request Trend
          </h3>
          <div className="h-48 flex items-end justify-between gap-2">
            {[65, 45, 78, 52, 90, 68, 85].map((height, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className="w-full bg-gradient-to-t from-[#7C3AED] to-[#A78BFA] rounded-t-lg transition-all duration-500 hover:from-[#6D28D9] hover:to-[#7C3AED]"
                  style={{ height: `${height}%` }}
                />
                <span className="text-xs text-[#635F69]">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Endpoint Usage */}
        <div className="clay-card shadow-clay-card p-6">
          <h3 className="font-bold text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
            Top Endpoints
          </h3>
          <div className="space-y-4">
            {endpointUsage.map((endpoint, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <code className="text-sm text-[#7C3AED] font-mono">{endpoint.endpoint}</code>
                  <span className="text-sm text-[#635F69]">{endpoint.count.toLocaleString()}</span>
                </div>
                <div className="h-2 bg-[#EFEBF5] rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-[#7C3AED] to-[#A78BFA] rounded-full transition-all duration-500"
                    style={{ width: `${endpoint.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Requests Table */}
      <div className="clay-card shadow-clay-card p-6">
        <h3 className="font-bold text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
          Recent Requests
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#E5E1EF]">
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Timestamp</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Endpoint</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Method</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Latency</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Key</th>
              </tr>
            </thead>
            <tbody>
              {recentRequests.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-sm text-[#635F69]">
                    No requests recorded in this range.
                  </td>
                </tr>
              )}
              {recentRequests.map((request) => (
                <tr key={request.id} className="border-b border-[#E5E1EF]/50 hover:bg-[#7C3AED]/5 transition-colors">
                  <td className="py-3 px-4 text-sm text-[#635F69] font-mono">{request.timestamp}</td>
                  <td className="py-3 px-4">
                    <code className="text-sm text-[#7C3AED] font-mono">{request.endpoint}</code>
                  </td>
                  <td className="py-3 px-4 text-sm text-[#635F69] uppercase">{request.method || 'GET'}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatusColor(request.statusCode)}`}>
                      {request.statusCode}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-[#635F69]">
                    {typeof request.latency === 'number' ? `${request.latency}ms` : '—'}
                  </td>
                  <td className="py-3 px-4">
                    <code className="text-xs text-[#635F69] font-mono">
                      {request.keyPreview || request.keyId || '—'}
                    </code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );

  return (
    <DashboardLayout>
      {session?.token ? renderUsageContent() : renderAuthGuard()}
    </DashboardLayout>
  );
}
// Metric Card Component
function MetricCard({ 
  title, 
  value, 
  subtitle,
  icon, 
  color 
}: { 
  title: string; 
  value: string; 
  subtitle?: string;
  icon: React.ReactNode; 
  color: 'purple' | 'green' | 'yellow' | 'blue';
}) {
  const colorClasses = {
    purple: 'from-[#A78BFA] to-[#7C3AED]',
    green: 'from-[#34D399] to-[#10B981]',
    yellow: 'from-[#FCD34D] to-[#F59E0B]',
    blue: 'from-[#60A5FA] to-[#0EA5E9]',
  };

  return (
    <div className="clay-card shadow-clay-card p-6 hover:shadow-clay-card-hover transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${colorClasses[color]} shadow-clay-orb flex items-center justify-center text-white`}>
          {icon}
        </div>
      </div>
      <p className="text-sm text-[#635F69] mb-1">{title}</p>
      <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
        {value}
      </p>
      {subtitle && (
        <p className="text-xs text-[#635F69] mt-1">{subtitle}</p>
      )}
    </div>
  );
}

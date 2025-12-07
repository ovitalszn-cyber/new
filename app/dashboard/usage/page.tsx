'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

type DateRange = 'today' | '7days' | '30days' | 'custom';

interface UsageData {
  totalRequests: number;
  successfulRequests: number;
  errorRate: number;
  tier: string;
  requestsRemaining: number;
  dailyLimit: number;
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
  statusCode: number;
  latency: number;
  keyId: string;
}

export default function UsagePage() {
  const [dateRange, setDateRange] = useState<DateRange>('7days');

  // Mock data
  const usageData: UsageData = {
    totalRequests: 12847,
    successfulRequests: 12654,
    errorRate: 1.5,
    tier: 'DEVELOPER',
    requestsRemaining: 87153,
    dailyLimit: 100000,
  };

  const endpointUsage: EndpointUsage[] = [
    { endpoint: '/v5/match', count: 5420, percentage: 42 },
    { endpoint: '/v5/event/{id}', count: 3210, percentage: 25 },
    { endpoint: '/v5/odds', count: 2156, percentage: 17 },
    { endpoint: '/v5/props', count: 1284, percentage: 10 },
    { endpoint: '/v5/ev-slips', count: 777, percentage: 6 },
  ];

  const recentRequests: RecentRequest[] = [
    { id: '1', timestamp: '2024-01-20 14:32:15', endpoint: '/v5/match?sport=basketball_nba', statusCode: 200, latency: 142, keyId: 'kr_prod_xxxx' },
    { id: '2', timestamp: '2024-01-20 14:32:10', endpoint: '/v5/event/12345', statusCode: 200, latency: 89, keyId: 'kr_prod_xxxx' },
    { id: '3', timestamp: '2024-01-20 14:32:05', endpoint: '/v5/odds?book=fanduel', statusCode: 200, latency: 156, keyId: 'kr_prod_xxxx' },
    { id: '4', timestamp: '2024-01-20 14:32:00', endpoint: '/v5/props?player=lebron', statusCode: 429, latency: 12, keyId: 'kr_test_xxxx' },
    { id: '5', timestamp: '2024-01-20 14:31:55', endpoint: '/v5/match?sport=football_nfl', statusCode: 200, latency: 178, keyId: 'kr_prod_xxxx' },
  ];

  const dateRangeOptions: { value: DateRange; label: string }[] = [
    { value: 'today', label: 'Today' },
    { value: '7days', label: 'Last 7 Days' },
    { value: '30days', label: 'Last 30 Days' },
    { value: 'custom', label: 'Custom Range' },
  ];

  const getStatusColor = (code: number) => {
    if (code >= 200 && code < 300) return 'text-[#10B981] bg-[#10B981]/10';
    if (code >= 400 && code < 500) return 'text-[#F59E0B] bg-[#F59E0B]/10';
    return 'text-[#EF4444] bg-[#EF4444]/10';
  };

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
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

      {/* Key Metrics */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Requests"
          value={usageData.totalRequests.toLocaleString()}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
          color="purple"
        />
        <MetricCard
          title="Successful"
          value={usageData.successfulRequests.toLocaleString()}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          }
          color="green"
        />
        <MetricCard
          title="Error Rate"
          value={`${usageData.errorRate}%`}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          }
          color="yellow"
        />
        <MetricCard
          title="Remaining Today"
          value={usageData.requestsRemaining.toLocaleString()}
          subtitle={`of ${usageData.dailyLimit.toLocaleString()}`}
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
        {/* Request Trend */}
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
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Latency</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Key</th>
              </tr>
            </thead>
            <tbody>
              {recentRequests.map((request) => (
                <tr key={request.id} className="border-b border-[#E5E1EF]/50 hover:bg-[#7C3AED]/5 transition-colors">
                  <td className="py-3 px-4 text-sm text-[#635F69] font-mono">{request.timestamp}</td>
                  <td className="py-3 px-4">
                    <code className="text-sm text-[#7C3AED] font-mono">{request.endpoint}</code>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatusColor(request.statusCode)}`}>
                      {request.statusCode}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-[#635F69]">{request.latency}ms</td>
                  <td className="py-3 px-4">
                    <code className="text-xs text-[#635F69] font-mono">{request.keyId}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
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

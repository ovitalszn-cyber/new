'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import DashboardLayout from '@/components/DashboardLayout';
import AuthGuard from '@/components/AuthGuard';

const PUBLIC_API_BASE = process.env.NEXT_PUBLIC_PUBLIC_API_BASE || 'https://api.kashrock.com';

interface DashboardStats {
  totalRequests: number;
  activeKeys: number;
  tier: string;
  requestsRemaining: number;
}

const quickActions = [
  {
    title: 'API Keys',
    description: 'Generate and manage your API keys',
    href: '/dashboard/api-keys',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
    color: 'from-[#A78BFA] to-[#7C3AED]',
  },
  {
    title: 'Usage',
    description: 'Monitor your API usage and metrics',
    href: '/dashboard/usage',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    color: 'from-[#34D399] to-[#10B981]',
  },
];

export default function DashboardPage() {
  const { data: session } = useSession();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        if (!session) return; // AuthGuard handles redirect

        // @ts-ignore
        const token = session.id_token || session.accessToken;

        // Fetch usage stats
        const headers = token ? {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        } : { 'Content-Type': 'application/json' };

        const usageRes = await fetch(`${PUBLIC_API_BASE}/v1/dashboard/usage`, { headers });

        // Fetch keys count
        let activeKeysCount = 0;
        try {
          const keysRes = await fetch(`${PUBLIC_API_BASE}/v1/dashboard/api-keys`, { headers });
          if (keysRes.ok) {
            const keysData = await keysRes.json();
            const keysList = Array.isArray(keysData) ? keysData : (keysData.keys || []);
            activeKeysCount = keysList.length;
          }
        } catch (e) {
          console.error("Failed to fetch keys count", e);
        }

        if (usageRes.ok) {
          const usageData = await usageRes.json();
          setStats({
            totalRequests: usageData.total_requests || 0,
            activeKeys: activeKeysCount,
            tier: usageData.tier || 'Free',
            requestsRemaining: usageData.remaining || 0,
          });
        } else {
          console.warn("Usage fetch failed", usageRes.status);
          setStats({
            totalRequests: 0,
            activeKeys: activeKeysCount,
            tier: 'Free',
            requestsRemaining: 0
          });
        }
      } catch (err) {
        console.error("Error loading dashboard data", err);
        setError("Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    if (session) {
      fetchStats();
    }
  }, [session]);

  return (
    <AuthGuard>
      <DashboardLayout>
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to your KashRock dashboard</h1>
          <p className="mt-2 text-lg text-gray-600">Get started with our API and explore its features.</p>

          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900">Stats</h2>
            {loading ? (
              <div className="mt-4 p-8 flex justify-center text-gray-500">
                <svg className="w-8 h-8 animate-spin text-[#7C3AED]" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            ) : error ? (
              <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg">{error}</div>
            ) : (
              <div className="mt-4 flex justify-between gap-4 flex-wrap">
                <div className="bg-white rounded-lg shadow-md p-4 flex-1 min-w-[200px]">
                  <h3 className="text-lg font-bold text-gray-900">Total Requests</h3>
                  <p className="text-lg text-gray-600">{stats?.totalRequests.toLocaleString()}</p>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4 flex-1 min-w-[200px]">
                  <h3 className="text-lg font-bold text-gray-900">Active Keys</h3>
                  <p className="text-lg text-gray-600">{stats?.activeKeys}</p>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4 flex-1 min-w-[200px]">
                  <h3 className="text-lg font-bold text-gray-900">Tier</h3>
                  <p className="text-lg text-gray-600">{stats?.tier}</p>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4 flex-1 min-w-[200px]">
                  <h3 className="text-lg font-bold text-gray-900">Requests Remaining</h3>
                  <p className="text-lg text-gray-600">{stats?.requestsRemaining.toLocaleString()}</p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900">Quick Actions</h2>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {quickActions.map((action, index) => (
                <Link key={index} href={action.href}>
                  <div className={`bg-gradient-to-r ${action.color} rounded-lg shadow-md p-4 h-full hover:scale-[1.02] transition-transform`}>
                    <div className="flex items-center">
                      {action.icon}
                      <h3 className="text-lg font-bold text-white ml-4">{action.title}</h3>
                    </div>
                    <p className="text-lg text-white mt-2 opacity-90">{action.description}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900">Getting Started</h2>
            <div className="mt-4">
              <p className="text-lg text-gray-600">1. Read our documentation to learn how to integrate our API.</p>
              <p className="text-lg text-gray-600">2. Generate an API key to start making requests.</p>
              <p className="text-lg text-gray-600">3. Explore our API endpoints to discover its features.</p>
            </div>
          </div>

          <div className="mt-8">
            <Link href="/docs">
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors">
                View Documentation
              </button>
            </Link>
          </div>
        </div>
      </DashboardLayout>
    </AuthGuard>
  );
}

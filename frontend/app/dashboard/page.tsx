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
    description: 'Generate and manage your API keys for authentication',
    href: '/dashboard/api-keys',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
    gradient: 'from-[#A78BFA] to-[#7C3AED]',
  },
  {
    title: 'Usage Analytics',
    description: 'Monitor your API usage, performance metrics, and quotas',
    href: '/dashboard/usage',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    gradient: 'from-[#34D399] to-[#10B981]',
  },
  {
    title: 'Documentation',
    description: 'Learn how to integrate our API into your applications',
    href: '/docs',
    icon: (
      <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    gradient: 'from-[#0EA5E9] to-[#0284C7]',
  },
];

const statCards = [
  {
    key: 'totalRequests',
    label: 'Total Requests',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    gradient: 'from-amber-400 to-orange-500',
  },
  {
    key: 'activeKeys',
    label: 'Active Keys',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
    gradient: 'from-purple-400 to-violet-500',
  },
  {
    key: 'tier',
    label: 'Current Plan',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
      </svg>
    ),
    gradient: 'from-pink-400 to-rose-500',
  },
  {
    key: 'requestsRemaining',
    label: 'Requests Left',
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    gradient: 'from-emerald-400 to-green-500',
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
        if (!session) return;

        // @ts-ignore
        const token = session.id_token || session.accessToken;

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const usageRes = await fetch(`${PUBLIC_API_BASE}/v1/dashboard/usage`, { headers });

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
            totalRequests: usageData.metrics?.totalRequests || usageData.total_requests || 0,
            activeKeys: activeKeysCount,
            tier: usageData.metrics?.tier || usageData.tier || 'Free',
            requestsRemaining: usageData.metrics?.requestsRemaining || usageData.remaining || 0,
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

  const getStatValue = (key: string) => {
    if (!stats) return '—';
    const value = stats[key as keyof DashboardStats];
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return value || '—';
  };

  return (
    <AuthGuard>
      <DashboardLayout>
        {/* Floating Blobs Background */}
        <div className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
          <div
            className="absolute h-[40vh] w-[40vh] rounded-full blur-3xl bg-[#8B5CF6]/5 animate-clay-float"
            style={{ top: '10%', right: '5%' }}
          />
          <div
            className="absolute h-[35vh] w-[35vh] rounded-full blur-3xl bg-[#0EA5E9]/5 animate-clay-float-delayed"
            style={{ bottom: '20%', left: '-5%' }}
          />
        </div>

        <div className="mb-10">
          {/* Welcome Header */}
          <div className="mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#10B981]/10 text-[#10B981] font-semibold text-sm mb-4">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              Dashboard
            </div>
            <h1
              className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-3"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Welcome back to{' '}
              <span className="bg-gradient-to-r from-[#A78BFA] via-[#7C3AED] to-[#DB2777] bg-clip-text text-transparent">
                KashRock
              </span>
            </h1>
            <p className="text-lg text-[#635F69] max-w-2xl">
              Your AI-first sports data backbone. Monitor your usage, manage API keys, and build amazing products.
            </p>
          </div>

          {/* Stats Grid */}
          <div className="mb-10">
            <h2
              className="text-xl font-bold text-[#332F3A] mb-5"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Overview
            </h2>

            {loading ? (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="clay-card shadow-clay-card p-6 animate-pulse">
                    <div className="w-12 h-12 rounded-2xl bg-[#EFEBF5] mb-4" />
                    <div className="h-8 bg-[#EFEBF5] rounded-lg w-20 mb-2" />
                    <div className="h-4 bg-[#EFEBF5] rounded w-24" />
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="clay-card shadow-clay-card p-6 bg-red-50/50">
                <p className="text-red-600 font-medium">{error}</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {statCards.map((stat) => (
                  <div
                    key={stat.key}
                    className="clay-card shadow-clay-card p-6 hover:-translate-y-2 hover:shadow-clay-card-hover transition-all duration-300 group"
                  >
                    <div
                      className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${stat.gradient} shadow-clay-orb flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}
                    >
                      <span className="text-white">{stat.icon}</span>
                    </div>
                    <p
                      className="text-2xl sm:text-3xl font-black text-[#332F3A] mb-1"
                      style={{ fontFamily: 'Nunito, sans-serif' }}
                    >
                      {getStatValue(stat.key)}
                    </p>
                    <p className="text-sm text-[#635F69] font-medium">{stat.label}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="mb-10">
            <h2
              className="text-xl font-bold text-[#332F3A] mb-5"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Quick Actions
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {quickActions.map((action, index) => (
                <Link key={index} href={action.href}>
                  <div
                    className={`clay-card shadow-clay-card p-6 bg-gradient-to-br ${action.gradient} hover:-translate-y-2 hover:shadow-clay-card-hover transition-all duration-300 group h-full`}
                  >
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <span className="text-white">{action.icon}</span>
                      </div>
                      <h3
                        className="text-xl font-bold text-white"
                        style={{ fontFamily: 'Nunito, sans-serif' }}
                      >
                        {action.title}
                      </h3>
                    </div>
                    <p className="text-white/90 text-sm leading-relaxed">
                      {action.description}
                    </p>
                    <div className="mt-4 flex items-center gap-2 text-white/80 text-sm font-medium group-hover:text-white transition-colors">
                      <span>Get Started</span>
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Getting Started */}
          <div className="clay-card shadow-clay-card p-8 relative overflow-hidden">
            {/* Decorative gradient */}
            <div className="absolute -top-20 -right-20 w-40 h-40 rounded-full bg-gradient-to-br from-[#7C3AED]/10 to-[#DB2777]/10 blur-3xl" />

            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] shadow-clay-orb flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h2
                  className="text-xl font-bold text-[#332F3A]"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  Getting Started
                </h2>
              </div>

              <div className="space-y-4 mb-8">
                {[
                  { step: 1, text: 'Read our documentation to learn how to integrate our API' },
                  { step: 2, text: 'Generate an API key to authenticate your requests' },
                  { step: 3, text: 'Explore our endpoints to discover sports data features' },
                ].map((item) => (
                  <div key={item.step} className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-[#7C3AED]/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-[#7C3AED]">{item.step}</span>
                    </div>
                    <p className="text-[#635F69]">{item.text}</p>
                  </div>
                ))}
              </div>

              <Link href="/docs">
                <button
                  className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.95] transition-all duration-200 flex items-center gap-2"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  View Documentation
                </button>
              </Link>
            </div>
          </div>
        </div>
      </DashboardLayout>
    </AuthGuard>
  );
}

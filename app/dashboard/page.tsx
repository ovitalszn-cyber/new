'use client';

import { useState, useEffect, useRef } from 'react';
import Script from 'next/script';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

interface AuthUser {
  id: string;
  email: string;
  name?: string | null;
  plan: string;
  status: string;
}

export default function DashboardPage() {
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [stats, setStats] = useState({
    totalRequests: 0,
    activeKeys: 0,
    tier: 'FREE',
    requestsRemaining: 0,
  });

  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    if (accessToken) {
      fetchDashboardData();
    }
  }, [accessToken]);

  const fetchDashboardData = async () => {
    setLoadingStats(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const headers = { Authorization: `Bearer ${accessToken}` };

      // Parallel fetch: Keys + Usage
      const [keysRes, usageRes] = await Promise.all([
        fetch(`${apiBase}/v1/dashboard/api-keys`, { headers }),
        fetch(`${apiBase}/v1/dashboard/usage?range=30days`, { headers })
      ]);

      let activeKeys = 0;
      if (keysRes.ok) {
        const keysData = await keysRes.json();
        if (Array.isArray(keysData)) {
          activeKeys = keysData.filter((k: any) => k.status === 'active').length;
        }
      }

      let totalRequests = 0;
      let requestsRemaining = 0;

      if (usageRes.ok) {
        const usageData = await usageRes.json();
        const liveStats = usageData.usage_stats?.live || { requests: 0, credits: 0 };
        const testStats = usageData.usage_stats?.test || { requests: 0, credits: 0 };

        totalRequests = liveStats.requests + testStats.requests;

        // Use quota from response if available, else fallback
        if (usageData.quota) {
          requestsRemaining = usageData.quota.remaining;
        }
      }

      setStats({
        totalRequests,
        activeKeys,
        tier: authUser?.plan?.toUpperCase() || 'FREE',
        requestsRemaining,
      });

    } catch (error) {
      console.error("Failed to fetch dashboard stats", error);
    } finally {
      setLoadingStats(false);
    }
  };

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
    {
      title: 'Documentation',
      description: 'Learn how to integrate the API',
      href: '/docs',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
      color: 'from-[#60A5FA] to-[#0EA5E9]',
    },
  ];

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = window.localStorage.getItem('kashrock_dashboard_session');
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed?.access_token && parsed?.user) {
        setAccessToken(parsed.access_token as string);
        setAuthUser(parsed.user as AuthUser);
      }
    } catch {
      // ignore invalid session
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthLoading(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${apiBase}/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.detail || 'Failed to sign in');
      }

      setAccessToken(data.access_token as string);
      setAuthUser(data.user as AuthUser);

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(
          'kashrock_dashboard_session',
          JSON.stringify({ access_token: data.access_token, user: data.user }),
        );
      }
    } catch (err: any) {
      setAuthError(err?.message || 'Failed to sign in');
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <DashboardLayout>
      {!accessToken ? (
        <div className="max-w-md mx-auto mt-8 clay-card shadow-clay-card p-8 text-center">
          <h1
            className="text-2xl sm:text-3xl font-black text-[#332F3A] mb-3"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            Sign in to your KashRock dashboard
          </h1>
          <p className="text-sm text-[#635F69] mb-6">
            Enter your email and password to access your API keys, usage, and account settings.
          </p>
          {authError && (
            <div className="mb-4 text-sm text-red-700 bg-red-100 border border-red-300 rounded-lg px-3 py-2">
              {authError}
            </div>
          )}
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
              className="w-full px-4 py-3 rounded-xl border border-[#E5E1EF] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] bg-white"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              className="w-full px-4 py-3 rounded-xl border border-[#E5E1EF] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] bg-white"
            />
            <button
              type="submit"
              disabled={authLoading}
              className="w-full px-5 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all disabled:opacity-50"
            >
              {authLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      ) : (
        <>
          {(() => {
            const displayName = authUser?.name?.trim() || authUser?.email || 'there';
            return (
              <div className="mb-8">
                <h1
                  className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {`Welcome back, ${displayName}!`}
                </h1>
                <p className="text-[#635F69]">
                  Here&apos;s an overview of your KashRock API account.
                </p>
              </div>
            );
          })()}

          {/* Welcome Header */}
          <div className="sr-only">
            {/* Hidden block kept for layout spacing via new heading above */}
          </div>

          {/* Stats Cards */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="clay-card shadow-clay-card p-6">
              <p className="text-sm text-[#635F69] mb-1">Total Requests (Month)</p>
              <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                {loadingStats ? "..." : stats.totalRequests.toLocaleString()}
              </p>
            </div>
            <div className="clay-card shadow-clay-card p-6">
              <p className="text-sm text-[#635F69] mb-1">Active Keys</p>
              <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                {loadingStats ? "..." : stats.activeKeys}
              </p>
            </div>
            <div className="clay-card shadow-clay-card p-6">
              <p className="text-sm text-[#635F69] mb-1">Current Tier</p>
              <p className="text-2xl font-black text-[#7C3AED]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                {stats.tier}
              </p>
            </div>
            <div className="clay-card shadow-clay-card p-6">
              <p className="text-sm text-[#635F69] mb-1">Remaining Credits</p>
              <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                {loadingStats ? "..." : stats.requestsRemaining.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2
              className="text-xl font-bold text-[#332F3A] mb-4"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Quick Actions
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {quickActions.map((action, index) => (
                <Link
                  key={index}
                  href={action.href}
                  className="clay-card shadow-clay-card p-6 hover:shadow-clay-card-hover hover:-translate-y-2 transition-all duration-300 group"
                >
                  <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${action.color} shadow-clay-orb flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                    {action.icon}
                  </div>
                  <h3 className="font-bold text-[#332F3A] mb-1" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    {action.title}
                  </h3>
                  <p className="text-sm text-[#635F69]">
                    {action.description}
                  </p>
                </Link>
              ))}
            </div>
          </div>

          {/* Getting Started */}
          <div className="clay-card shadow-clay-card p-8">
            <h2
              className="text-xl font-bold text-[#332F3A] mb-4"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Getting Started
            </h2>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-[#7C3AED] text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                  1
                </div>
                <div>
                  <h4 className="font-bold text-[#332F3A]">Generate an API Key</h4>
                  <p className="text-sm text-[#635F69]">Create your first API key to start making requests.</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-[#7C3AED] text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                  2
                </div>
                <div>
                  <h4 className="font-bold text-[#332F3A]">Make Your First Request</h4>
                  <p className="text-sm text-[#635F69]">Use the quick start examples to test the API.</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-[#7C3AED] text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                  3
                </div>
                <div>
                  <h4 className="font-bold text-[#332F3A]">Build Something Amazing</h4>
                  <p className="text-sm text-[#635F69]">Explore the docs and start building your application.</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </DashboardLayout>
  );
}

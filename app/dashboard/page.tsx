'use client';

import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

export default function DashboardPage() {
  // Mock data for overview
  const stats = {
    totalRequests: 12847,
    activeKeys: 2,
    tier: 'DEVELOPER',
    requestsRemaining: 87153,
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
    {
      title: 'Support',
      description: 'Get help from our team',
      href: '/support',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      color: 'from-[#F472B6] to-[#DB2777]',
    },
  ];

  return (
    <DashboardLayout>
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Welcome back!
        </h1>
        <p className="text-[#635F69]">
          Here&apos;s an overview of your KashRock API account.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Total Requests</p>
          <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {stats.totalRequests.toLocaleString()}
          </p>
        </div>
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Active Keys</p>
          <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {stats.activeKeys}
          </p>
        </div>
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Current Tier</p>
          <p className="text-2xl font-black text-[#7C3AED]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {stats.tier}
          </p>
        </div>
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Remaining Today</p>
          <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {stats.requestsRemaining.toLocaleString()}
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
    </DashboardLayout>
  );
}

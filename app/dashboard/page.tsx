'use client';

import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

const mockStats = {
  totalRequests: 12932,
  activeKeys: 4,
  tier: 'FREE',
  requestsRemaining: 8713,
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

const stats = mockStats;

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome to your KashRock dashboard</h1>
        <p className="mt-2 text-lg text-gray-600">Get started with our API and explore its features.</p>
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900">Stats</h2>
          <div className="mt-4 flex justify-between">
            <div className="bg-white rounded-lg shadow-md p-4 w-1/2">
              <h3 className="text-lg font-bold text-gray-900">Total Requests</h3>
              <p className="text-lg text-gray-600">{stats.totalRequests}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4 w-1/2">
              <h3 className="text-lg font-bold text-gray-900">Active Keys</h3>
              <p className="text-lg text-gray-600">{stats.activeKeys}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4 w-1/2">
              <h3 className="text-lg font-bold text-gray-900">Tier</h3>
              <p className="text-lg text-gray-600">{stats.tier}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4 w-1/2">
              <h3 className="text-lg font-bold text-gray-900">Requests Remaining</h3>
              <p className="text-lg text-gray-600">{stats.requestsRemaining}</p>
            </div>
          </div>
        </div>
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900">Quick Actions</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {quickActions.map((action, index) => (
              <Link key={index} href={action.href}>
                <div className={`bg-gradient-to-r ${action.color} rounded-lg shadow-md p-4`}>
                  <div className="flex items-center">
                    {action.icon}
                    <h3 className="text-lg font-bold text-white ml-4">{action.title}</h3>
                  </div>
                  <p className="text-lg text-white mt-2">{action.description}</p>
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
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              View Documentation
            </button>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
}

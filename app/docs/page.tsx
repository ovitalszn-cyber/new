'use client';

import { useState } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState<string>('overview');

  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'v6-cached', label: 'Cached Events API' },
    { id: 'v6-stats', label: 'Stats & History API' },
    { id: 'v6-odds', label: 'Odds & Books API' },
    { id: 'dashboard', label: 'Dashboard API' },
  ];

  const Endpoint = ({ method, path, desc, params, response }: { method: string, path: string, desc: string, params?: string[], response?: string }) => (
    <div className="border border-gray-200 rounded-lg p-4 mb-4 bg-white">
      <div className="flex items-center gap-3 mb-2">
        <span className={`px-2 py-1 rounded text-xs font-bold ${
          method === 'GET' ? 'bg-blue-100 text-blue-700' :
          method === 'POST' ? 'bg-green-100 text-green-700' :
          method === 'DELETE' ? 'bg-red-100 text-red-700' : 'bg-gray-100'
        }`}>
          {method}
        </span>
        <code className="text-sm font-mono text-[#332F3A]">{path}</code>
      </div>
      <p className="text-sm text-[#635F69] mb-3">{desc}</p>
      {params && (
        <div className="mb-3">
          <p className="text-xs font-bold text-[#332F3A] mb-1">Parameters:</p>
          <ul className="list-disc list-inside text-xs text-[#635F69] space-y-1">
            {params.map((p, i) => <li key={i} dangerouslySetInnerHTML={{ __html: p }} />)}
          </ul>
        </div>
      )}
      {response && (
        <div>
          <p className="text-xs font-bold text-[#332F3A] mb-1">Response:</p>
          <pre className="bg-gray-50 p-2 rounded text-xs text-[#635F69] overflow-x-auto font-mono">
            {response}
          </pre>
        </div>
      )}
    </div>
  );

  const renderSection = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              API Overview
            </h2>
            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Authentication</h3>
              <p className="text-sm text-[#635F69] mb-4">
                All API requests detailed below require a valid API Key. Include it in the header of your requests:
              </p>
              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm mb-4">
                Authorization: Bearer &lt;YOUR_API_KEY&gt;
              </div>
              <p className="text-sm text-[#635F69]">
                You can manage your API keys in the <Link href="/dashboard/api-keys" className="text-[#7C3AED] hover:underline">API Keys</Link> section.
              </p>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Rate Limiting</h3>
              <p className="text-sm text-[#635F69] mb-2">
                Standard limits apply to all accounts unless otherwise negotiated:
              </p>
              <ul className="list-disc list-inside text-sm text-[#635F69] space-y-1 ml-2">
                <li><strong>Burst:</strong> 20 requests / second</li>
                <li><strong>Sustained:</strong> 1,000 requests / minute</li>
                <li><strong>Daily:</strong> 100,000 requests / day</li>
              </ul>
              <p className="text-sm text-[#635F69] mt-3">
                Exceeding these limits will result in a <code>429 Too Many Requests</code> response.
              </p>
            </div>
          </div>
        );

      case 'v6-cached':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Cached Events API
            </h2>
            <p className="text-sm text-[#635F69]">
              High-performance endpoints served directly from Redis cache (~50-100ms latency). Ideal for live odds and rapid polls.
            </p>

            <Endpoint
              method="GET"
              path="/v6/match"
              desc="Discover active matches and events across supported sports."
              params={[
                "<code>sport</code> (required): e.g. 'basketball_nba'",
                "<code>region</code> (optional): 'us', 'uk', 'eu'",
                "<code>limit</code> (optional): Defaults to 50"
              ]}
              response={JSON.stringify([
                { id: "evt_12345", sport: "basketball_nba", home: "Lakers", away: "Warriors", start_time: "2023-12-25T20:00:00Z" }
              ], null, 2)}
            />

            <Endpoint
              method="GET"
              path="/v6/event/{id}"
              desc="Retrieve full details for a specific canonical event, including current markets."
              params={["<code>id</code> (required): The canonical event ID (e.g., 'evt_12345')"]}
            />

            <Endpoint
              method="GET"
              path="/v6/spreads"
              desc="Get standardized point spreads and moneylines for upcoming games."
              params={["<code>sport</code> (required): Sport key"]}
            />
          </div>
        );

      case 'v6-stats':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Stats & History API
            </h2>
            <p className="text-sm text-[#635F69]">
              Comprehensive statistical data, rosters, and historical records derived from ESPN and other sources.
            </p>

            <Endpoint
              method="GET"
              path="/v6/stats/{player_id}"
              desc="Get detailed season stats for a specific player."
              params={[
                "<code>player_id</code> (required): Canonical player ID",
                "<code>categories</code> (optional): Comma-separated list of stat categories (e.g., 'scoring,passing')"
              ]}
            />

            <Endpoint
              method="GET"
              path="/v6/games/live"
              desc="Get real-time scores and status for currently active games."
              params={["<code>sport</code> (required): Sport key"]}
              response={JSON.stringify({
                games: [{ id: "game_999", score_home: 102, score_away: 98, quarter: 4, clock: "2:30" }]
              }, null, 2)}
            />
          </div>
        );

      case 'v6-odds':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Odds & Books API
            </h2>
            <p className="text-sm text-[#635F69]">
              Unified odds aggregation from multiple sportsbooks (Lunosoft, etc.).
            </p>

            <Endpoint
              method="GET"
              path="/v6/odds/live/{sport}"
              desc="Stream live odds updates for a specific sport."
              params={[
                "<code>sport</code> (required): Sport key (e.g., 'americanfootball_nfl')",
                "<code>books</code> (optional): Filter by bookmaker (e.g., 'draftkings,fanduel')"
              ]}
            />
          </div>
        );

      case 'dashboard':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Dashboard API
            </h2>
            <p className="text-sm text-[#635F69]">
              Management endpoints for your account integration.
            </p>

            <Endpoint
              method="GET"
              path="/v1/dashboard/usage"
              desc="Retrieve your current API usage statistics and quota status."
              params={["<code>range</code> (optional): 'today', '7days', '30days'"]}
              response={JSON.stringify({
                total_requests: 15430,
                quota_limit: 100000,
                remaining: 84570,
                tier: "Pro"
              }, null, 2)}
            />

             <Endpoint
              method="POST"
              path="/v1/dashboard/api-keys"
              desc="Generate a new API key programmatically."
              response={JSON.stringify({
                 key_id: "key_abc123",
                 key_secret: "rk_live_99887766...",
                 created_at: "2023-10-10T12:00:00Z"
              }, null, 2)}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <DashboardLayout>
      <div className="flex gap-8">
        <nav className="w-64 flex-shrink-0">
          <div className="clay-card shadow-clay-card p-6 sticky top-8">
            <h3 className="text-lg font-bold text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Documentation
            </h3>
            <ul className="space-y-2">
              {navItems.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      activeSection === item.id
                        ? 'bg-[#7C3AED] text-white'
                        : 'text-[#635F69] hover:bg-gray-100'
                    }`}
                  >
                    {item.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        <main className="flex-1 min-w-0 pb-12">
          {renderSection()}
        </main>
      </div>
    </DashboardLayout>
  );
}

'use client';

import { useState } from 'react';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState<string>('overview');

  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'v6-cached', label: 'V6 Cached API' },
    { id: 'v6-unified', label: 'V6 Unified API' },
    { id: 'v6-stats', label: 'V6 Stats API' },
    { id: 'v6-odds', label: 'V6 Odds API' },
    { id: 'v6-export', label: 'V6 Export API' },
    { id: 'v6-production', label: 'V6 Production API' },
    { id: 'dashboard-api', label: 'Dashboard API' },
  ];

  const renderSection = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              KashRock V6 API Overview
            </h2>
            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Base URL</h3>
              <code className="block bg-gray-100 p-3 rounded text-sm">http://&lt;host&gt;:&lt;port&gt;</code>
            </div>
            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Router Mounting</h3>
              <ul className="space-y-2 text-sm text-[#635F69]">
                <li><code>v6.api.cached.router</code> → <code>/v6</code></li>
                <li><code>v6.api.stats.router</code> → <code>/v6</code></li>
                <li><code>v6.api.odds.router</code> → <code>/v6</code></li>
                <li><code>v6.api.unified.router</code> → <code>/v6</code></li>
                <li><code>v6.api.export.router</code> → <code>/v6</code></li>
                <li><code>v6.api.production.router</code> → <strong>not mounted</strong></li>
              </ul>
            </div>
            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Authentication</h3>
              <p className="text-sm text-[#635F69] mb-2">
                Most cached endpoints require a KashRock API key via <code>Authorization: Bearer &lt;api_key&gt;</code>.
              </p>
              <p className="text-sm text-[#635F69]">
                Production router uses FastAPI <code>HTTPBearer</code> (placeholder for real auth).
              </p>
            </div>
          </div>
        );

      case 'v6-cached':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Cached API (<code>/v6</code>)
            </h2>
            <p className="text-sm text-[#635F69]">
              Redis-backed, background-worker-populated endpoints for sub‑100ms responses.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Event Discovery & Retrieval</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/event/{'{canonical_event_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Fetch a single canonical event from Redis. Auth: API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/match</code>
                  <p className="text-sm text-[#635F69] mt-1">Discovery endpoint to find cached events by sport/teams. Auth: API key.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Market-Level Views</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/spreads</code>
                  <p className="text-sm text-[#635F69] mt-1">Point‑spread markets from cached events. Auth: API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/player_props</code>
                  <p className="text-sm text-[#635F69] mt-1">Player props only (filters out traditional markets). Auth: API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/game_bundle</code>
                  <p className="text-sm text-[#635F69] mt-1">Single-game bundle: normalized markets + per‑team player props. Auth: API key.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">EV-Focused Views</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/ev-props</code>
                  <p className="text-sm text-[#635F69] mt-1">EV‑enhanced props from Redis (cached, sub‑100ms). Auth: API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/ev</code>
                  <p className="text-sm text-[#635F69] mt-1">Live EV fetch/merge from Walter/Rotowire/Proply (not cached; slower). Auth: API key.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Health & Admin</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/health/cache</code>
                  <p className="text-sm text-[#635F69] mt-1">Redis cache + V6 background worker health. Auth: API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/stats</code>
                  <p className="text-sm text-[#635F69] mt-1">Cache metrics and event counts per sport. Auth: API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">POST /v6/admin/cache/clear</code>
                  <p className="text-sm text-[#635F69] mt-1">Clear Redis keys (admin). Auth: API key.</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'v6-unified':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Unified API (<code>/v6</code>)
            </h2>
            <p className="text-sm text-[#635F69]">
              Combines OddsEngine and Redis-based props into a unified interface.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Health & Book Discovery</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/health</code>
                  <p className="text-sm text-[#635F69] mt-1">Odds engine + props cache health.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/books</code>
                  <p className="text-sm text-[#635F69] mt-1">Available odds books + props books per sport.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Odds & Props</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/ods/{'{book_key}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Odds from a single book (optional sport filter).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds</code>
                  <p className="text-sm text-[#635F69] mt-1">Aggregated odds (optional sport filter).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/props/{'{book_key}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Cached props for a single book + sport.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/props</code>
                  <p className="text-sm text-[#635F69] mt-1">Aggregated cached props for a sport (optional books filter).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Convenience Endpoints</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/main-sports</code>
                  <p className="text-sm text-[#635F69] mt-1">Snapshot for NFL/NBA/MLB/NHL (odds + props).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/player/{'{player_name}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Props for a specific player across books.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/stat/{'{stat_type}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Props for a specific stat type across books.</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'v6-stats':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Stats API (<code>/v6</code>)
            </h2>
            <p className="text-sm text-[#635F69]">
              Games, teams, players, box scores, and ESPN historical data.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Games & Schedule</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/games</code>
                  <p className="text-sm text-[#635F69] mt-1">List games (sport, league, event_ids, betmode).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/games/today</code>
                  <p className="text-sm text-[#635F69] mt-1">Today&apos;s games for a sport.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/games/live</code>
                  <p className="text-sm text-[#635F69] mt-1">Live games for a sport.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/games/{'{game_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Single game details.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/schedule</code>
                  <p className="text-sm text-[#635F69] mt-1">Sport schedule (UTC offset supported).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Teams & Standings</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/teams</code>
                  <p className="text-sm text-[#635F69] mt-1">List teams (sport, league).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/teams/{'{team_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Single team details.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/standings</code>
                  <p className="text-sm text-[#635F69] mt-1">League standings (sport, league).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Players & Box Scores</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/players</code>
                  <p className="text-sm text-[#635F69] mt-1">Players for a team (sideload_team optional).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/roster</code>
                  <p className="text-sm text-[#635F69] mt-1">Alias for /players.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/players/{'{player_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Single player details.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/boxscore/{'{game_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Normalized box score for a game.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Comprehensive Stats</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/stats</code>
                  <p className="text-sm text-[#635F69] mt-1">Team‑level player stats (filters: start_date, end_date, categories, position, min_games).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/stats/{'{player_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Player‑level stats (filters: categories, team_id optional).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/stats/categories</code>
                  <p className="text-sm text-[#635F69] mt-1">Metadata about stat categories and supported sports.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/stats/compare</code>
                  <p className="text-sm text-[#635F69] mt-1">Side‑by‑side player comparison (player_ids comma-separated).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">ESPN Historical Data</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/history/{'{sport}'}/{'{date}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Historical games list for a date (YYYY‑MM‑DD).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/history/{'{event_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Complete historical game summary (ESPN event id).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/history/{'{sport}'}/search</code>
                  <p className="text-sm text-[#635F69] mt-1">Search historical games by team/date range (filters: team, start_date, end_date, limit).</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'v6-odds':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Odds API (<code>/v6</code>)
            </h2>
            <p className="text-sm text-[#635F69]">
              Odds-focused endpoints wrapping Lunosoft and internal aggregation.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Live Odds</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds/live</code>
                  <p className="text-sm text-[#635F69] mt-1">Live odds for in‑progress games (sport filter).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds/live/{'{sport}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Live odds for all current/upcoming games in a sport (limit optional).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Unified Game Odds</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds/{'{game_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Unified odds list for a specific game (sport filter).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Historical Odds</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds/history/{'{sport}'}/{'{date}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Historical odds for a date (YYYY‑MM‑DD). Optional sportsbook_ids filter.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds/history/{'{game_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Odds movement history for a game (hours_back filter; currently simulated).</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Export</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/odds/export/{'{sport}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Export odds metadata (date_from, date_to, format). Currently stubbed.</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'v6-export':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Export API (<code>/v6</code>)
            </h2>
            <p className="text-sm text-[#635F69]">
              Streaming export of odds, props, stats, and historical datasets.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Export Endpoint</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/export</code>
                  <p className="text-sm text-[#635F69] mt-1">Streaming NDJSON or CSV export.</p>
                </div>
                <div className="text-sm text-[#635F69] space-y-2">
                  <p><strong>Query params:</strong></p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li><code>format</code> – <code>"json"</code> (NDJSON) or <code>"csv"</code></li>
                    <li><code>datasets</code> – comma list (e.g., <code>live_odds,game_stats,historical_games</code>)</li>
                    <li><code>scope</code> – <code>"all"</code> | <code>"live"</code> | <code>"historical"</code></li>
                    <li><strong>Filters:</strong> sport, books, book_name, date_from, date_to, team_id, player_id, game_id, limit</li>
                  </ul>
                </div>
                <div className="text-sm text-[#635F69]">
                  <p><strong>Available datasets:</strong></p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>live_odds, live_props, game_stats</li>
                    <li>historical_odds, historical_props, historical_games</li>
                    <li>historical_team_stats, historical_team_stat_leaders</li>
                    <li>historical_players, historical_player_boxscores</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      case 'v6-production':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              V6 Production API (<code>/v6/prod</code>, NOT mounted by default)
            </h2>
            <p className="text-sm text-[#635F69]">
              Production‑grade monitoring, admin, and persistence endpoints. Not currently attached in <code>main.py</code>.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Health & Monitoring</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/prod/health</code>
                  <p className="text-sm text-[#635F69] mt-1">Detailed health across optimized engines, caches, metrics. Auth: Bearer (placeholder).</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/prod/monitoring/metrics</code>
                  <p className="text-sm text-[#635F69] mt-1">Realtime + historical metrics (hours_back filter). Auth: Bearer.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/prod/monitoring/caches</code>
                  <p className="text-sm text-[#635F69] mt-1">Cache info for odds + props caches. Auth: Bearer.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/prod/monitoring/circuit-breakers</code>
                  <p className="text-sm text-[#635F69] mt-1">Per‑book circuit breaker state. Auth: Bearer.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Admin & Historical Persistence</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">POST /v6/prod/admin/caches/clear</code>
                  <p className="text-sm text-[#635F69] mt-1">Clear in‑process caches (cache_type filter). Auth: Bearer.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">POST /v6/prod/admin/circuit-breakers/reset</code>
                  <p className="text-sm text-[#635F69] mt-1">Reset circuit breakers (book_key optional). Auth: Bearer.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/prod/history/odds/{'{book_key}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Odds snapshots over time from persistence (sport, hours_back). Auth: Bearer.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/prod/history/props/{'{book_key}'}/{'{player_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Historical props for a player/book (hours_back). Auth: Bearer.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">POST /v6/prod/admin/persistence/cleanup</code>
                  <p className="text-sm text-[#635F69] mt-1">Async cleanup of old historical data (days_to_keep). Auth: Bearer.</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'dashboard-api':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Dashboard API (<code>/v1/dashboard</code>)
            </h2>
            <p className="text-sm text-[#635F69]">
              Endpoints used by the frontend dashboard for management and analytics.
            </p>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Usage & Stats</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v1/dashboard/usage</code>
                  <p className="text-sm text-[#635F69] mt-1">
                    Get aggregated usage stats, quota info, and request breakdown.
                    <br />
                    <span className="text-xs">Query: <code>range</code> (today, 7days, 30days)</span>
                  </p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v1/dashboard/api-keys</code>
                  <p className="text-sm text-[#635F69] mt-1">List API keys for the current user.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">POST /v1/dashboard/api-keys</code>
                  <p className="text-sm text-[#635F69] mt-1">Create a new API key.</p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">DELETE /v1/dashboard/api-keys/{'{key_id}'}</code>
                  <p className="text-sm text-[#635F69] mt-1">Permanently delete an API key.</p>
                </div>
              </div>
            </div>

            <div className="clay-card shadow-clay-card p-6">
              <h3 className="text-lg font-bold text-[#332F3A] mb-3">Admin (Internal)</h3>
              <div className="space-y-4">
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/admin/usage/users</code>
                  <p className="text-sm text-[#635F69] mt-1">
                    Aggregated usage stats for all users (Admin only).
                    <br />
                    <span className="text-xs">Auth: <code>X-Admin-Secret</code> header.</span>
                  </p>
                </div>
                <div>
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">GET /v6/admin/usage/users/{'{user_id}'}/endpoints</code>
                  <p className="text-sm text-[#635F69] mt-1">
                    Detailed endpoint breakdown for a specific user.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <DashboardLayout>
      <div className="flex gap-8">
        {/* Sidebar Navigation */}
        <nav className="w-64 flex-shrink-0">
          <div className="clay-card shadow-clay-card p-6 sticky top-8">
            <h3 className="text-lg font-bold text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
              API Reference
            </h3>
            <ul className="space-y-2">
              {navItems.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${activeSection === item.id
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

        {/* Main Content */}
        <main className="flex-1 min-w-0">
          {renderSection()}
        </main>
      </div>
    </DashboardLayout>
  );
}

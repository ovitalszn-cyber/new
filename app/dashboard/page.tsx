'use client';

import { useState, useEffect } from 'react';
import SlipCard from '@/components/SlipCard';
import Filters from '@/components/Filters';
import { fetchSlips } from '@/lib/api';

export interface Slip {
  sport: string;
  soft_bookmaker_key: string;
  num_legs: number;
  legs: Leg[];
  total_expected_value_percent: number;
  payout_multiplier: number;
  sharp_parlay_probability: number;
  soft_parlay_payout: number;
  timestamp: string;
}

export interface Leg {
  sport: string;
  match_id: string;
  match_title: string;
  commence_time: string;
  outcome_description: string;
  player_info?: {
    player: string;
    canonical_player_name: string;
    stat: string;
    canonical_stat_key: string;
    line: number;
    team: string;
  };
  soft_book_odds: number;
  sharp_no_vig_odds: number;
  expected_value_percent: number;
}

export default function Home() {
  const [slips, setSlips] = useState<Slip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    sports: ['basketball_nba', 'americanfootball_nfl', 'icehockey_nhl'],
    numLegs: 2,
    minEV: 6.0,
    minTotalEV: 0.0,
    mixedSports: true,
    prematch: true,
    live: false,
  });

  useEffect(() => {
    loadSlips();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadSlips, 30000);
    return () => clearInterval(interval);
  }, [filters]);

  const loadSlips = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSlips(filters);
      setSlips(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load slips');
      console.error('Error loading slips:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-purple-800/50 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">K</span>
              </div>
              <h1 className="text-2xl font-bold text-white">KashRock EV Slips</h1>
            </div>
            <button
              onClick={loadSlips}
              disabled={loading}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Filters */}
        <Filters filters={filters} onFiltersChange={setFilters} />

        {/* Stats Bar */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-purple-800/30">
            <div className="text-purple-300 text-sm font-medium">Total Slips</div>
            <div className="text-2xl font-bold text-white mt-1">{slips.length}</div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-purple-800/30">
            <div className="text-purple-300 text-sm font-medium">Avg EV</div>
            <div className="text-2xl font-bold text-white mt-1">
              {slips.length > 0
                ? (slips.reduce((sum, s) => sum + s.total_expected_value_percent, 0) / slips.length).toFixed(1)
                : '0.0'}%
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-purple-800/30">
            <div className="text-purple-300 text-sm font-medium">Max EV</div>
            <div className="text-2xl font-bold text-green-400 mt-1">
              {slips.length > 0
                ? Math.max(...slips.map(s => s.total_expected_value_percent)).toFixed(1)
                : '0.0'}%
            </div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border border-purple-800/30">
            <div className="text-purple-300 text-sm font-medium">Mixed Sports</div>
            <div className="text-2xl font-bold text-white mt-1">
              {slips.filter(s => s.sport.includes(',')).length}
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 bg-red-900/50 border border-red-700 rounded-lg p-4 text-red-200">
            <div className="font-semibold">Error loading slips</div>
            <div className="text-sm mt-1">{error}</div>
          </div>
        )}

        {/* Slips Grid */}
        {loading && slips.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <div className="text-purple-300">Loading EV slips...</div>
            </div>
          </div>
        ) : slips.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-purple-300 text-lg">No slips found</div>
            <div className="text-purple-400/70 text-sm mt-2">Try adjusting your filters</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {slips.map((slip, index) => (
              <SlipCard key={index} slip={slip} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

'use client';

import type { Slip, Leg } from '@/app/dashboard/page';
import { formatTime } from '@/lib/utils';

interface SlipCardProps {
  slip: Slip;
}

export default function SlipCard({ slip }: SlipCardProps) {
  const evColor = slip.total_expected_value_percent >= 10 
    ? 'text-green-400' 
    : slip.total_expected_value_percent >= 5 
    ? 'text-yellow-400' 
    : 'text-purple-400';

  const isMixedSports = slip.sport.includes(',');

  return (
    <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-purple-800/30 p-6 hover:border-purple-600/50 transition-all shadow-lg hover:shadow-purple-900/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center font-bold text-white ${
            isMixedSports 
              ? 'bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500' 
              : 'bg-gradient-to-br from-purple-500 to-pink-500'
          }`}>
            {slip.num_legs}
          </div>
          <div>
            <div className="text-white font-semibold">
              {isMixedSports ? 'Mixed Sports' : slip.sport.replace('_', ' ').toUpperCase()}
            </div>
            <div className="text-purple-300 text-sm">
              {slip.num_legs} Pick {slip.num_legs === 2 ? 'Power' : slip.num_legs === 3 ? 'Flex' : 'Mega'}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-3xl font-bold ${evColor}`}>
            {slip.total_expected_value_percent.toFixed(1)}% EV
          </div>
          <div className="text-purple-300 text-sm mt-1">
            {slip.payout_multiplier}x Payout
          </div>
        </div>
      </div>

      {/* Payout Info */}
      <div className="mb-4 p-3 bg-slate-900/50 rounded-lg border border-purple-800/20">
        <div className="flex items-center justify-between text-sm">
          <span className="text-purple-300">Win Probability:</span>
          <span className="text-white font-semibold">
            {(slip.sharp_parlay_probability * 100).toFixed(1)}%
          </span>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="text-purple-300">Example: Bet $10 →</span>
          <span className="text-green-400 font-bold">
            Win ${(10 * slip.payout_multiplier).toFixed(0)}
          </span>
        </div>
      </div>

      {/* Legs */}
      <div className="space-y-3">
        {slip.legs.map((leg: Leg, index: number) => (
          <LegItem key={index} leg={leg} index={index + 1} />
        ))}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-purple-800/30 flex items-center justify-between text-xs text-purple-400">
        <span>{slip.soft_bookmaker_key.toUpperCase()}</span>
        <span>{formatTime(slip.timestamp)}</span>
      </div>
    </div>
  );
}

function LegItem({ leg, index }: { leg: Leg; index: number }) {
  const sportIcon = (sport: string) => {
    if (sport.includes('basketball')) return '🏀';
    if (sport.includes('football')) return '🏈';
    if (sport.includes('hockey')) return '🏒';
    if (sport.includes('baseball')) return '⚾';
    return '🎯';
  };

  return (
    <div className="bg-slate-900/40 rounded-lg p-3 border border-purple-800/20">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{sportIcon(leg.sport)}</span>
            <span className="text-white font-semibold text-sm">
              {leg.player_info?.player || 'Unknown Player'}
            </span>
            {leg.player_info?.team && (
              <span className="text-purple-300 text-xs">
                ({leg.player_info.team})
              </span>
            )}
          </div>
          
          <div className="text-purple-200 text-sm mb-2">
            {leg.outcome_description}
          </div>
          
          <div className="text-xs text-purple-400 mb-1">
            {leg.match_title}
          </div>
          
          <div className="text-xs text-purple-500">
            {formatTime(leg.commence_time)}
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-white font-semibold">
            {leg.soft_book_odds.toFixed(2)}x
          </div>
          <div className="text-green-400 text-xs">
            {leg.expected_value_percent.toFixed(1)}% EV
          </div>
        </div>
      </div>
    </div>
  );
}





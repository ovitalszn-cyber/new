'use client';

export interface Filters {
  sports: string[];
  numLegs: number;
  minEV: number;
  minTotalEV: number;
  mixedSports: boolean;
  prematch: boolean;
  live: boolean;
}

interface FiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
}

const SPORTS = [
  { key: 'basketball_nba', label: 'NBA' },
  { key: 'americanfootball_nfl', label: 'NFL' },
  { key: 'icehockey_nhl', label: 'NHL' },
  { key: 'baseball_mlb', label: 'MLB' },
  { key: 'basketball_wnba', label: 'WNBA' },
  { key: 'basketball_ncaa', label: 'NCAAB' },
];

export default function Filters({ filters, onFiltersChange }: FiltersProps) {
  const updateFilter = (key: keyof Filters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const toggleSport = (sportKey: string) => {
    const newSports = filters.sports.includes(sportKey)
      ? filters.sports.filter(s => s !== sportKey)
      : [...filters.sports, sportKey];
    updateFilter('sports', newSports);
  };

  return (
    <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl border border-purple-800/30 p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sports Selection */}
        <div>
          <label className="block text-purple-300 text-sm font-medium mb-2">
            Sports
          </label>
          <div className="flex flex-wrap gap-2">
            {SPORTS.map(sport => (
              <button
                key={sport.key}
                onClick={() => toggleSport(sport.key)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  filters.sports.includes(sport.key)
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-purple-300 hover:bg-slate-600'
                }`}
              >
                {sport.label}
              </button>
            ))}
          </div>
        </div>

        {/* Number of Legs */}
        <div>
          <label className="block text-purple-300 text-sm font-medium mb-2">
            Legs: {filters.numLegs}
          </label>
          <input
            type="range"
            min="2"
            max="10"
            value={filters.numLegs}
            onChange={(e) => updateFilter('numLegs', parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-purple-400 mt-1">
            <span>2</span>
            <span>10</span>
          </div>
        </div>

        {/* Min EV */}
        <div>
          <label className="block text-purple-300 text-sm font-medium mb-2">
            Min EV: {filters.minEV}%
          </label>
          <input
            type="range"
            min="0"
            max="20"
            step="0.5"
            value={filters.minEV}
            onChange={(e) => updateFilter('minEV', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Min Total EV */}
        <div>
          <label className="block text-purple-300 text-sm font-medium mb-2">
            Min Total EV: {filters.minTotalEV}%
          </label>
          <input
            type="range"
            min="0"
            max="30"
            step="0.5"
            value={filters.minTotalEV}
            onChange={(e) => updateFilter('minTotalEV', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      {/* Toggles */}
      <div className="flex items-center gap-6 mt-4 pt-4 border-t border-purple-800/30">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.mixedSports}
            onChange={(e) => updateFilter('mixedSports', e.target.checked)}
            className="w-5 h-5 rounded bg-slate-700 border-purple-600 text-purple-600 focus:ring-purple-500"
          />
          <span className="text-purple-300 text-sm font-medium">Mixed Sports</span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.prematch}
            onChange={(e) => updateFilter('prematch', e.target.checked)}
            className="w-5 h-5 rounded bg-slate-700 border-purple-600 text-purple-600 focus:ring-purple-500"
          />
          <span className="text-purple-300 text-sm font-medium">Prematch</span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.live}
            onChange={(e) => updateFilter('live', e.target.checked)}
            className="w-5 h-5 rounded bg-slate-700 border-purple-600 text-purple-600 focus:ring-purple-500"
          />
          <span className="text-purple-300 text-sm font-medium">Live</span>
        </label>
      </div>
    </div>
  );
}





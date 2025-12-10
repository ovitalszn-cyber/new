const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

export interface Filters {
  sports: string[];
  numLegs: number;
  minEV: number;
  minTotalEV: number;
  mixedSports: boolean;
  prematch: boolean;
  live: boolean;
}

export async function fetchSlips(filters: Filters) {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`;
  }

  let slips: any[] = [];

  if (filters.mixedSports && filters.sports.length > 1) {
    // Fetch mixed sports slips
    const response = await fetch(
      `${API_BASE_URL}/v4/dabble_slips/mixed?sports=${filters.sports.join(',')}&num_legs=${filters.numLegs}&min_ev_percentage=${filters.minEV}&min_total_ev_percentage=${filters.minTotalEV}&max_results=50`,
      { headers }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch mixed slips: ${response.statusText}`);
    }

    const mixedSlips = await response.json();
    slips.push(...mixedSlips);
  } else {
    // Fetch single-sport slips
    for (const sport of filters.sports) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/v4/sports/${sport}/dabble_slips?num_legs=${filters.numLegs}&min_ev_percentage=${filters.minEV}&min_total_ev_percentage=${filters.minTotalEV}&max_results=20`,
          { headers }
        );

        if (response.ok) {
          const sportSlips = await response.json();
          slips.push(...sportSlips);
        }
      } catch (error) {
        console.error(`Error fetching slips for ${sport}:`, error);
      }
    }
  }

  // Filter by prematch/live if needed
  // Note: This is a simple filter - you might want to enhance this based on commence_time
  if (!filters.prematch && !filters.live) {
    return [];
  }

  // Sort by EV descending
  slips.sort((a, b) => b.total_expected_value_percent - a.total_expected_value_percent);

  return slips;
}





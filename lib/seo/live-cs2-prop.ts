/** Live GET /v6/esports/cs2/props?book=prizepicks — pulled 2026-09-08 from kashrock.up.railway.app */

export const LIVE_CS2_PROP_PATH = "/v6/esports/cs2/props"

export const LIVE_CS2_PROP_SAMPLE = {
  source: "kashrock",
  sport: "cs2",
  props: [
    {
      propId: "kr_prop_959e4bdd3a1d",
      player_name: "Ax1Le",
      stat_type: "CS2_HEADSHOTS_MAPS_1_2",
      line: 15.5,
      odds: -137,
      direction: "over",
      team: "1win",
      book_name: "PrizePicks",
      event_time: "2026-09-09T08:00:00.000Z",
    },
  ],
} as const

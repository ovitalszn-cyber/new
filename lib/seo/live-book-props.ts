/** Live CS2 props from kashrock.up.railway.app — pulled 2026-09-10. */

export type LivePropRow = {
  propId: string
  player_name: string
  stat_type: string
  line: number
  odds: number
  direction: string
  team: string
  book_name: string
  event_time: string
}

function wrap(bookPath: string, row: LivePropRow) {
  return {
    path: bookPath,
    sample: {
      source: "kashrock",
      sport: "cs2",
      props: [row],
    },
  } as const
}

export const LIVE_PRIZEPICKS = wrap("/v6/esports/cs2/props?book=prizepicks", {
  propId: "kr_prop_da545d589900",
  player_name: "iDISBALANCE",
  stat_type: "CS2_HEADSHOTS_MAP_3",
  line: 5.5,
  odds: -110,
  direction: "over",
  team: "Bebop",
  book_name: "PrizePicks",
  event_time: "2026-09-10T13:00:00.000Z",
})

export const LIVE_UNDERDOG = wrap("/v6/esports/cs2/props?book=underdog", {
  propId: "kr_prop_26479ac3ae66",
  player_name: "clax",
  stat_type: "CS2_KILLS_MAPS_1_2",
  line: 27.5,
  odds: -112,
  direction: "over",
  team: "Nemiga",
  book_name: "Underdog",
  event_time: "2026-09-10T13:00:00.000Z",
})

export const LIVE_SLEEPER = wrap("/v6/esports/cs2/props?book=sleeper", {
  propId: "prop_1f518b1e573a9dfd",
  player_name: "nte",
  stat_type: "CS2_HEADSHOTS_MAPS_1_2",
  line: 16.5,
  odds: -158,
  direction: "over",
  team: "Ninjas in Pyjamas",
  book_name: "Sleeper",
  event_time: "",
})

export const LIVE_BETR = wrap("/v6/esports/cs2/props?book=betr", {
  propId: "kr_prop_e00ecb464ea8",
  player_name: "esenthial",
  stat_type: "CS2_HEADSHOTS_MAPS_1_2",
  line: 17.5,
  odds: -137,
  direction: "over",
  team: "B8",
  book_name: "Betr",
  event_time: "2026-09-10T14:00:00.000Z",
})

/** Live props pulled 2026-09-11 from upstream clients / production shape. */

export type LivePropRow = {
  propId: string
  player_name: string
  stat_type: string
  line: number | null
  odds: number | null
  direction: string
  team: string
  book_name: string
  event_time: string
}

function wrap(bookPath: string, sport: string, row: LivePropRow) {
  return {
    path: bookPath,
    sample: {
      source: "kashrock",
      sport,
      props: [row],
    },
  } as const
}

export const LIVE_PRIZEPICKS = wrap("/v6/esports/cs2/props?book=prizepicks", "cs2", {
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

export const LIVE_UNDERDOG = wrap("/v6/esports/cs2/props?book=underdog", "cs2", {
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

export const LIVE_SLEEPER = wrap("/v6/esports/cs2/props?book=sleeper", "cs2", {
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

export const LIVE_BETR = wrap("/v6/esports/cs2/props?book=betr", "cs2", {
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

export const LIVE_BOOM = wrap("/v6/esports/cs2/props?book=boom", "cs2", {
  propId: "8c9d0e9e-c56a-493e-8911-107bca7fb696",
  player_name: "doc",
  stat_type: "CS2_KILLS_MAPS_1_2",
  line: 32.5,
  odds: 1.76,
  direction: "over",
  team: "DENDELE CS",
  book_name: "Boom",
  event_time: "2026-09-11T20:00:00+00:00",
})

export const LIVE_PICK6 = wrap("/v6/esports/lol/props?book=pick6", "lol", {
  propId: "15994151",
  player_name: "Myrwn",
  stat_type: "LOL_KILLS_MAPS_1_3",
  line: 7.5,
  odds: null,
  direction: "over",
  team: "MKOI",
  book_name: "Pick6",
  event_time: "2026-09-12T15:00:00.0000000+00:00",
})

export const LIVE_THUNDERPICK = wrap("/v6/esports/cs2/props?book=thunderpick", "cs2", {
  propId: "prop_da111f08efb414ec",
  player_name: "SINQU Esports",
  stat_type: "MONEYLINE",
  line: null,
  odds: 530,
  direction: "home",
  team: "SINQU Esports",
  book_name: "Thunderpick",
  event_time: "2026-09-11T17:03:00+00:00",
})

export const LIVE_KALSHI = wrap("/v6/esports/cs2/props?book=kalshi", "cs2", {
  propId: "prop_60314492f9bf8781",
  player_name: "BOJONG",
  stat_type: "MONEYLINE",
  line: null,
  odds: 178,
  direction: "home",
  team: "BOJONG",
  book_name: "Kalshi",
  event_time: "2026-09-11T19:30:00Z",
})

export const LIVE_POLYMARKET = wrap("/v6/esports/cs2/props?book=polymarket", "cs2", {
  propId: "prop_5e73ad47ceb5bce8",
  player_name: "Quintessence",
  stat_type: "MONEYLINE_MAP_1",
  line: null,
  odds: 104,
  direction: "home",
  team: "Quintessence",
  book_name: "Polymarket",
  event_time: "2026-09-12T15:30:00+00:00",
})

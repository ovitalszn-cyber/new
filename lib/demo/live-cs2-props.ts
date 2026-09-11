/** Live CS2 prop sample for the landing try-me — never the full board. */

export const DEMO_PROPS_PATH = "/v6/demo/cs2-prop"

export type DemoCs2Prop = {
  propId: string
  player_name: string
  stat_type: string
  line: number
  odds: number | null
  direction: string
  team: string
  book_name: string
  event_time: string
  links: { market: string }
}

export type DemoCs2PropsResponse = {
  source: "kashrock"
  sport: "cs2"
  props: DemoCs2Prop[]
  ms?: number
}

const API_BASE =
  process.env.KASHROCK_API_BASE?.replace(/\/$/, "") ||
  "https://kashrock.up.railway.app"

const CACHE_TTL_MS = 45_000

type CacheEntry = { at: number; body: DemoCs2PropsResponse }

let cache: CacheEntry | null = null

export async function fetchLiveCs2PropSample(): Promise<DemoCs2PropsResponse> {
  const now = Date.now()
  if (cache && now - cache.at < CACHE_TTL_MS) {
    return { ...cache.body, ms: 0 }
  }

  const started = Date.now()
  const response = await fetch(`${API_BASE}${DEMO_PROPS_PATH}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  })
  if (!response.ok) {
    throw new Error(`Upstream demo returned ${response.status}`)
  }
  const data = (await response.json()) as DemoCs2PropsResponse
  if (!data?.props?.[0]) {
    throw new Error("No live CS2 props available")
  }

  const body: DemoCs2PropsResponse = {
    source: "kashrock",
    sport: "cs2",
    props: [data.props[0]],
    ms: Date.now() - started,
  }
  cache = { at: Date.now(), body }
  return body
}

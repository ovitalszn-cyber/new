export const API_BASE = 'https://kashrock.up.railway.app'

export const SPORTS = [
  { id: 'cs2', name: 'Counter-Strike 2' },
  { id: 'valorant', name: 'Valorant' },
  { id: 'lol', name: 'League of Legends' },
  { id: 'dota2', name: 'Dota 2' },
  { id: 'cod', name: 'Call of Duty' },
  { id: 'r6', name: 'Rainbow Six' },
  { id: 'mlbb', name: 'Mobile Legends' },
  { id: 'deadlock', name: 'Deadlock' },
] as const

export const BOOKS = [
  { id: 'prizepicks', name: 'PrizePicks' },
  { id: 'underdog', name: 'Underdog' },
  { id: 'parlayplay', name: 'ParlayPlay' },
  { id: 'dabble', name: 'Dabble' },
  { id: 'sleeper', name: 'Sleeper' },
  { id: 'betr', name: 'Betr' },
] as const

export type NavItem = { href: string; label: string; id: string }

export const DOC_NAV: { title: string; items: NavItem[] }[] = [
  {
    title: 'Start',
    items: [
      { href: '/docs', label: 'Overview', id: 'overview' },
      { href: '/docs#authentication', label: 'Authentication', id: 'authentication' },
    ],
  },
  {
    title: 'Endpoints',
    items: [
      { href: '/docs/endpoints/matches', label: 'Matches & fixtures', id: 'matches' },
      { href: '/docs/endpoints/rankings', label: 'Rankings', id: 'rankings' },
      { href: '/docs/endpoints/players', label: 'Players', id: 'players' },
      { href: '/docs/endpoints/props', label: 'Props', id: 'props' },
      { href: '/docs/endpoints/results', label: 'Results', id: 'results' },
      { href: '/docs/endpoints/research', label: 'Research', id: 'research' },
      { href: '/docs/endpoints/history', label: 'History tape', id: 'history' },
      { href: '/docs/endpoints/stacks', label: 'Stacks', id: 'stacks' },
    ],
  },
  {
    title: 'Reference',
    items: [
      { href: '/docs/reference/disciplines', label: 'Sports', id: 'sports' },
      { href: '/docs/reference/sportsbooks', label: 'Books', id: 'books' },
      { href: '/docs/markets', label: 'Markets', id: 'markets' },
      { href: '/docs/api-reference', label: 'Route index', id: 'index' },
      { href: '/docs#id-system', label: 'IDs', id: 'id-system' },
      { href: '/docs#errors', label: 'Errors', id: 'errors' },
    ],
  },
]

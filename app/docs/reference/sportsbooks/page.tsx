import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock } from '@/components/docs/Code'
import { BOOKS } from '@/lib/docs'
import { BOOK_LOGOS } from '@/lib/seo/book-logos'

const SAMPLE = {
  source: 'kashrock',
  total_books: 3,
  books: [
    { book_id: 1, key: 'prizepicks', display_name: 'PrizePicks' },
    { book_id: 9, key: 'thunderpick', display_name: 'Thunderpick' },
    { book_id: 10, key: 'kalshi', display_name: 'Kalshi' },
  ],
}

const LOGO_BY_NAME = Object.fromEntries(BOOK_LOGOS.map((b) => [b.name, b.src]))

const GROUPS: { title: string; blurb: string; ids: string[] }[] = [
  {
    title: 'DFS apps',
    blurb: 'Player props on the same propId schema.',
    ids: ['prizepicks', 'underdog', 'dabble', 'sleeper', 'betr', 'boom', 'pick6', 'parlayplay'],
  },
  {
    title: 'Sportsbook',
    blurb: 'Match/map mainlines and player props where listed.',
    ids: ['thunderpick'],
  },
  {
    title: 'Prediction markets',
    blurb: 'Probability-priced match/map markets. Feed GET /{sport}/lines consensus.',
    ids: ['kalshi', 'polymarket'],
  },
]

export default function BooksPage() {
  const byId = Object.fromEntries(BOOKS.map((b) => [b.id, b]))
  return (
    <DocsShell active="books">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Books</h1>
      <p className="text-lg text-zinc-400 mb-8">
        DFS apps:{' '}
        <Link href="/docs/endpoints/props" className="text-white underline">
          /props
        </Link>
        . DFS + Thunderpick named-player props:{' '}
        <Link href="/docs/endpoints/player-props" className="text-white underline">
          /player-props
        </Link>
        . Team mainlines (sportsbooks + Kalshi/Polymarket as themselves):{' '}
        <Link href="/docs/endpoints/lines" className="text-white underline">
          /lines
        </Link>
        . Registry: <code className="text-white">GET /v6/books</code>.
      </p>

      {GROUPS.map((group) => (
        <div key={group.title} className="mb-10">
          <h2 className="text-xl font-semibold text-white mb-2">{group.title}</h2>
          <p className="text-sm text-zinc-500 mb-4">{group.blurb}</p>
          <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-zinc-500">
                <tr>
                  <th className="py-3 px-4">Logo</th>
                  <th className="py-3 px-4">Key</th>
                  <th className="py-3 px-4">Name</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {group.ids.map((id) => {
                  const b = byId[id]
                  if (!b) return null
                  const logo = LOGO_BY_NAME[b.name]
                  return (
                    <tr key={b.id}>
                      <td className="py-3 px-4">
                        {logo ? (
                          <img
                            src={logo}
                            alt={b.name}
                            className="h-8 w-8 rounded-sm border border-white/10 object-cover"
                          />
                        ) : null}
                      </td>
                      <td className="py-3 px-4 font-mono text-emerald-400">{b.id}</td>
                      <td className="py-3 px-4 text-white">{b.name}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      <Curl path="/v6/books" />
      <JsonBlock title="200 · live" data={SAMPLE} />
      <Curl path="/v6/esports/cs2/props?book=parlayplay" />
      <p className="text-sm text-zinc-400 mt-6">
        Product pages:{' '}
        <Link href="/parlayplay-api" className="text-white underline">
          ParlayPlay
        </Link>
        {' · '}
        <Link href="/thunderpick-api" className="text-white underline">
          Thunderpick
        </Link>
        {' · '}
        <Link href="/kalshi-api" className="text-white underline">
          Kalshi
        </Link>
        {' · '}
        <Link href="/polymarket-api" className="text-white underline">
          Polymarket
        </Link>
        {' · '}
        <Link href="/esports-consensus-api" className="text-white underline">
          Consensus
        </Link>
      </p>
    </DocsShell>
  )
}

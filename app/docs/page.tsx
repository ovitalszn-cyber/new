import { Metadata } from 'next'
import Link from 'next/link'
import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock } from '@/components/docs/Code'
import { API_BASE, SPORTS } from '@/lib/docs'

export const metadata: Metadata = {
  title: 'API Documentation | KashRock',
  description: 'KashRock esports DaaS: live props, fixtures, settlements, and player research.',
}

const PROP_SAMPLE = {
  propId: 'kr_prop_883ba7a1e090',
  eventId: 'kr_ev_d9410a855f83',
  offerId: 'kr_prop_883ba7a1e090_6_over',
  book_name: 'Betr',
  player_name: 'mezii',
  stat_type: 'CS2_HEADSHOTS_MAPS_1_2',
  line: 14.5,
  direction: 'over',
  team: 'Team Vitality',
  opponent: 'Lynn Vision Gaming',
  event_time: '2026-08-16T13:55:00.000Z',
}

export default function DocsPage() {
  return (
    <DocsShell active="overview">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">
        Esports data API
      </h1>
      <p className="text-lg text-zinc-400 leading-relaxed mb-8">
        KashRock is a DaaS for esports books and apps. One key, one ID system, live ingested props, historical quote tape, and settled results. Base URL <code className="text-white">{API_BASE}</code>.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <div>
          <h3 className="text-white font-semibold mb-2">Live board</h3>
          <p className="text-sm text-zinc-400">Normalized props from PrizePicks, Underdog, ParlayPlay, Dabble, Sleeper, and Betr.</p>
        </div>
        <div>
          <h3 className="text-white font-semibold mb-2">Schedule</h3>
          <p className="text-sm text-zinc-400">Fixtures and matches for CS2, Valorant, LoL, Dota 2, COD, R6, MLBB, and Deadlock.</p>
        </div>
        <div>
          <h3 className="text-white font-semibold mb-2">Research</h3>
          <p className="text-sm text-zinc-400">One player, one market: live line, series totals, coverage, and settled outcomes.</p>
        </div>
        <div>
          <h3 className="text-white font-semibold mb-2">Settlement</h3>
          <p className="text-sm text-zinc-400">Hit / miss / push on the same canonical <code className="text-white">stat_type</code> you received on the board.</p>
        </div>
      </div>

      <hr className="border-white/5 mb-16" />

      <section id="quick-start" className="mb-20 scroll-mt-24">
        <h2 className="text-2xl font-semibold text-white mb-6">Quick start</h2>
        <p className="text-zinc-400 mb-6">HTTPS only. Pass your key on every <code className="text-white">/v6</code> request.</p>
        <Curl path="/v6/esports/props?game=cs2" />
        <JsonBlock title="200 · live prop" data={PROP_SAMPLE} />
      </section>

      <section id="authentication" className="mb-20 scroll-mt-24">
        <h2 className="text-2xl font-semibold text-white mb-6">Authentication</h2>
        <p className="text-zinc-400 mb-4">
          Create keys in the <Link href="/console" className="text-white underline">Console</Link>. Send either header:
        </p>
        <ul className="text-zinc-400 text-sm space-y-2 mb-6 list-disc pl-5">
          <li><code className="text-white">X-API-Key: YOUR_API_KEY</code></li>
          <li><code className="text-white">Authorization: Bearer YOUR_API_KEY</code></li>
        </ul>
        <p className="text-sm text-zinc-500">Keep keys server-side. Do not ship them in browsers or public repos.</p>
      </section>

      <section className="mb-20">
        <h2 className="text-2xl font-semibold text-white mb-6">Sports</h2>
        <p className="text-zinc-400 mb-4">Use the slug in the path as <code className="text-white">{'{sport}'}</code>, or <code className="text-white">game=</code> on props.</p>
        <div className="flex flex-wrap gap-2">
          {SPORTS.map((s) => (
            <code key={s.id} className="px-2 py-1 bg-white/5 border border-white/10 rounded text-xs text-emerald-400">
              {s.id}
            </code>
          ))}
        </div>
      </section>

      <section id="id-system" className="mb-20 scroll-mt-24">
        <h2 className="text-2xl font-semibold text-white mb-2">ID system</h2>
        <p className="text-zinc-400 mb-8">Every prop row carries five IDs. Use the <code className="text-white">kr_</code> fields to join books.</p>
        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-6">
          <table className="w-full text-left text-sm">
            <thead className="bg-white/5 text-zinc-500">
              <tr>
                <th className="px-4 py-3">Field</th>
                <th className="px-4 py-3">Layer</th>
                <th className="px-4 py-3">Purpose</th>
              </tr>
            </thead>
            <tbody className="text-zinc-400 divide-y divide-white/5">
              <tr>
                <td className="px-4 py-3 font-mono text-white">eventId</td>
                <td className="px-4 py-3">Match</td>
                <td className="px-4 py-3">Same game across every book.</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-mono text-white">propId</td>
                <td className="px-4 py-3">Market</td>
                <td className="px-4 py-3">Player + stat + line. Shared by over and under.</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-mono text-white">offerId</td>
                <td className="px-4 py-3">Selection</td>
                <td className="px-4 py-3">One book × direction. Use this on a bet slip.</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-mono text-white">source_event_id</td>
                <td className="px-4 py-3">Provider</td>
                <td className="px-4 py-3">Raw event id from the book.</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-mono text-white">source_prop_id</td>
                <td className="px-4 py-3">Provider</td>
                <td className="px-4 py-3">Raw prop id from the book.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section id="errors" className="mb-20 scroll-mt-24">
        <h2 className="text-2xl font-semibold text-white mb-6">Errors</h2>
        <p className="text-zinc-400 mb-6">JSON body with a <code className="text-white">detail</code> string.</p>
        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F]">
          <table className="w-full text-left text-sm">
            <thead className="bg-white/5 text-zinc-500">
              <tr>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Meaning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-zinc-400">
              <tr><td className="py-3 px-4 font-mono text-white">401</td><td className="py-3 px-4">Missing or invalid API key.</td></tr>
              <tr><td className="py-3 px-4 font-mono text-white">403</td><td className="py-3 px-4">Key is not allowed on this route.</td></tr>
              <tr><td className="py-3 px-4 font-mono text-white">404</td><td className="py-3 px-4">No tape or player for that query.</td></tr>
              <tr><td className="py-3 px-4 font-mono text-white">409</td><td className="py-3 px-4">More than one player matches the name.</td></tr>
              <tr><td className="py-3 px-4 font-mono text-white">422</td><td className="py-3 px-4">Bad or missing parameter.</td></tr>
              <tr><td className="py-3 px-4 font-mono text-white">429</td><td className="py-3 px-4">Rate limited. Back off and retry.</td></tr>
              <tr><td className="py-3 px-4 font-mono text-white">503</td><td className="py-3 px-4">Vault or cache unavailable. Retry.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </DocsShell>
  )
}

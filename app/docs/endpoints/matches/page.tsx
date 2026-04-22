import Link from 'next/link';

export default function MatchesEndpointPage() {
  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans">
      <header className="h-16 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md sticky top-0 z-50 flex items-center px-6 justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <img src="/kashrock-logo.svg" alt="KashRock" className="h-5 w-auto" />
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="https://backend.kashrock.com/docs" className="text-sm font-medium text-white">Documentation</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto py-12 px-6">
        <div className="mb-4">
          <Link href="https://backend.kashrock.com/docs" className="text-sm text-zinc-500 hover:text-white">&larr; Back to Docs</Link>
        </div>

        <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Matches</h1>
        <p className="text-lg text-zinc-400 mb-8">
          Retrieve live, upcoming, and finished matches across all supported esports disciplines.
        </p>

        <h2 className="text-xl font-semibold text-white mb-4">API Endpoint</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm mb-8">
          <span className="text-emerald-400">GET</span>
          <span className="text-zinc-300 ml-3">/v6/esports/{'{discipline}'}/matches</span>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Parameters</h2>
        <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-xs font-semibold uppercase tracking-wider text-zinc-500 border-b border-white/5">
                <th className="py-4 px-6">Parameter</th>
                <th className="py-4 px-6">Type</th>
                <th className="py-4 px-6">Required</th>
                <th className="py-4 px-6">Description</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-white/5">
              <tr>
                <td className="py-4 px-6 font-mono text-white">discipline</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6"><span className="text-emerald-400">✓</span></td>
                <td className="py-4 px-6 text-zinc-400">Game slug: <code className="text-white">cs2</code>, <code className="text-white">valorant</code>, <code className="text-white">lol</code>, <code className="text-white">dota-2</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">status</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Filter by status: <code className="text-white">live</code>, <code className="text-white">upcoming</code>, <code className="text-white">finished</code></td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">start_date</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Filter by start date (YYYY-MM-DD)</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">end_date</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Filter by end date (YYYY-MM-DD)</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">league_id</td>
                <td className="py-4 px-6 text-zinc-400">string</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Filter by league/tournament ID</td>
              </tr>
              <tr>
                <td className="py-4 px-6 font-mono text-white">limit</td>
                <td className="py-4 px-6 text-zinc-400">integer</td>
                <td className="py-4 px-6 text-zinc-600">—</td>
                <td className="py-4 px-6 text-zinc-400">Max results to return (default: 50, max: 100)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example URLs</h2>
        <div className="space-y-4 mb-8">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">CS2 live matches:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/cs2/matches?status=live
            </code>
          </div>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4">
            <p className="text-zinc-500 text-xs mb-2">Valorant upcoming matches for specific date:</p>
            <code className="text-zinc-300 text-sm font-mono">
              /v6/esports/valorant/matches?status=upcoming&start_date=2026-04-20
            </code>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-white mb-4">Example Response</h2>
        <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-xs mb-8">
          <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500">
            Response
          </div>
          <pre className="p-4 overflow-x-auto text-zinc-300">
{`{
  "source": "kashrock",
  "discipline": "valorant",
  "updated": "2026-04-20T16:21:00.000Z",
  "matches": [
    {
      "slug": "twisted-minds-orchid-vs-fokus-sakura-2026-05-14",
      "status": "upcoming",
      "videogame": {
        "id": 26,
        "name": "Valorant",
        "slug": "valorant"
      },
      "opponents": [
        {
          "type": "Team",
          "opponent": {
            "id": 136929,
            "name": "Twisted Minds Orchid",
            "slug": "twisted-minds-orchid",
            "acronym": "TMO",
            "image_url": "https://cdn-api.pandascore.co/images/team/image/136929/600px_twisted_minds_2023_full_lightmode.png"
          }
        },
        {
          "type": "Team",
          "opponent": {
            "id": 133128,
            "name": "FOKUS Sakura",
            "slug": "fokus-sakura",
            "acronym": "FKS",
            "image_url": "https://cdn-api.pandascore.co/images/team/image/133128/600px_fokus_2022_allmode.png"
          }
        }
      ],
      "streams_list": [
        {
          "main": true,
          "language": "en",
          "embed_url": "https://player.twitch.tv/?channel=valorant_emea2",
          "official": true,
          "raw_url": "https://www.twitch.tv/valorant_emea2"
        }
      ],
      "games": [
        {
          "id": 48516,
          "position": 1,
          "status": "not_started",
          "finished": false
        }
      ]
    }
  ]
}`}
</pre>
        </div>

        <div className="flex gap-4 mt-12">
          <Link href="/docs/endpoints/rankings" className="text-sm text-emerald-400 hover:text-emerald-300">
            Next: Rankings →
          </Link>
        </div>
      </div>
    </div>
  );
}

import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'DFS Esports API | KashRock',
  description: 'KashRock is a dfs esports api for builders — slates, props, player game logs, results grading, and media with stable IDs. Get normalized esports data for your DFS applications.',
  alternates: {
    canonical: 'https://www.kashrock.com/dfs-esports-api',
  },
  openGraph: {
    title: 'DFS Esports API | KashRock',
    description: 'KashRock is a dfs esports api for builders — slates, props, player game logs, results grading, and media with stable IDs.',
    url: 'https://www.kashrock.com/dfs-esports-api',
    siteName: 'KashRock',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DFS Esports API | KashRock',
    description: 'KashRock is a dfs esports api for builders — slates, props, player game logs, results grading, and media with stable IDs.',
  },
};

export default function DFSEsportsAPIPage() {
  return (
    <div className="min-h-screen bg-[#0A0B0C] text-white">
      <div className="max-w-4xl mx-auto px-6 py-24">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-medium tracking-tight text-white mb-6">
            DFS Esports API
          </h1>
          <p className="text-xl text-zinc-300 leading-relaxed max-w-3xl mx-auto">
            KashRock is a dfs esports api for builders — slates, props, player game logs, results grading, and media with stable IDs.
          </p>
        </div>

        {/* What you get Section */}
        <section className="mb-16">
          <h2 className="text-2xl font-medium text-white mb-8">What you get</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Slates</h3>
              <p className="text-zinc-400">Upcoming, live, and completed esports slates with normalized data structures</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">DFS props</h3>
              <p className="text-zinc-400">Normalized markets across all major esports titles and DFS platforms</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Player game logs</h3>
              <p className="text-zinc-400">Comprehensive player statistics and historical performance data</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Results + grading</h3>
              <p className="text-zinc-400">Hit/miss/push grading for all props with automated result processing</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Player headshots + team logos</h3>
              <p className="text-zinc-400">High-quality media assets for all players and teams in our database</p>
            </div>
          </div>
        </section>

        {/* Quickstart Section */}
        <section className="mb-16">
          <h2 className="text-2xl font-medium text-white mb-8">Quickstart</h2>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10">
              <h3 className="text-sm font-medium text-zinc-400">Example request</h3>
            </div>
            <div className="p-6">
              <pre className="text-sm text-zinc-300 overflow-x-auto">
                <code>{`curl -X GET \\
  "https://api.kashrock.com/v6/esports/props?game=cs2&date=today" \\
  -H "Authorization: Bearer YOUR_API_KEY"`}</code>
              </pre>
            </div>
          </div>
        </section>

        {/* Example Response Section */}
        <section className="mb-16">
          <h2 className="text-2xl font-medium text-white mb-8">Example response</h2>
          <div className="bg-[#0C0D0F] border border-white/10 rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10">
              <h3 className="text-sm font-medium text-zinc-400">Sanitized JSON response</h3>
            </div>
            <div className="p-6">
              <pre className="text-sm text-zinc-300 overflow-x-auto">
                <code>{`{
  "source": "kashrock",
  "sport": "cs2",
  "projections": [
    {
      "projection_id": "proj_233510",
      "player_name": "Mol011",
      "stat_type": "CS2_MAPS_1-2_KILLS",
      "line": 26.5,
      "direction": "over",
      "team": "AaB Elite",
      "opponent": "AMKAL",
      "event_time": "2025-11-30T09:00:00Z",
      "status": "pre_game",
      "links": {
        "bet": "[redacted]"
      }
    }
  ]
}`}</code>
              </pre>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="mb-16">
          <h2 className="text-2xl font-medium text-white mb-8">FAQ</h2>
          <div className="space-y-6">
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Which esports games are supported?</h3>
              <p className="text-zinc-400">We support all major esports titles including CS2, League of Legends, Dota 2, Valorant, and more. Our coverage continues to expand based on market demand.</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Do you provide live + historical data?</h3>
              <p className="text-zinc-400">Yes, we provide both real-time live data and comprehensive historical data for all supported esports titles and markets.</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">Do you grade props (hit/miss)?</h3>
              <p className="text-zinc-400">Yes, we automatically grade all props with hit/miss/push results as soon as matches complete, providing instant feedback for your DFS applications.</p>
            </div>
            <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">How do I get an API key?</h3>
              <p className="text-zinc-400">Request access to KashRock via the console to get your API key. All plans are paid with published RPM limits so you can go live immediately.</p>
            </div>
          </div>
        </section>

        {/* CTAs */}
        <section className="text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="/console" 
              className="inline-flex items-center justify-center px-6 py-3 bg-white text-black font-medium rounded-lg hover:bg-zinc-200 transition-colors"
            >
              Get API Key
            </a>
            <a 
              href="/docs" 
              className="inline-flex items-center justify-center px-6 py-3 bg-[#0C0D0F] border border-white/10 text-white font-medium rounded-lg hover:bg-white/5 transition-colors"
            >
              Read Docs
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}

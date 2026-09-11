import type { Metadata } from "next"

import { MarketingShell } from "@/components/seo/MarketingShell"
import { COVERAGE_DESCRIPTION, COVERAGE_TITLE } from "@/lib/seo/book-api-copy"

export const metadata: Metadata = {
  title: { absolute: COVERAGE_TITLE },
  description: COVERAGE_DESCRIPTION,
  alternates: { canonical: "/coverage" },
}

const TITLES = [
  "CS2",
  "League of Legends",
  "Dota 2",
  "Valorant",
  "Call of Duty",
  "Rainbow Six Siege",
  "Mobile Legends",
  "Deadlock",
]

const BOOKS = ["PrizePicks", "Underdog", "Betr", "Sleeper", "Dabble", "ParlayPlay"]

const FEEDS: [string, string][] = [
  ["Player props & lines", "All titles above"],
  ["Match schedules & fixtures", "All titles above"],
  ["Player stats / box scores / game logs", "CS2, LoL, Dota 2, Valorant"],
  ["Outcome verification (hit / miss / push)", "All prop titles"],
  ["Historical prop tape", "Indexed to player game logs"],
]

export default function CoveragePage() {
  return (
    <MarketingShell>
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Coverage.
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-light leading-relaxed">
            Everything KashRock covers, in one place. One key, one schema across every title and book below.
          </p>
        </div>
      </section>

      <section className="py-12 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-10">
        <div>
          <h2 className="text-2xl font-medium tracking-tight text-white mb-6">Titles</h2>
          <ul className="space-y-2">
            {TITLES.map((t) => (
              <li
                key={t}
                className="bg-[#0C0D0F] border border-white/10 rounded-sm px-4 py-3 text-zinc-300"
              >
                {t}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2 className="text-2xl font-medium tracking-tight text-white mb-6">Books normalized</h2>
          <ul className="space-y-2">
            {BOOKS.map((b) => (
              <li
                key={b}
                className="bg-[#0C0D0F] border border-white/10 rounded-sm px-4 py-3 text-zinc-300"
              >
                <a
                  href={
                    b === "PrizePicks"
                      ? "/prizepicks-api"
                      : b === "Underdog"
                        ? "/underdog-api"
                        : b === "Betr"
                          ? "/betr-api"
                          : b === "Sleeper"
                            ? "/sleeper-api"
                            : "/dfs-esports-api"
                  }
                  className="hover:text-white"
                >
                  {b}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-2xl font-medium tracking-tight text-white mb-6">Data feeds</h2>
        <div className="overflow-x-auto border border-white/10 rounded-sm bg-[#0C0D0F]">
          <table className="w-full text-left text-sm">
            <thead className="bg-white/5 text-zinc-500">
              <tr>
                <th className="px-4 py-3 font-medium">Feed</th>
                <th className="px-4 py-3 font-medium">Coverage</th>
              </tr>
            </thead>
            <tbody className="text-zinc-300 divide-y divide-white/5">
              {FEEDS.map(([feed, coverage]) => (
                <tr key={feed}>
                  <td className="px-4 py-3 text-white">{feed}</td>
                  <td className="px-4 py-3">{coverage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-base text-zinc-400 mt-10">
          Start on the{" "}
          <a href="/esports-data-api" className="text-white underline">
            esports data API
          </a>
          , the{" "}
          <a href="/historical-esports-data-api" className="text-white underline">
            historical esports data API
          </a>
          , or the{" "}
          <a href="/dfs-esports-api" className="text-white underline">
            DFS Esports API
          </a>
          .{" "}
          <a href="/docs" className="text-white underline">
            Docs
          </a>{" "}
          ·{" "}
          <a href="/#pricing" className="text-white underline">
            Pricing
          </a>
          .
        </p>
      </section>
    </MarketingShell>
  )
}

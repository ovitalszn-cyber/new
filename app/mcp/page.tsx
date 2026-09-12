import type { Metadata } from "next"
import Link from "next/link"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { SportLogoRow } from "@/components/seo/SportLogoRow"
import {
  MCP_GROUP_LABEL,
  MCP_SPORTS,
  MCP_TIER_LABEL,
  MCP_TOOLS,
  type McpTool,
} from "@/lib/mcp/catalog"
import {
  MCP_DESCRIPTION,
  MCP_FAQS,
  MCP_SNIPPET,
  MCP_STEPS,
  MCP_TITLE,
} from "@/lib/seo/copy"
import { mcpJsonLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: { absolute: MCP_TITLE },
  description: MCP_DESCRIPTION,
  alternates: { canonical: "https://www.kashrock.com/mcp" },
  keywords: [
    "kashrock mcp",
    "cursor esports api",
    "claude mcp prizepicks",
    "esports api cursor",
    "cs2 props mcp",
    "uvx kashrock-mcp",
  ],
  openGraph: {
    title: MCP_TITLE,
    description: MCP_DESCRIPTION,
    url: "https://www.kashrock.com/mcp",
    siteName: "KashRock",
  },
  twitter: { card: "summary_large_image", title: MCP_TITLE, description: MCP_DESCRIPTION },
}

const PROMPTS = [
  "Log in to KashRock, then whoami.",
  "Show CS2 Kalshi and Polymarket moneylines for tonight.",
  "Pull PrizePicks and ParlayPlay CS2 kills for Vitality.",
  "ZywOo last 10 maps and grade an Underdog kills prop.",
  "suggest_build: DFS board + live streams for LoL",
  "Head-to-head: Vitality vs MOUZ — then live streams.",
]

const TIERS = [
  {
    plan: "Sandbox",
    gets: "login, whoami, capabilities, CS2 props + coverage, list_sports / markets",
  },
  {
    plan: "Hobby",
    gets: "All 8 sports · moneylines · consensus lines · research · rankings · streams · H2H",
  },
  {
    plan: "Builder+",
    gets: "Matches, search, gamelogs, boxscores, results, history tape",
  },
]

const GROUPS: McpTool["group"][] = ["session", "board", "players", "schedule"]

export default function McpPage() {
  return (
    <MarketingShell>
      <JsonLd data={mcpJsonLd()} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Ask Cursor.
            <br />
            <span className="seo-grad">Don&apos;t read the docs.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            Thirty seconds. Paste one snippet. Log in with Google. Your agent gets the full
            KashRock surface for your plan — props, moneylines, consensus lines, research, and
            (on Builder) history. Install: <code className="text-white text-base">uvx kashrock-mcp</code>.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href="#setup"
              className="px-6 py-3 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 text-center"
            >
              Copy setup
            </a>
            <Link
              href="/docs/mcp"
              className="px-6 py-3 border border-white/20 text-white text-sm font-medium rounded-sm hover:bg-white/5 text-center"
            >
              Full tool docs
            </Link>
          </div>
        </div>
      </section>

      <section className="pb-8 max-w-7xl mx-auto px-6">
        <SportLogoRow className="mb-4" />
        <p className="text-center text-sm text-zinc-500 mb-16">
          {MCP_SPORTS.join(" · ")}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-16">
          {MCP_STEPS.map((step) => (
            <div key={step.n} className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
              <p className="text-sm text-zinc-500 mb-3">{step.n}</p>
              <h2 className="text-xl font-medium text-white mb-2">{step.title}</h2>
              <p className="text-base text-zinc-400 leading-relaxed">{step.body}</p>
            </div>
          ))}
        </div>

        <div id="setup" className="bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden mb-16 scroll-mt-24">
          <div className="flex items-center px-4 py-3 border-b border-white/5 bg-white/[0.02]">
            <div className="text-xs font-mono text-zinc-500">Cursor → Settings → MCP</div>
          </div>
          <pre className="p-5 font-mono text-xs leading-normal overflow-x-auto text-zinc-300">
            {MCP_SNIPPET}
          </pre>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-16">
          <div>
            <h2 className="text-2xl font-medium text-white mb-4">What your plan unlocks</h2>
            <ul className="space-y-3">
              {TIERS.map((row) => (
                <li key={row.plan} className="border-b border-white/5 pb-3">
                  <p className="text-white font-medium">{row.plan}</p>
                  <p className="text-sm text-zinc-400">{row.gets}</p>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-medium text-white mb-4">Try saying</h2>
            <ul className="space-y-3">
              {PROMPTS.map((p) => (
                <li
                  key={p}
                  className="text-sm text-zinc-300 font-mono bg-black/40 border border-white/5 rounded-sm px-4 py-3"
                >
                  {p}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div id="tools" className="mb-16 scroll-mt-24">
          <h2 className="text-2xl font-medium text-white mb-2">Full tool catalog</h2>
          <p className="text-sm text-zinc-500 mb-8">
            Same surface as <code className="text-zinc-400">list_capabilities</code>. Stacks are not exposed via MCP.
          </p>
          {GROUPS.map((group) => (
            <div key={group} className="mb-10">
              <h3 className="text-lg font-medium text-white mb-4">{MCP_GROUP_LABEL[group]}</h3>
              <div className="overflow-x-auto border border-white/10 rounded-sm bg-[#0C0D0F]">
                <table className="w-full text-left text-sm">
                  <thead className="bg-white/5 text-zinc-500">
                    <tr>
                      <th className="px-4 py-3 font-medium">Tool</th>
                      <th className="px-4 py-3 font-medium">When to use</th>
                      <th className="px-4 py-3 font-medium">Plan</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-zinc-400">
                    {MCP_TOOLS.filter((t) => t.group === group).map((t) => (
                      <tr key={t.id}>
                        <td className="px-4 py-3 font-mono text-emerald-400 whitespace-nowrap">{t.id}</td>
                        <td className="px-4 py-3">{t.when}</td>
                        <td className="px-4 py-3 whitespace-nowrap">{MCP_TIER_LABEL[t.tier]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </section>
      <FaqGrid faqs={MCP_FAQS} />
    </MarketingShell>
  )
}

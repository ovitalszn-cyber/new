import type { Metadata } from "next"
import Link from "next/link"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
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
  "Show CS2 Kalshi and Polymarket moneylines for tonight.",
  "Pull PrizePicks CS2 kills for Vitality players.",
  "ZywOo last 10 maps and grade an Underdog kills prop.",
  "Head-to-head: Vitality vs MOUZ — then live streams.",
]

const TIERS = [
  { plan: "Sandbox", gets: "CS2 props schema checks" },
  { plan: "Hobby", gets: "All-sport props, lines, research, H2H, streams" },
  { plan: "Builder+", gets: "Schedule, gamelogs, boxscores, results, history tape" },
]

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
            KashRock board for your plan — props, moneylines, consensus lines, research, and
            (on Builder) history.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href="#setup"
              className="px-6 py-3 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 text-center"
            >
              Copy setup
            </a>
            <Link
              href="/pricing"
              className="px-6 py-3 border border-white/20 text-white text-sm font-medium rounded-sm hover:bg-white/5 text-center"
            >
              See plans
            </Link>
          </div>
        </div>
      </section>

      <section className="pb-16 max-w-7xl mx-auto px-6">
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
      </section>
      <FaqGrid faqs={MCP_FAQS} />
    </MarketingShell>
  )
}

import type { Metadata } from "next"

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

export default function McpPage() {
  return (
    <MarketingShell>
      <JsonLd data={mcpJsonLd()} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Ask Cursor.<br />
            <span className="seo-grad">Don&apos;t read the docs.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            Thirty seconds. Paste one snippet. Log in with Google. Then ask for CS2, LoL, Dota, or Valorant props in plain English.
          </p>
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
        <div className="bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden">
          <div className="flex items-center px-4 py-3 border-b border-white/5 bg-white/[0.02]">
            <div className="text-xs font-mono text-zinc-500">Cursor → Settings → MCP</div>
          </div>
          <pre className="p-5 font-mono text-xs leading-normal overflow-x-auto text-zinc-300">{MCP_SNIPPET}</pre>
        </div>
      </section>
      <FaqGrid faqs={MCP_FAQS} />
    </MarketingShell>
  )
}

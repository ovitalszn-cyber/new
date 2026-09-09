import type { ReactNode } from "react"

import LandingAuthNav from "@/components/LandingAuthNav"

const NAV = [
  { href: "/#features", label: "Features" },
  { href: "/#how-it-works", label: "How it works" },
  { href: "/#pricing", label: "Pricing" },
  { href: "/mcp", label: "MCP" },
  { href: "/docs", label: "Docs" },
] as const

export function MarketingShell({ children }: { children: ReactNode }) {
  return (
    <div
      className="antialiased selection:bg-white/20 selection:text-white min-h-screen"
      style={{ fontFamily: "Inter, sans-serif", backgroundColor: "#08090A", color: "#E3E5E7" }}
    >
      <style>{`
        @import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap");
        .seo-glass { background: rgba(8, 9, 10, 0.7); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.08); }
        .seo-grad { background: linear-gradient(to right, #ffffff, #a1a1aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .seo-grid { background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 40px 40px; }
      `}</style>
      <nav className="fixed top-0 w-full z-50 seo-glass">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <a href="/"><img src="/kashrock-logo.svg" alt="KashRock" className="h-10 w-auto" /></a>
          <div className="hidden md:flex items-center gap-8">
            {NAV.map((item) => (
              <a key={item.href} href={item.href} className="text-sm font-normal text-zinc-400 hover:text-white transition-colors">
                {item.label}
              </a>
            ))}
          </div>
          <LandingAuthNav />
        </div>
      </nav>
      {children}
      <footer className="border-t border-white/5 bg-[#050505] pt-16 pb-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-zinc-600">© 2026 KashRock Inc. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <a href="/esports-data-api" className="text-sm text-zinc-600 hover:text-white">Esports Data API</a>
            <a href="/dfs-esports-api" className="text-sm text-zinc-600 hover:text-white">DFS Esports API</a>
            <a href="/mcp" className="text-sm text-zinc-600 hover:text-white">MCP</a>
            <a href="/docs" className="text-sm text-zinc-600 hover:text-white">Docs</a>
            <a href="/legal" className="text-sm text-zinc-600 hover:text-white">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

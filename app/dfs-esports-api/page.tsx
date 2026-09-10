import type { Metadata } from "next"

import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { PropCode } from "@/components/seo/PropCode"
import { DFS_DESCRIPTION, DFS_FAQS, DFS_TITLE } from "@/lib/seo/copy"
import { BOOK_LOGOS } from "@/lib/seo/book-logos"
import { GAME_LOGOS } from "@/lib/seo/game-logos"
import { dfsJsonLd } from "@/lib/seo/schema"

export const metadata: Metadata = {
  title: DFS_TITLE,
  description: DFS_DESCRIPTION,
  alternates: { canonical: "https://www.kashrock.com/dfs-esports-api" },
  keywords: [
    "dfs esports api",
    "prizepicks api",
    "underdog api",
    "cs2 player props api",
    "lol dfs data",
    "esports odds api",
  ],
  openGraph: {
    title: DFS_TITLE,
    description: DFS_DESCRIPTION,
    url: "https://www.kashrock.com/dfs-esports-api",
    siteName: "KashRock",
  },
  twitter: { card: "summary_large_image", title: DFS_TITLE, description: DFS_DESCRIPTION },
}

export default function DfsEsportsApiPage() {
  return (
    <MarketingShell>
      <JsonLd data={dfsJsonLd()} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[100px] rounded-full pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            DFS Esports API.<br />
            <span className="seo-grad">PrizePicks & Underdog for CS2 & LoL.</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            Affordable player props API with an instant key. Pull PrizePicks, Underdog, Betr, and Sleeper lines for CS2 and League of Legends — plus Dabble and ParlayPlay — from one path: GET /v6/esports/{"{sport}"}/props.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a href="/#pricing" className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200">
              Get API Key
            </a>
            <a href="/docs/endpoints/props" className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900">
              Read Documentation
            </a>
          </div>
          <div className="mt-14 flex flex-wrap items-center justify-center gap-x-8 gap-y-4">
            {GAME_LOGOS.map((logo) => (
              <img key={logo.alt} src={logo.src} alt={logo.alt} className={`h-8 w-auto ${logo.invert ? "invert" : ""}`} />
            ))}
          </div>
        </div>
      </section>
      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-4">
          One DFS board. <span className="text-zinc-500">Every book you actually use.</span>
        </h2>
        <p className="text-lg text-zinc-400 max-w-3xl mb-10">
          Filter by book on the path-style props route. PrizePicks and Underdog share the same player, market, and propId as Betr, Sleeper, Dabble, and ParlayPlay.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-16">
          {BOOK_LOGOS.map((book) => (
            <div key={book.name} className="bg-[#0C0D0F] border border-white/10 rounded-sm px-4 py-4 flex flex-col items-center gap-2">
              <img src={book.src} alt={book.name} className="h-12 w-12 rounded-xl object-cover" />
              <span className="text-sm text-white">{book.name}</span>
            </div>
          ))}
        </div>
        <div className="flex flex-col lg:flex-row gap-16 items-center">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
              GET /v6/esports/{"{sport}"}/props
            </h2>
            <p className="text-lg text-zinc-500 mb-6">
              Live PrizePicks CS2 prop from production. Same shape for Underdog and LoL DFS data.
            </p>
            <div className="flex flex-col gap-2 text-sm text-zinc-400 mb-6">
              <a href="/prizepicks-api" className="hover:text-white">PrizePicks API →</a>
              <a href="/underdog-api" className="hover:text-white">Underdog API →</a>
              <a href="/sleeper-api" className="hover:text-white">Sleeper API →</a>
              <a href="/betr-api" className="hover:text-white">Betr API →</a>
              <a href="/blog/how-to-get-prizepicks-props-api" className="hover:text-white">How to get PrizePicks props without scraping →</a>
              <a href="/coverage" className="hover:text-white">Full coverage matrix →</a>
            </div>
            <a href="/esports-data-api" className="text-sm text-zinc-400 hover:text-white">
              Need the broader esports data API? →
            </a>
          </div>
          <div className="flex-1 w-full max-w-2xl">
            <PropCode />
          </div>
        </div>
      </section>
      <section className="py-24 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">Frequently asked questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DFS_FAQS.map((faq) => (
            <div key={faq.q} className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
              <h3 className="text-lg font-medium text-white mb-2">{faq.q}</h3>
              <p className="text-base text-zinc-400 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </section>
    </MarketingShell>
  )
}

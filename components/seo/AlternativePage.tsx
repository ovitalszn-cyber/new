import type { ReactNode } from "react"

import { CompareTable } from "@/components/seo/CompareTable"
import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { faqPageLd } from "@/lib/seo/schema"

type Faq = { q: string; a: string }

type AlternativePageProps = {
  jsonLdFaqs: readonly Faq[]
  h1: ReactNode
  lede: ReactNode
  compareTitle: string
  headers: readonly string[]
  rows: readonly (readonly string[])[]
  reasonsTitle: string
  reasons: string[]
  related: ReactNode
}

export function AlternativePage({
  jsonLdFaqs,
  h1,
  lede,
  compareTitle,
  headers,
  rows,
  reasonsTitle,
  reasons,
  related,
}: AlternativePageProps) {
  return (
    <MarketingShell>
      <JsonLd data={faqPageLd(jsonLdFaqs)} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            {h1}
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            {lede}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/pricing"
              className="w-full sm:w-auto px-8 py-3.5 bg-white text-black text-base font-medium rounded-sm hover:bg-zinc-200"
            >
              Get API Key
            </a>
            <a
              href="/docs"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-zinc-700 text-white text-base font-medium rounded-sm hover:bg-zinc-900"
            >
              Read Documentation
            </a>
          </div>
        </div>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-10">
          {compareTitle}
        </h2>
        <CompareTable headers={headers} rows={rows} />
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">
          {reasonsTitle}
        </h2>
        <ul className="space-y-4 max-w-3xl">
          {reasons.map((item) => (
            <li key={item} className="flex items-start gap-3 text-base text-zinc-300">
              <span className="text-white mt-0.5">—</span>
              {item}
            </li>
          ))}
        </ul>
        <p className="text-base text-zinc-400 mt-10">{related}</p>
      </section>

      <FaqGrid faqs={jsonLdFaqs} />
    </MarketingShell>
  )
}

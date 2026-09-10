import type { ReactNode } from "react"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { PropCode } from "@/components/seo/PropCode"
import { appFaqGraphLd } from "@/lib/seo/schema"

type Faq = { q: string; a: string }

type BookApiPageProps = {
  brand: string
  h1Line2: string
  lede: ReactNode
  bullets: string[]
  endpointLabel: string
  samplePath: string
  sample: unknown
  faqs: readonly Faq[]
  disclaimer: string
  related: ReactNode
  jsonLdName: string
}

export function BookApiPage({
  brand,
  h1Line2,
  lede,
  bullets,
  endpointLabel,
  samplePath,
  sample,
  faqs,
  disclaimer,
  related,
  jsonLdName,
}: BookApiPageProps) {
  return (
    <MarketingShell>
      <JsonLd data={appFaqGraphLd(jsonLdName, faqs)} />
      <section className="relative pt-24 pb-20 md:pt-40 md:pb-24 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-white/5 blur-[100px] rounded-full pointer-events-none" />
        <div className="max-w-5xl mx-auto px-6 relative z-10 text-center">
          <h1 className="text-5xl md:text-7xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            {brand} API.
            <br />
            <span className="seo-grad">{h1Line2}</span>
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 font-light leading-relaxed">
            {lede}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/#pricing"
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
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">
          What you get
        </h2>
        <ul className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {bullets.map((item) => (
            <li
              key={item}
              className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8 text-base text-zinc-400 leading-relaxed"
            >
              {item}
            </li>
          ))}
        </ul>
      </section>

      <section className="py-16 max-w-7xl mx-auto px-6">
        <div className="flex flex-col lg:flex-row gap-16 items-center">
          <div className="flex-1">
            <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
              {endpointLabel}
            </h2>
            <p className="text-lg text-zinc-500 mb-6">
              Live {brand} CS2 prop from production.
            </p>
            <div className="text-base text-zinc-400 leading-relaxed">{related}</div>
          </div>
          <div className="flex-1 w-full max-w-2xl">
            <PropCode path={samplePath} sample={sample} />
          </div>
        </div>
      </section>

      <FaqGrid faqs={faqs} />

      <section className="pb-24 max-w-7xl mx-auto px-6">
        <p className="text-xs text-zinc-600 leading-relaxed max-w-3xl">{disclaimer}</p>
      </section>
    </MarketingShell>
  )
}

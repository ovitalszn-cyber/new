import type { ReactNode } from "react"

import { FaqGrid } from "@/components/seo/FaqGrid"
import { JsonLd } from "@/components/seo/JsonLd"
import { MarketingShell } from "@/components/seo/MarketingShell"
import { PropCode } from "@/components/seo/PropCode"
import {
  RefSection,
  RefTable,
  RefToc,
} from "@/components/seo/reference"
import { appFaqGraphLd, softwareApplicationLd } from "@/lib/seo/schema"

export type SportRefFaq = { q: string; a: string }

export type SportRefContent = {
  path: string
  title: string
  description: string
  keywords: string[]
  jsonLdName: string
  h1: ReactNode
  lede: string
  toc: { id: string; label: string; children?: { id: string; label: string }[] }[]
  samplePath: string
  sample: unknown
  endpointRows: string[][]
  fieldRows: string[][]
  sourceRows: string[][]
  faqs: readonly SportRefFaq[]
  relatedLinks: { href: string; label: string }[]
  sections: {
    why: ReactNode
    schema: ReactNode
    endpoints: ReactNode
    ids: ReactNode
    sample: ReactNode
    sources: ReactNode
    grading: ReactNode
    ops: ReactNode
    quick: ReactNode
  }
}

export function SportReferencePage({ content }: { content: SportRefContent }) {
  const url = `https://www.kashrock.com${content.path}`
  return (
    <MarketingShell>
      <JsonLd
        data={[
          softwareApplicationLd({
            name: content.jsonLdName,
            url,
            description: content.description,
          }),
          appFaqGraphLd(content.jsonLdName, content.faqs),
          {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            headline: content.title,
            description: content.description,
            author: { "@type": "Organization", name: "KashRock" },
            mainEntityOfPage: url,
          },
        ]}
      />

      <article className="relative pt-24 pb-8 md:pt-36 md:pb-12 overflow-hidden">
        <div className="absolute inset-0 seo-grid opacity-30 pointer-events-none" />
        <div className="max-w-3xl mx-auto px-6 relative z-10">
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            {content.h1}
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 mb-8 font-light leading-relaxed">
            {content.lede}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 mb-12">
            <a
              href="/pricing"
              className="px-6 py-3 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 text-center"
            >
              Get API Key
            </a>
            <a
              href="/docs/endpoints/props"
              className="px-6 py-3 border border-zinc-700 text-white text-sm font-medium rounded-sm hover:bg-zinc-900 text-center"
            >
              Props docs
            </a>
          </div>

          <RefToc items={content.toc} />

          <RefSection id="why" title={String(content.toc[0]?.label || "Why this needs a schema")}>
            {content.sections.why}
          </RefSection>

          <RefSection id="schema" title={String(content.toc[1]?.label || "What the record represents")}>
            {content.sections.schema}
          </RefSection>

          <RefSection id="endpoints" title={String(content.toc[2]?.label || "Core endpoints")}>
            {content.sections.endpoints}
            <RefTable
              headers={["Endpoint", "Purpose", "Key filters"]}
              rows={content.endpointRows}
            />
          </RefSection>

          <RefSection id="ids" title={String(content.toc[3]?.label || "Canonical IDs")}>
            {content.sections.ids}
          </RefSection>

          <RefSection id="sample" title={String(content.toc[4]?.label || "Sample payload")}>
            {content.sections.sample}
            <RefTable headers={["Field", "Example", "Used for"]} rows={content.fieldRows} />
            <div className="my-6">
              <PropCode path={content.samplePath} sample={content.sample} />
            </div>
          </RefSection>

          <RefSection id="sources" title={String(content.toc[5]?.label || "Comparing sources")}>
            {content.sections.sources}
            <RefTable
              headers={["Source", "Schema", "Best use"]}
              rows={content.sourceRows}
            />
          </RefSection>

          <RefSection id="grading" title={String(content.toc[6]?.label || "Prop verification")}>
            {content.sections.grading}
          </RefSection>

          <RefSection id="ops" title={String(content.toc[7]?.label || "Operational practices")}>
            {content.sections.ops}
          </RefSection>

          <RefSection id="quick" title={String(content.toc[8]?.label || "Quick reference")}>
            {content.sections.quick}
          </RefSection>

          <section className="border-t border-white/10 pt-10 mt-8 mb-8">
            <p className="text-base text-zinc-400 leading-relaxed mb-6">
              If you need a normalized feed instead of another UI wrapper, KashRock exposes live boards,
              schedules, and history on one schema — with the IDs and outcome patterns that keep
              backtests and grading honest. Start free on{" "}
              <a href="/esports-api-free-tier" className="text-white underline">
                Sandbox
              </a>
              , or see{" "}
              <a href="/esports-api-pricing" className="text-white underline">
                published pricing
              </a>
              .
            </p>
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-zinc-500">
              {content.relatedLinks.map((link) => (
                <a key={link.href} href={link.href} className="hover:text-white transition-colors">
                  {link.label} →
                </a>
              ))}
            </div>
          </section>
        </div>
      </article>

      <FaqGrid faqs={content.faqs} />
    </MarketingShell>
  )
}

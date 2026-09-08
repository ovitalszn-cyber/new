import { DFS_FAQS, PLAN_OFFERS } from "./copy"

type Faq = { q: string; a: string }

export function softwareApplicationLd(opts: {
  name: string
  url: string
  description: string
}) {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: opts.name,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Any",
    url: opts.url,
    description: opts.description,
    offers: PLAN_OFFERS.map((plan) => ({
      "@type": "Offer",
      name: plan.name,
      price: plan.price,
      priceCurrency: "USD",
    })),
  }
}

export function faqPageLd(faqs: readonly Faq[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((faq) => ({
      "@type": "Question",
      name: faq.q,
      acceptedAnswer: { "@type": "Answer", text: faq.a },
    })),
  }
}

export function dfsJsonLd() {
  const url = "https://www.kashrock.com/dfs-esports-api"
  return [
    softwareApplicationLd({
      name: "KashRock DFS Esports API",
      url,
      description:
        "PrizePicks and Underdog player props for CS2 and LoL, plus Betr, Sleeper, Dabble, and ParlayPlay.",
    }),
    faqPageLd(DFS_FAQS),
  ]
}

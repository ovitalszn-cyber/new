import { DFS_FAQS, MCP_DESCRIPTION, MCP_FAQS, MCP_STEPS, PLAN_OFFERS } from "./copy"

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
        "PrizePicks and Underdog player props for CS2 and LoL, plus Betr, Sleeper, Dabble, ParlayPlay, Boom, and Pick6.",
    }),
    faqPageLd(DFS_FAQS),
  ]
}

export function mcpJsonLd() {
  const url = "https://www.kashrock.com/mcp"
  return [
    softwareApplicationLd({
      name: "KashRock MCP",
      url,
      description: MCP_DESCRIPTION,
    }),
    {
      "@context": "https://schema.org",
      "@type": "HowTo",
      name: "Set up KashRock in Cursor in 30 seconds",
      totalTime: "PT30S",
      url,
      step: MCP_STEPS.map((step) => ({
        "@type": "HowToStep",
        name: step.title,
        text: step.body,
        position: Number(step.n),
      })),
    },
    faqPageLd(MCP_FAQS),
  ]
}

export function appFaqGraphLd(name: string, faqs: readonly Faq[]) {
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "SoftwareApplication",
        name,
        applicationCategory: "DeveloperApplication",
        operatingSystem: "Web",
        offers: PLAN_OFFERS.map((plan) => ({
          "@type": "Offer",
          name: plan.name,
          price: plan.price,
          priceCurrency: "USD",
        })),
      },
      {
        "@type": "FAQPage",
        mainEntity: faqs.map((faq) => ({
          "@type": "Question",
          name: faq.q,
          acceptedAnswer: { "@type": "Answer", text: faq.a },
        })),
      },
    ],
  }
}

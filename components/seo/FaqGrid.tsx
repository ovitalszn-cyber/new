type Faq = { q: string; a: string }

export function FaqGrid({ faqs }: { faqs: readonly Faq[] }) {
  return (
    <section className="py-24 max-w-7xl mx-auto px-6">
      <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-8">
        Frequently asked questions
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {faqs.map((faq) => (
          <div key={faq.q} className="bg-[#0C0D0F] border border-white/10 rounded-sm p-8">
            <h3 className="text-lg font-medium text-white mb-2">{faq.q}</h3>
            <p className="text-base text-zinc-400 leading-relaxed">{faq.a}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

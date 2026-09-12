import type { ReactNode } from "react"

export function RefCallout({ children }: { children: ReactNode }) {
  return (
    <blockquote className="border-l-2 border-white/30 pl-4 my-6 text-zinc-300 text-base leading-relaxed">
      <span className="text-white font-medium">Practical rule: </span>
      {children}
    </blockquote>
  )
}

export function RefToc({
  items,
}: {
  items: { id: string; label: string; children?: { id: string; label: string }[] }[]
}) {
  return (
    <nav
      aria-label="Table of contents"
      className="bg-[#0C0D0F] border border-white/10 rounded-sm p-6 mb-12"
    >
      <p className="text-xs uppercase tracking-wider text-zinc-500 mb-4">Table of contents</p>
      <ol className="space-y-2 text-sm text-zinc-300">
        {items.map((item) => (
          <li key={item.id}>
            <a href={`#${item.id}`} className="hover:text-white transition-colors">
              {item.label}
            </a>
            {item.children?.length ? (
              <ol className="mt-2 ml-4 space-y-1 text-zinc-500">
                {item.children.map((child) => (
                  <li key={child.id}>
                    <a href={`#${child.id}`} className="hover:text-zinc-300 transition-colors">
                      {child.label}
                    </a>
                  </li>
                ))}
              </ol>
            ) : null}
          </li>
        ))}
      </ol>
    </nav>
  )
}

export function RefSection({
  id,
  title,
  children,
}: {
  id: string
  title: string
  children: ReactNode
}) {
  return (
    <section id={id} className="scroll-mt-28 mb-16">
      <h2 className="text-3xl md:text-4xl font-medium tracking-tight text-white mb-6">
        {title}
      </h2>
      <div className="space-y-4 text-base text-zinc-400 leading-relaxed">{children}</div>
    </section>
  )
}

export function RefSub({
  id,
  title,
  children,
}: {
  id: string
  title: string
  children: ReactNode
}) {
  return (
    <div id={id} className="scroll-mt-28 mt-8">
      <h3 className="text-xl font-medium tracking-tight text-white mb-3">{title}</h3>
      <div className="space-y-3 text-base text-zinc-400 leading-relaxed">{children}</div>
    </div>
  )
}

export function RefTable({
  headers,
  rows,
}: {
  headers: string[]
  rows: string[][]
}) {
  return (
    <div className="overflow-x-auto my-6 border border-white/10 rounded-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10 bg-white/[0.02]">
            {headers.map((h) => (
              <th
                key={h}
                className="text-left py-3 px-4 text-zinc-400 font-normal whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.join("|")} className="border-b border-white/5">
              {row.map((cell, i) => (
                <td
                  key={`${row[0]}-${i}`}
                  className={`py-3 px-4 ${i === 0 ? "text-zinc-200 font-medium" : "text-zinc-400"}`}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function RefBullets({ items }: { items: ReactNode[] }) {
  return (
    <ul className="space-y-3 my-4">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3 text-zinc-400">
          <span className="text-white shrink-0">—</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}

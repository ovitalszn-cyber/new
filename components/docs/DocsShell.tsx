import Link from 'next/link'
import type { ReactNode } from 'react'
import { DOC_NAV } from '@/lib/docs'

export function DocsShell({
  active,
  children,
}: {
  active: string
  children: ReactNode
}) {
  return (
    <div className="min-h-screen bg-[#08090A] text-[#E3E5E7] font-sans selection:bg-white/20">
      <header className="h-16 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md sticky top-0 z-50 flex items-center px-6 justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5">
            <img src="/kashrock-logo.svg" alt="KashRock" className="h-5 w-auto" />
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="/docs" className="text-sm font-medium text-white">Docs</Link>
            <Link href="/console" className="text-sm font-medium text-zinc-400 hover:text-white">Console</Link>
          </nav>
        </div>
        <Link href="/console" className="text-xs bg-white text-black px-3 py-1.5 rounded-sm font-medium hover:bg-zinc-200">
          Get a key
        </Link>
      </header>
      <div className="max-w-7xl mx-auto flex">
        <aside className="w-64 hidden lg:block border-r border-white/5 h-[calc(100vh-64px)] sticky top-16 p-6 overflow-y-auto">
          <div className="space-y-8">
            {DOC_NAV.map((section) => (
              <section key={section.title}>
                <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">
                  {section.title}
                </h3>
                <ul className="space-y-3">
                  {section.items.map((item) => (
                    <li key={item.id}>
                      <Link
                        href={item.href}
                        className={`text-sm transition-colors ${
                          active === item.id
                            ? 'text-white'
                            : 'text-zinc-400 hover:text-white'
                        }`}
                      >
                        {item.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </aside>
        <main className="flex-1 px-6 lg:px-12 py-12 max-w-4xl min-w-0">{children}</main>
      </div>
    </div>
  )
}

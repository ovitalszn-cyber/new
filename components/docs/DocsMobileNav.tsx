'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

import { DOC_NAV } from '@/lib/docs'

export function DocsMobileNav({ active }: { active: string }) {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prev
    }
  }, [open])

  const current =
    DOC_NAV.flatMap((s) => s.items).find((item) => item.id === active)?.label ??
    'Docs'

  return (
    <div className="lg:hidden border-b border-white/5 bg-[#08090A] sticky top-16 z-40">
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="w-full px-6 py-3 flex items-center justify-between gap-3 text-left"
        aria-expanded={open}
        aria-controls="docs-mobile-nav"
      >
        <span className="text-sm text-zinc-400">
          Browse docs
          <span className="text-white font-medium ml-2">{current}</span>
        </span>
        <span className="text-zinc-500 text-xs uppercase tracking-wider">Menu</span>
      </button>

      {open ? (
        <div className="fixed inset-0 z-50" id="docs-mobile-nav" role="dialog" aria-modal="true">
          <button
            type="button"
            className="absolute inset-0 bg-black/70"
            aria-label="Close docs menu"
            onClick={() => setOpen(false)}
          />
          <div className="absolute inset-y-0 left-0 w-[min(100%,20rem)] bg-[#0C0D0F] border-r border-white/10 shadow-xl flex flex-col">
            <div className="h-16 px-5 flex items-center justify-between border-b border-white/5">
              <span className="text-sm font-medium text-white">Documentation</span>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="text-sm text-zinc-400 hover:text-white"
              >
                Close
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto p-5 space-y-8">
              {DOC_NAV.map((section) => (
                <section key={section.title}>
                  <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-3">
                    {section.title}
                  </h3>
                  <ul className="space-y-1">
                    {section.items.map((item) => (
                      <li key={item.id}>
                        <Link
                          href={item.href}
                          onClick={() => setOpen(false)}
                          className={`block rounded-sm px-3 py-2.5 text-sm ${
                            active === item.id
                              ? 'bg-white/10 text-white'
                              : 'text-zinc-400 hover:text-white hover:bg-white/5'
                          }`}
                        >
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </section>
              ))}
            </nav>
          </div>
        </div>
      ) : null}
    </div>
  )
}

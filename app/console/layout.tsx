'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { useSession } from '@/components/auth/SessionProvider';

type LucideApi = {
  createIcons: (options: { attrs: Record<string, string> }) => void;
};

function getLucide(): LucideApi | undefined {
  return (window as Window & { lucide?: LucideApi }).lucide;
}

function refreshLucideIcons() {
  getLucide()?.createIcons({ attrs: { 'stroke-width': '1.5' } });
}

function loadLucideScript(): Promise<void> {
  if (getLucide()) return Promise.resolve();
  const existing = document.querySelector<HTMLScriptElement>(
    'script[data-kashrock-lucide]',
  );
  if (existing) {
    return new Promise((resolve, reject) => {
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => reject(), { once: true });
      if (getLucide()) resolve();
    });
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/lucide@0.469.0';
    script.async = true;
    script.dataset.kashrockLucide = '1';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Lucide'));
    document.body.appendChild(script);
  });
}

export default function ConsoleLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { status, user, logout } = useSession();
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);

  const displayName = user?.full_name || user?.email?.split('@')[0] || 'User';
  const userInitials = displayName
    ? displayName.split(' ').map((name) => name[0]).join('').toUpperCase().slice(0, 2)
    : 'U';
  const userName = displayName;
  const userEmail = user?.email || '';

  useEffect(() => {
    let cancelled = false;
    void loadLucideScript()
      .then(() => {
        if (!cancelled) refreshLucideIcons();
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [pathname]);

  const isActive = (path: string) => pathname === path;

  const navLinkClass = (path: string) =>
    isActive(path)
      ? 'flex items-center gap-3 px-3 py-2 bg-white/5 text-white text-sm font-medium rounded-sm border border-white/5 transition-all'
      : 'flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02] text-sm font-medium rounded-sm transition-all group';

  const iconClass = (path: string) =>
    isActive(path)
      ? 'w-4 h-4 text-white'
      : 'w-4 h-4 text-zinc-500 group-hover:text-zinc-300 transition-colors';

  if (status === 'loading') {
    return <div className="min-h-screen bg-[#08090A]" />;
  }

  return (
    <div
      className="antialiased selection:bg-white/20 selection:text-white h-screen flex overflow-hidden"
      style={{
        fontFamily: 'var(--font-dm-sans), sans-serif',
        backgroundColor: '#08090A',
        color: '#E3E5E7',
      }}
    >
      <style jsx global>{`
        body { font-family: var(--font-dm-sans), sans-serif; background-color: #08090A; color: #E3E5E7; }
        .font-mono { font-family: ui-monospace, monospace; }
        .grid-bg { background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 20px 20px; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
        .chart-bar { transition: height 0.5s ease-out, background-color 0.2s; }
        .chart-bar:hover { background-color: #E3E5E7; }
      `}</style>

      <aside className="w-64 border-r border-white/5 bg-[#050505] flex flex-col justify-between shrink-0 transition-all duration-300">
        <div>
          <div className="h-16 flex items-center px-6 border-b border-white/5">
            <Link href="/" className="flex items-center gap-2.5">
              <Image src="/kashrock-logo.svg" alt="KashRock" width={120} height={24} className="h-6 w-auto" />
              <span className="text-[10px] bg-white/10 text-zinc-400 px-1.5 py-0.5 rounded-sm border border-white/5">v6.0</span>
            </Link>
          </div>

          <div className="p-3 space-y-1">
            <Link href="/console" className={navLinkClass('/console')}>
              <i data-lucide="layout-grid" className={iconClass('/console')}></i>
              Overview
            </Link>
            <Link href="/docs" className="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02] text-sm font-medium rounded-sm transition-all group">
              <i data-lucide="book" className="w-4 h-4 text-zinc-500 group-hover:text-zinc-300 transition-colors"></i>
              Documentation
            </Link>
            <div className="h-px bg-white/5 my-2 mx-3"></div>
            <Link href="/legal" className="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02] text-sm font-medium rounded-sm transition-all group">
              <i data-lucide="shield" className="w-4 h-4 text-zinc-500 group-hover:text-zinc-300 transition-colors"></i>
              Legal
            </Link>
          </div>
        </div>

        <div className="border-t border-white/5 p-3 relative">
          <button
            onClick={() => setProfileMenuOpen(!profileMenuOpen)}
            className="flex items-center gap-3 w-full p-2 hover:bg-white/[0.03] rounded-sm transition-colors text-left group"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-zinc-700 to-zinc-600 border border-white/10 flex items-center justify-center">
              <span className="text-xs font-medium text-white">{userInitials}</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">{userName}</div>
              <div className="text-xs text-zinc-500 truncate group-hover:text-zinc-400">{user?.tier || 'Plan unavailable'}</div>
            </div>
            <i data-lucide="chevrons-up-down" className="w-4 h-4 text-zinc-600"></i>
          </button>

          {profileMenuOpen && (
            <div className="absolute bottom-full left-3 right-3 mb-2 bg-[#0C0D0F] border border-white/10 rounded-md shadow-xl overflow-hidden">
              <div className="px-3 py-2 border-b border-white/5">
                <div className="text-xs text-zinc-500 truncate">{userEmail}</div>
              </div>
              <Link
                href="/settings"
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                <i data-lucide="settings" className="w-4 h-4"></i>
                Settings
              </Link>
              <button
                onClick={() => void logout()}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                <i data-lucide="log-out" className="w-4 h-4"></i>
                Sign out
              </button>
            </div>
          )}
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#08090A]">
        {children}
      </main>
    </div>
  );
}

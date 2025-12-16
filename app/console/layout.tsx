'use client';

import Script from 'next/script';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { User } from '@supabase/supabase-js';
import { usePathname } from 'next/navigation';

export default function ConsoleLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const { supabase } = await import('@/lib/supabase');
      if (!supabase) {
        setLoading(false);
        return;
      }
      
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        setUser(session.user);
      } else {
        router.push('/login');
      }
      setLoading(false);

      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        setUser(session?.user ?? null);
        if (!session?.user) {
          router.push('/login');
        }
      });

      return () => subscription.unsubscribe();
    };
    initAuth();
  }, [router]);

  const userInitials = user?.user_metadata?.full_name
    ? user.user_metadata.full_name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U';
  const userName = user?.user_metadata?.full_name || 'User';
  const userEmail = user?.email || '';
  const userImage = user?.user_metadata?.avatar_url;

  const handleSignOut = async () => {
    const { supabase } = await import('@/lib/supabase');
    if (supabase) {
      await supabase.auth.signOut();
    }
    router.push('/');
  };

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
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

  return (
    <>
      <Script src="https://unpkg.com/lucide@latest" strategy="beforeInteractive" />
      
      <div className="antialiased selection:bg-white/20 selection:text-white h-screen flex overflow-hidden" style={{ 
        fontFamily: 'Inter, sans-serif',
        backgroundColor: '#08090A',
        color: '#E3E5E7'
      }}>
        <style jsx global>{`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
          
          body { font-family: 'Inter', sans-serif; background-color: #08090A; color: #E3E5E7; }
          .font-mono { font-family: 'JetBrains Mono', monospace; }
          
          .grid-bg { background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 20px 20px; }
          
          ::-webkit-scrollbar { width: 6px; height: 6px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
          ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

          .chart-bar { transition: height 0.5s ease-out, background-color 0.2s; }
          .chart-bar:hover { background-color: #E3E5E7; }
        `}</style>

        {/* Sidebar */}
        <aside className="w-64 border-r border-white/5 bg-[#050505] flex flex-col justify-between shrink-0 transition-all duration-300">
          <div>
            {/* Logo Area */}
            <div className="h-16 flex items-center px-6 border-b border-white/5">
              <Link href="/" className="flex items-center gap-2.5">
                <img src="/kashrock-logo.svg" alt="KashRock" className="h-6 w-auto" />
                <span className="text-[10px] bg-white/10 text-zinc-400 px-1.5 py-0.5 rounded-sm border border-white/5">v6.0</span>
              </Link>
            </div>

            {/* Navigation */}
            <div className="p-3 space-y-1">
              <div className="px-3 py-2 text-xs font-medium text-zinc-500 uppercase tracking-wider">Platform</div>
              
              <Link href="/console" className={navLinkClass('/console')}>
                <i data-lucide="layout-grid" className={iconClass('/console')}></i>
                Overview
              </Link>
              <Link href="/console/keys" className={navLinkClass('/console/keys')}>
                <i data-lucide="key" className={iconClass('/console/keys')}></i>
                API Keys
              </Link>
              <Link href="/console/usage" className={navLinkClass('/console/usage')}>
                <i data-lucide="bar-chart-2" className={iconClass('/console/usage')}></i>
                Usage &amp; Limits
              </Link>
              <Link href="/console/logs" className={navLinkClass('/console/logs')}>
                <i data-lucide="file-json" className={iconClass('/console/logs')}></i>
                Logs
              </Link>

              <div className="h-px bg-white/5 my-2 mx-3"></div>
              
              <div className="px-3 py-2 text-xs font-medium text-zinc-500 uppercase tracking-wider">Settings</div>
              <Link href="/console/billing" className={navLinkClass('/console/billing')}>
                <i data-lucide="credit-card" className={iconClass('/console/billing')}></i>
                Billing
              </Link>
              <Link href="/console/team" className={navLinkClass('/console/team')}>
                <i data-lucide="users" className={iconClass('/console/team')}></i>
                Team
              </Link>
              <a href="https://api.kashrock.com/docs" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02] text-sm font-medium rounded-sm transition-all group">
                <i data-lucide="book" className="w-4 h-4 text-zinc-500 group-hover:text-zinc-300 transition-colors"></i>
                Documentation <i data-lucide="external-link" className="w-3 h-3 ml-auto opacity-50"></i>
              </a>
              
              <div className="h-px bg-white/5 my-2 mx-3"></div>
              
              <Link href="/legal" className="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02] text-sm font-medium rounded-sm transition-all group">
                <i data-lucide="shield" className="w-4 h-4 text-zinc-500 group-hover:text-zinc-300 transition-colors"></i>
                Legal
              </Link>
            </div>
          </div>

          {/* User Profile */}
          <div className="border-t border-white/5 p-3 relative">
            <button 
              onClick={() => setProfileMenuOpen(!profileMenuOpen)}
              className="flex items-center gap-3 w-full p-2 hover:bg-white/[0.03] rounded-sm transition-colors text-left group"
            >
              {userImage ? (
                <img src={userImage} alt="" className="w-8 h-8 rounded-full border border-white/10" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-zinc-700 to-zinc-600 border border-white/10 flex items-center justify-center">
                  <span className="text-xs font-medium text-white">{userInitials}</span>
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-white truncate">{userName}</div>
                <div className="text-xs text-zinc-500 truncate group-hover:text-zinc-400">Starter Plan</div>
              </div>
              <i data-lucide="chevrons-up-down" className="w-4 h-4 text-zinc-600"></i>
            </button>
            
            {/* Profile Dropdown Menu */}
            {profileMenuOpen && (
              <div className="absolute bottom-full left-3 right-3 mb-2 bg-[#0C0D0F] border border-white/10 rounded-md shadow-xl overflow-hidden">
                <div className="px-3 py-2 border-b border-white/5">
                  <div className="text-xs text-zinc-500 truncate">{userEmail}</div>
                </div>
                <button
                  onClick={handleSignOut}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                >
                  <i data-lucide="log-out" className="w-4 h-4"></i>
                  Sign out
                </button>
              </div>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#08090A]">
          {children}
        </main>
      </div>
    </>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const handleAuthCallback = async () => {
      // Dynamic import to avoid build-time issues
      const { supabase } = await import('@/lib/supabase');
      
      // First, try to exchange the code for a session
      const { data, error } = await supabase.auth.getSession();
      
      // If no session, check if we have auth code in URL to exchange
      if (!data.session && !error) {
        const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(window.location.href);
        if (exchangeError) {
          console.error('Code exchange error:', exchangeError);
          router.push('/login?error=code_exchange_failed');
          return;
        }
      }
      
      // Now get the session after exchange
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError) {
        console.error('Auth callback error:', sessionError);
        router.push('/login?error=auth_failed');
        return;
      }

      if (session) {
        console.log('Auth successful, session:', session.user.email);
        router.push('/console');
      } else {
        console.log('No session found, redirecting to login');
        router.push('/login');
      }
    };

    handleAuthCallback();
  }, [router, mounted]);

  return (
    <div className="min-h-screen bg-[#08090A] flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-zinc-400 text-sm">Completing sign in...</p>
      </div>
    </div>
  );
}

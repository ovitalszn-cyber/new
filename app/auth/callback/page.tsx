'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { saveSessionTokens, clearSessionTokens } from '@/lib/auth-storage';

export default function AuthCallbackPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const handleAuthCallback = async () => {
      const { supabase } = await import('@/lib/supabase');

      const hashParams = new URLSearchParams(window.location.hash.replace('#', ''));
      const accessToken = hashParams.get('access_token');
      const refreshToken = hashParams.get('refresh_token');
      const queryParams = new URLSearchParams(window.location.search);
      const code = queryParams.get('code');
      const errorDescription = queryParams.get('error_description');

      if (errorDescription) {
        clearSessionTokens();
        router.push(`/login?error=${encodeURIComponent(errorDescription)}`);
        return;
      }

      try {
        console.log('[Auth Callback] Hash params:', { accessToken: !!accessToken, refreshToken: !!refreshToken });
        console.log('[Auth Callback] Query params:', { code: !!code });
        
        if (accessToken && refreshToken) {
          console.log('[Auth Callback] Setting session with tokens from hash...');
          const { data, error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          });
          if (error) {
            console.error('[Auth Callback] setSession error:', error);
            clearSessionTokens();
            router.push('/login?error=session_failed');
            return;
          }
          window.history.replaceState({}, document.title, window.location.pathname);
          if (data.session) {
            console.log('[Auth Callback] Session set successfully:', data.session.user.email);
            console.log('[Auth Callback] Access token preview:', data.session.access_token.substring(0, 50));
            saveSessionTokens(data.session);
            
            // Verify it was saved
            const { data: { session: verifySession } } = await supabase.auth.getSession();
            console.log('[Auth Callback] Verification - session exists:', !!verifySession);
            
            router.push('/console');
            return;
          }
        }

        if (code) {
          const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(window.location.href);
          if (exchangeError) {
            console.error('Code exchange error:', exchangeError);
            clearSessionTokens();
            router.push('/login?error=code_exchange_failed');
            return;
          }

          if (data.session) {
            console.log('Auth successful (pkce), session:', data.session.user.email);
            saveSessionTokens(data.session);
            const cleanUrl = window.location.pathname;
            window.history.replaceState({}, document.title, cleanUrl);
            router.push('/console');
            return;
          }
        }

        // Final attempt to read any session Supabase may have stored
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        if (sessionError) {
          console.error('Auth callback error:', sessionError);
          clearSessionTokens();
          router.push('/login?error=auth_failed');
          return;
        }

        if (session) {
          console.log('Auth successful (fallback), session:', session.user.email);
          saveSessionTokens(session);
          router.push('/console');
        } else {
          console.warn('No session found after callback');
          clearSessionTokens();
          router.push('/login?error=session_missing');
        }
      } catch (err) {
        console.error('Unexpected auth callback error:', err);
        clearSessionTokens();
        router.push('/login?error=unexpected');
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

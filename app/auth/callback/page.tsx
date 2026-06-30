'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { exchangeGoogleIdToken, api } from '@/lib/api-client';

export default function AuthCallbackPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const handleAuthCallback = async () => {
      const hashParams = new URLSearchParams(window.location.hash.replace('#', ''));
      const idToken = hashParams.get('id_token') || hashParams.get('access_token');
      const queryParams = new URLSearchParams(window.location.search);
      const errorDescription = queryParams.get('error_description');

      if (errorDescription) {
        router.push(`/login?error=${encodeURIComponent(errorDescription)}`);
        return;
      }

      try {
        if (!idToken) {
          router.push('/login?error=no_token');
          return;
        }

        const session = await exchangeGoogleIdToken(idToken);
        window.history.replaceState({}, document.title, window.location.pathname);

        const redirect = sessionStorage.getItem('auth_redirect');
        const plan = sessionStorage.getItem('auth_plan');
        sessionStorage.removeItem('auth_redirect');
        sessionStorage.removeItem('auth_plan');

        if (redirect === 'checkout' && plan) {
          const checkout = await api.createCheckoutSession(plan);
          window.location.href = checkout.url;
          return;
        }

        if (session.initial_api_key) {
          sessionStorage.setItem('initial_api_key', session.initial_api_key);
        }

        router.push('/console');
      } catch (err) {
        console.error('Unexpected auth callback error:', err);
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

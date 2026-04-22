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
      const hashParams = new URLSearchParams(window.location.hash.replace('#', ''));
      const accessToken = hashParams.get('access_token');
      const queryParams = new URLSearchParams(window.location.search);
      const errorDescription = queryParams.get('error_description');

      if (errorDescription) {
        router.push(`/login?error=${encodeURIComponent(errorDescription)}`);
        return;
      }

      try {
        if (accessToken) {
          // Store the Google ID token in localStorage
          localStorage.setItem('google_id_token', accessToken);
          
          // Redirect to console
          window.history.replaceState({}, document.title, window.location.pathname);
          router.push('/console');
          return;
        }

        // No token found
        console.warn('No access token found in callback');
        router.push('/login?error=no_token');
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

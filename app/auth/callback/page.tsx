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
      const { data: { session }, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error('Auth callback error:', error);
        router.push('/login?error=auth_failed');
        return;
      }

      if (session) {
        router.push('/console');
      } else {
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

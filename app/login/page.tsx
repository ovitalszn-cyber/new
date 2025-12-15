'use client';

import Link from 'next/link';
import { supabase } from '@/lib/supabase';

export default function LoginPage() {
  const handleGoogleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    });
    
    if (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ 
      fontFamily: 'Inter, sans-serif',
      backgroundColor: '#08090A',
      color: '#E3E5E7'
    }}>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #08090A; color: #E3E5E7; }
      `}</style>

      <div className="w-full max-w-md px-6">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <img src="/kashrock-logo.svg" alt="KashRock" className="h-10 w-auto mx-auto" />
          </Link>
        </div>

        {/* Login Card */}
        <div className="bg-[#0C0D0F] border border-white/5 rounded-lg p-8">
          <h1 className="text-2xl font-semibold text-white text-center mb-2">Welcome back</h1>
          <p className="text-sm text-zinc-500 text-center mb-8">Sign in to access your dashboard</p>

          {/* Google Sign In Button */}
          <button
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 bg-white text-black px-4 py-3 rounded-sm font-medium hover:bg-zinc-200 transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
              <path fill="none" d="M1 1h22v22H1z" />
            </svg>
            Continue with Google
          </button>
        </div>

        {/* Footer Links */}
        <div className="mt-6 text-center text-xs text-zinc-600">
          <p>
            By signing in, you agree to our{' '}
            <Link href="/legal?tab=terms" className="text-zinc-400 hover:text-white transition-colors">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/legal" className="text-zinc-400 hover:text-white transition-colors">
              Privacy Policy
            </Link>
          </p>
        </div>

        <div className="mt-8 text-center">
          <Link href="/" className="text-sm text-zinc-500 hover:text-white transition-colors">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}

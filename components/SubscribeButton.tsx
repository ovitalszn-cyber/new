'use client';

import { useState } from 'react';
import { loadSessionTokens } from '@/lib/auth-storage';
import { api } from '@/lib/api-client';

type PlanId = 'sandbox' | 'hobby' | 'builder' | 'pro';

interface SubscribeButtonProps {
  plan: PlanId;
  label: string;
  className?: string;
}

export default function SubscribeButton({ plan, label, className }: SubscribeButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (plan === 'sandbox') {
      const session = loadSessionTokens();
      if (!session?.accessToken) {
        sessionStorage.setItem('auth_redirect', 'console');
        window.location.href = '/login';
        return;
      }
      window.location.href = '/console';
      return;
    }

    const session = loadSessionTokens();
    if (!session?.accessToken) {
      sessionStorage.setItem('auth_redirect', 'checkout');
      sessionStorage.setItem('auth_plan', plan);
      window.location.href = '/login';
      return;
    }

    try {
      setLoading(true);
      const checkout = await api.createCheckoutSession(plan);
      window.location.href = checkout.url;
    } catch (err) {
      console.error('Checkout failed:', err);
      alert(err instanceof Error ? err.message : 'Failed to start checkout');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={loading}
      className={className}
    >
      {loading ? 'Redirecting...' : label}
    </button>
  );
}

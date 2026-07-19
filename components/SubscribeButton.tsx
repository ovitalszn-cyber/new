'use client';

import { useState } from 'react';

import { useSession } from '@/components/auth/SessionProvider';

type PlanId = 'sandbox' | 'hobby' | 'builder' | 'pro';

interface SubscribeButtonProps {
  plan: PlanId;
  label: string;
  className?: string;
}

export default function SubscribeButton({ plan, label, className }: SubscribeButtonProps) {
  const [loading, setLoading] = useState(false);
  const { status } = useSession();

  const handleClick = async () => {
    setLoading(true);
    const checkoutPath = `/checkout/start?plan=${encodeURIComponent(plan)}`;
    if (status !== 'authenticated') {
      window.location.assign(
        `/login?returnTo=${encodeURIComponent(checkoutPath)}`,
      );
      return;
    }
    window.location.assign(checkoutPath);
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

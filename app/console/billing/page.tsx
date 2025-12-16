import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import BillingClient from './BillingClient';
import { getBillingInfoServer, getBillingHistoryServer } from '@/lib/server-api';

interface BillingData {
  plan: string;
  monthly_limit: number;
  current_usage: number;
  billing_cycle_end: string;
  payment_method?: { last4: string; brand: string; exp_month: number; exp_year: number };
}

interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: string;
  pdf_url: string;
}

export default async function BillingPage() {
  // Get user info server-side
  const cookieStore = await cookies();
  let userName = 'User';
  
  try {
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll();
          },
        },
      }
    );
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.user?.user_metadata?.full_name) {
      userName = session.user.user_metadata.full_name;
    }
  } catch (e) {
    console.error('[BillingPage] Failed to get user:', e);
  }

  // Fetch billing data server-side
  let billing: BillingData | null = null;
  let invoices: Invoice[] = [];
  let error: string | null = null;
  
  try {
    const [billingData, historyData] = await Promise.all([
      getBillingInfoServer(),
      getBillingHistoryServer()
    ]);
    billing = billingData;
    invoices = historyData.invoices;
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load billing data';
    console.error('[BillingPage] Failed to fetch billing:', e);
  }

  return (
    <BillingClient 
      billing={billing}
      invoices={invoices}
      error={error}
      userName={userName}
    />
  );
}

import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import UsageClient from './UsageClient';
import { getUsageSummaryServer } from '@/lib/server-api';

export default async function UsagePage() {
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
    console.error('[UsagePage] Failed to get user:', e);
  }

  // Fetch initial data server-side
  let initialData = null;
  let initialError = null;
  
  try {
    initialData = await getUsageSummaryServer('7d');
  } catch (e) {
    initialError = e instanceof Error ? e.message : 'Failed to load usage data';
    console.error('[UsagePage] Failed to fetch usage:', e);
  }

  return (
    <UsageClient 
      initialData={initialData} 
      initialError={initialError} 
      userName={userName} 
    />
  );
}

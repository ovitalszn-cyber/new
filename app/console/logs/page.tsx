import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import LogsClient from './LogsClient';
import { getRequestLogsServer } from '@/lib/server-api';

export default async function LogsPage() {
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
    console.error('[LogsPage] Failed to get user:', e);
  }

  // Fetch initial data server-side
  let initialLogs: Array<{ id: string; method: string; endpoint: string; status_code: number; latency_ms: number; timestamp: string }> = [];
  let initialTotal = 0;
  let initialError = null;
  
  try {
    const data = await getRequestLogsServer({ limit: 20, offset: 0 });
    initialLogs = data.logs;
    initialTotal = data.total;
  } catch (e) {
    initialError = e instanceof Error ? e.message : 'Failed to load logs';
    console.error('[LogsPage] Failed to fetch logs:', e);
  }

  return (
    <LogsClient 
      initialLogs={initialLogs}
      initialTotal={initialTotal}
      initialError={initialError}
      userName={userName} 
    />
  );
}

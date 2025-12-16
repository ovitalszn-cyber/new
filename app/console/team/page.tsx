import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';
import TeamClient from './TeamClient';
import { getTeamMembersServer } from '@/lib/server-api';

interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: string;
  avatar_url?: string;
  joined_at: string;
}

export default async function TeamPage() {
  // Get user info server-side
  const cookieStore = await cookies();
  let userName = 'User';
  let userEmail = '';
  let userImage: string | undefined = undefined;
  
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
    if (session?.user) {
      userName = session.user.user_metadata?.full_name || 'User';
      userEmail = session.user.email || '';
      userImage = session.user.user_metadata?.avatar_url;
    }
  } catch (e) {
    console.error('[TeamPage] Failed to get user:', e);
  }

  // Fetch team members server-side
  let members: TeamMember[] = [];
  let error: string | null = null;
  
  try {
    const data = await getTeamMembersServer();
    members = data.members;
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load team';
    console.error('[TeamPage] Failed to fetch team:', e);
  }

  return (
    <TeamClient 
      members={members}
      error={error}
      userName={userName}
      userEmail={userEmail}
      userImage={userImage}
    />
  );
}

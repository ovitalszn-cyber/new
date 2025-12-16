'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getTeamMembers } from '@/lib/api';

interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: string;
  avatar_url?: string;
  joined_at: string;
}

export default function TeamPage() {
  const [userName, setUserName] = useState('User');
  const [userEmail, setUserEmail] = useState('');
  const [userImage, setUserImage] = useState<string | undefined>(undefined);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const getUser = async () => {
      const { supabase } = await import('@/lib/supabase');
      if (!supabase) return;
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        setUserName(session.user.user_metadata?.full_name || 'User');
        setUserEmail(session.user.email || '');
        setUserImage(session.user.user_metadata?.avatar_url);
      }
    };
    getUser();
  }, []);

  useEffect(() => {
    fetchTeam();
  }, []);

  const fetchTeam = async () => {
    try {
      setLoading(true);
      const data = await getTeamMembers();
      setMembers(data.members);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load team');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, [members, loading]);

  return (
    <>
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <nav className="flex items-center text-sm font-medium text-zinc-500">
            <span className="hover:text-zinc-300 transition-colors cursor-pointer">{userName}</span>
            <span className="mx-2 text-zinc-700">/</span>
            <span className="text-white">Team</span>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-zinc-400 hover:text-white transition-colors">
            <i data-lucide="help-circle" className="w-5 h-5"></i>
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          
          {/* Page Header */}
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Team</h1>
              <p className="text-sm text-zinc-500">Manage team members and their access to your API keys.</p>
            </div>
            <button className="px-4 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors flex items-center gap-2">
              <i data-lucide="user-plus" className="w-4 h-4"></i>
              Invite Member
            </button>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-sm p-4 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Team Members */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-sm font-medium text-white">Team Members</h3>
            </div>
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
              </div>
            ) : (
            <div className="divide-y divide-white/5">
              {/* Owner (Current User) */}
              <div className="p-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {userImage ? (
                    <img src={userImage} alt="" className="w-10 h-10 rounded-full border border-white/10" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-zinc-700 to-zinc-600 border border-white/10 flex items-center justify-center">
                      <span className="text-sm font-medium text-white">
                        {userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                      </span>
                    </div>
                  )}
                  <div>
                    <div className="text-sm font-medium text-white flex items-center gap-2">
                      {userName}
                      <span className="px-2 py-0.5 bg-white/10 border border-white/5 rounded text-[10px] text-zinc-400">You</span>
                    </div>
                    <div className="text-xs text-zinc-500">{userEmail}</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-xs font-medium text-purple-400">Owner</span>
                </div>
              </div>
              
              {/* Other Team Members from API */}
              {members.map((member) => (
                <div key={member.id} className="p-6 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {member.avatar_url ? (
                      <img src={member.avatar_url} alt="" className="w-10 h-10 rounded-full border border-white/10" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-zinc-700 to-zinc-600 border border-white/10 flex items-center justify-center">
                        <span className="text-sm font-medium text-white">
                          {member.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                        </span>
                      </div>
                    )}
                    <div>
                      <div className="text-sm font-medium text-white">{member.name}</div>
                      <div className="text-xs text-zinc-500">{member.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      member.role === 'admin' 
                        ? 'bg-blue-500/10 border border-blue-500/20 text-blue-400'
                        : 'bg-zinc-500/10 border border-zinc-500/20 text-zinc-400'
                    }`}>
                      {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            )}
          </div>

          {/* Pending Invites */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-sm font-medium text-white">Pending Invitations</h3>
            </div>
            
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/5 border border-white/5 mb-4">
                <i data-lucide="mail" className="w-6 h-6 text-zinc-500"></i>
              </div>
              <p className="text-sm text-zinc-400 mb-1">No pending invitations</p>
              <p className="text-xs text-zinc-600">Invite team members to collaborate on your API project</p>
            </div>
          </div>

          {/* Roles & Permissions */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
            <h3 className="text-sm font-medium text-white mb-4">Roles & Permissions</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 bg-black/30 border border-white/5 rounded-sm">
                <div className="p-2 bg-purple-500/10 rounded border border-purple-500/20">
                  <i data-lucide="crown" className="w-4 h-4 text-purple-400"></i>
                </div>
                <div>
                  <div className="text-sm font-medium text-white">Owner</div>
                  <p className="text-xs text-zinc-500 mt-1">Full access to all features including billing, team management, and API keys.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-black/30 border border-white/5 rounded-sm">
                <div className="p-2 bg-blue-500/10 rounded border border-blue-500/20">
                  <i data-lucide="shield" className="w-4 h-4 text-blue-400"></i>
                </div>
                <div>
                  <div className="text-sm font-medium text-white">Admin</div>
                  <p className="text-xs text-zinc-500 mt-1">Can manage API keys and view usage. Cannot access billing or invite members.</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-black/30 border border-white/5 rounded-sm">
                <div className="p-2 bg-zinc-500/10 rounded border border-zinc-500/20">
                  <i data-lucide="eye" className="w-4 h-4 text-zinc-400"></i>
                </div>
                <div>
                  <div className="text-sm font-medium text-white">Viewer</div>
                  <p className="text-xs text-zinc-500 mt-1">Read-only access to usage stats and logs. Cannot manage keys or settings.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link>
          </div>

        </div>
      </div>
    </>
  );
}

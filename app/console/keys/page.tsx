'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { listApiKeys, createApiKey, revokeApiKey } from '@/lib/api';

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
}

export default function APIKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());
  const [copied, setCopied] = useState<string | null>(null);
  const [userName, setUserName] = useState('User');
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);

  useEffect(() => {
    const getUser = async () => {
      const { supabase } = await import('@/lib/supabase');
      if (!supabase) return;
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user?.user_metadata?.full_name) {
        setUserName(session.user.user_metadata.full_name);
      }
    };
    getUser();
  }, []);

  useEffect(() => {
    fetchKeys();
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, [keys, showCreateModal, newlyCreatedKey]);

  const fetchKeys = async () => {
    try {
      setLoading(true);
      const data = await listApiKeys();
      setKeys(data.keys);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return;
    try {
      setCreating(true);
      const result = await createApiKey(newKeyName);
      setNewlyCreatedKey(result.key);
      setNewKeyName('');
      setShowCreateModal(false);
      await fetchKeys();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create key');
    } finally {
      setCreating(false);
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this key? This action cannot be undone.')) return;
    try {
      await revokeApiKey(keyId);
      await fetchKeys();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke key');
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <>
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <nav className="flex items-center text-sm font-medium text-zinc-500">
            <span className="hover:text-zinc-300 transition-colors cursor-pointer">{userName}</span>
            <span className="mx-2 text-zinc-700">/</span>
            <span className="text-white">API Keys</span>
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
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">API Keys</h1>
              <p className="text-sm text-zinc-500">Manage your API keys for authentication. Keep your keys secure and never share them publicly.</p>
            </div>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors flex items-center gap-2"
            >
              <i data-lucide="plus" className="w-4 h-4"></i>
              Create Key
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-sm p-4 text-sm text-red-400">
              {error}
              <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-white">×</button>
            </div>
          )}

          {/* Newly Created Key Alert */}
          {newlyCreatedKey && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-sm p-4">
              <div className="flex items-center gap-2 mb-2">
                <i data-lucide="check-circle" className="w-4 h-4 text-emerald-400"></i>
                <span className="text-sm font-medium text-emerald-400">API Key Created Successfully</span>
              </div>
              <p className="text-xs text-zinc-400 mb-3">Copy your key now. You won&apos;t be able to see it again.</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-black/50 border border-white/5 rounded-sm px-3 py-2 font-mono text-sm text-white">
                  {newlyCreatedKey}
                </code>
                <button 
                  onClick={() => handleCopy(newlyCreatedKey, 'new')}
                  className="p-2 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-white/5"
                >
                  {copied === 'new' ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
                </button>
              </div>
              <button 
                onClick={() => setNewlyCreatedKey(null)}
                className="mt-3 text-xs text-zinc-500 hover:text-white transition-colors"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-12 text-center">
              <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-sm text-zinc-500">Loading API keys...</p>
            </div>
          )}

          {/* No Keys State */}
          {!loading && keys.length === 0 && (
            <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-12 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/5 border border-white/5 mb-4">
                <i data-lucide="key" className="w-6 h-6 text-zinc-500"></i>
              </div>
              <p className="text-sm text-zinc-400 mb-1">No API keys yet</p>
              <p className="text-xs text-zinc-600 mb-4">Create your first API key to start making requests</p>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors"
              >
                Create Your First Key
              </button>
            </div>
          )}

          {/* API Keys List */}
          {!loading && keys.map((key) => (
            <div key={key.id} className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
              <div className="p-6 border-b border-white/5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-sm border ${key.is_active ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-zinc-500/10 border-zinc-500/20'}`}>
                      <i data-lucide="key" className={`w-4 h-4 ${key.is_active ? 'text-emerald-400' : 'text-zinc-400'}`}></i>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-white">{key.name}</h3>
                      <p className="text-xs text-zinc-500">Created {formatDate(key.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-medium ${
                      key.is_active 
                        ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' 
                        : 'bg-zinc-500/10 border border-zinc-500/20 text-zinc-400'
                    }`}>
                      {key.is_active ? 'ACTIVE' : 'REVOKED'}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-black/50 border border-white/5 rounded-sm px-4 py-3 font-mono text-sm text-zinc-300">
                    {key.prefix}••••••••••••••••••••••••
                  </div>
                  <button 
                    onClick={() => handleCopy(key.prefix, key.id)}
                    className="p-3 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-white/5" 
                    title="Copy Prefix"
                  >
                    {copied === key.id ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
                  </button>
                </div>
              </div>
              
              <div className="px-6 py-4 bg-white/[0.01] flex items-center justify-between">
                <div className="text-xs text-zinc-500">
                  Last used: {key.last_used_at ? formatDate(key.last_used_at) : 'Never'}
                </div>
                {key.is_active && (
                  <button 
                    onClick={() => handleRevokeKey(key.id)}
                    className="text-xs text-red-400 hover:text-red-300 transition-colors"
                  >
                    Revoke Key
                  </button>
                )}
              </div>
            </div>
          ))}

          {/* Security Tips */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm p-6">
            <h3 className="text-sm font-medium text-white mb-4 flex items-center gap-2">
              <i data-lucide="shield-check" className="w-4 h-4 text-zinc-400"></i>
              Security Best Practices
            </h3>
            <ul className="space-y-3 text-sm text-zinc-400">
              <li className="flex items-start gap-2">
                <i data-lucide="check" className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0"></i>
                Never expose your API keys in client-side code or public repositories
              </li>
              <li className="flex items-start gap-2">
                <i data-lucide="check" className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0"></i>
                Use environment variables to store your keys securely
              </li>
              <li className="flex items-start gap-2">
                <i data-lucide="check" className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0"></i>
                Revoke your keys immediately if you suspect they&apos;ve been compromised
              </li>
            </ul>
          </div>

          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link>
          </div>

        </div>
      </div>

      {/* Create Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#0C0D0F] border border-white/10 rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-medium text-white mb-4">Create New API Key</h2>
            <div className="mb-4">
              <label className="block text-sm text-zinc-400 mb-2">Key Name</label>
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="e.g., Production Key"
                className="w-full bg-black/50 border border-white/10 rounded-sm px-4 py-2 text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-500"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-white/5 border border-white/10 text-zinc-400 text-sm font-medium rounded-sm hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateKey}
                disabled={creating || !newKeyName.trim()}
                className="flex-1 px-4 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create Key'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

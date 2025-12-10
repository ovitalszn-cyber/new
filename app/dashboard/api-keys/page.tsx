'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';

interface AuthUser {
  id: string;
  email: string;
  name?: string | null;
  plan: string;
  status: string;
}

interface DashboardSession {
  token: string;
  user: AuthUser;
}

type KeyStatus = 'active' | 'revoked' | 'pending' | 'unknown';
type LanguageTab = 'bash' | 'python' | 'javascript';
type SnippetKind = 'health' | 'request';

interface ApiKeyRow {
  id: string;
  name: string;
  keyPreview: string;
  keyType: string;
  status: KeyStatus;
  createdAt?: string | null;
  lastUsedAt?: string | null;
  fullKey?: string;
}

const statusColors: Record<KeyStatus, { bg: string; text: string }> = {
  active: { bg: 'bg-[#10B981]/10', text: 'text-[#10B981]' },
  pending: { bg: 'bg-[#F59E0B]/10', text: 'text-[#F59E0B]' },
  revoked: { bg: 'bg-[#EF4444]/10', text: 'text-[#EF4444]' },
  unknown: { bg: 'bg-[#635F69]/10', text: 'text-[#635F69]' },
};

const keyTypeColors: Record<string, string> = {
  LIVE: 'text-[#0EA5E9]',
  TEST: 'text-[#7C3AED]',
  SANDBOX: 'text-[#F59E0B]',
};

const snippetOrder: SnippetKind[] = ['health', 'request'];
const snippetLabels: Record<SnippetKind, string> = {
  health: 'Health Check',
  request: 'First Data Request',
};

const PUBLIC_API_BASE = process.env.NEXT_PUBLIC_PUBLIC_API_BASE || 'https://api.kashrock.com';

const formatDate = (value?: string | null) => {
  if (!value) return 'Never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
};

export default function ApiKeysPage() {
  const router = useRouter();
  const [session, setSession] = useState<DashboardSession | null>(null);
  const [keys, setKeys] = useState<ApiKeyRow[]>([]);
  const [loadingKeys, setLoadingKeys] = useState(false);
  const [keysError, setKeysError] = useState<string | null>(null);
  const [showNewKeyModal, setShowNewKeyModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKey, setNewKey] = useState<ApiKeyRow | null>(null);
  const [copiedFullKey, setCopiedFullKey] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState<{ tab: LanguageTab; kind: SnippetKind } | null>(null);
  const [activeTab, setActiveTab] = useState<LanguageTab>('bash');
  const [createError, setCreateError] = useState<string | null>(null);
  const [creatingKey, setCreatingKey] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);

  const apiBase = useMemo(() => process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000', []);

  const safeCopy = useCallback((text?: string) => {
    if (!text || typeof navigator === 'undefined') return;
    navigator.clipboard.writeText(text);
  }, []);

  const handleCopyPreview = useCallback(
    (text: string) => {
      safeCopy(text);
    },
    [safeCopy],
  );

  const handleCopyFullKey = useCallback(
    (text?: string) => {
      if (!text) return;
      safeCopy(text);
      setCopiedFullKey(true);
      setTimeout(() => setCopiedFullKey(false), 2000);
    },
    [safeCopy],
  );

  const handleCopySnippet = useCallback(
    (tab: LanguageTab, kind: SnippetKind, text: string) => {
      safeCopy(text);
      setCopiedSnippet({ tab, kind });
      setTimeout(() => setCopiedSnippet(null), 2000);
    },
    [safeCopy],
  );

  const signOut = useCallback(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('kashrock_dashboard_session');
    }
    setSession(null);
    router.push('/dashboard');
  }, [router]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = window.localStorage.getItem('kashrock_dashboard_session');
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed?.access_token && parsed?.user) {
        setSession({ token: parsed.access_token as string, user: parsed.user as AuthUser });
      }
    } catch {
      // ignore corrupted storage
    }
  }, []);

  const normalizeKey = (record: any): ApiKeyRow => {
    const prefix = record.key_prefix || record.name || 'kr_key';
    const preview = `${prefix}${prefix.includes('…') ? '' : '…'}`;
    const status = (record.status || 'unknown').toString().toLowerCase() as KeyStatus;
    return {
      id: record.id,
      name: record.name || 'Untitled key',
      keyPreview: preview,
      keyType: (record.key_type || 'live').toUpperCase(),
      status: statusColors[status] ? status : 'unknown',
      createdAt: record.created_at,
      lastUsedAt: record.last_used_at,
    };
  };

  const fetchKeys = useCallback(async () => {
    if (!session?.token) return;
    setLoadingKeys(true);
    setKeysError(null);
    try {
      const res = await fetch(`${apiBase}/v1/dashboard/api-keys`, {
        headers: { Authorization: `Bearer ${session.token}` },
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 401) {
          signOut();
          throw new Error('Session expired. Please sign in again.');
        }
        throw new Error(data?.detail || 'Failed to load API keys');
      }
      setKeys(Array.isArray(data) ? data.map(normalizeKey) : []);
    } catch (err: any) {
      setKeysError(err?.message || 'Failed to load API keys');
    } finally {
      setLoadingKeys(false);
    }
  }, [apiBase, session?.token, signOut]);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys, apiBase, session?.token, signOut]);

  const handleGenerateKey = async () => {
    if (!session?.token) return;
    setCreatingKey(true);
    setCreateError(null);
    try {
      const res = await fetch(`${apiBase}/v1/dashboard/api-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({
          name: newKeyName || undefined,
          key_type: 'live',
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 401) {
          signOut();
          throw new Error('Session expired. Please sign in again.');
        }
        throw new Error(data?.detail || 'Failed to create API key');
      }
      const generated: ApiKeyRow = normalizeKey(data);
      generated.fullKey = data.plain_key;
      setNewKey(generated);
      setNewKeyName('');
      await fetchKeys();
    } catch (err: any) {
      setCreateError(err?.message || 'Unable to create key');
    } finally {
      setCreatingKey(false);
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!session?.token) return;
    setRevokingId(keyId);
    try {
      const res = await fetch(`${apiBase}/v1/dashboard/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${session.token}` },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (res.status === 401) {
          signOut();
          throw new Error('Session expired. Please sign in again.');
        }
        throw new Error(data?.detail || 'Failed to delete key');
      }
      await fetchKeys();
    } catch (err: any) {
      setKeysError(err?.message || 'Unable to delete key');
    } finally {
      setRevokingId(null);
    }
  };

  const codeExamples = useMemo(() => {
    const token = newKey?.fullKey || 'kr_YOUR_API_KEY';
    const bearer = `Bearer ${token}`;
    return {
      bash: {
        health: `curl -H "Authorization: ${bearer}" "${PUBLIC_API_BASE}/health"`,
        request: `curl -H "Authorization: ${bearer}" "${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba"`,
      },
      python: {
        health: `import httpx

headers = {"Authorization": "${bearer}"}
health = httpx.get("${PUBLIC_API_BASE}/health", headers=headers)
health.raise_for_status()`,
        request: `import httpx

headers = {"Authorization": "${bearer}"}
response = httpx.get("${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba", headers=headers)
response.raise_for_status()
print(response.json())`,
      },
      javascript: {
        health: `const headers = { Authorization: "${bearer}" };
const health = await fetch("${PUBLIC_API_BASE}/health", { headers });
if (!health.ok) throw new Error("Key failed health check");`,
        request: `const headers = { Authorization: "${bearer}" };
const response = await fetch("${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba", { headers });
const data = await response.json();
console.log(data);`,
      },
    } satisfies Record<LanguageTab, Record<SnippetKind, string>>;
  }, [newKey]);

  const renderAuthGuard = () => (
    <div className="max-w-md mx-auto mt-8 clay-card shadow-clay-card p-8 text-center">
      <h2
        className="text-2xl font-black text-[#332F3A] mb-3"
        style={{ fontFamily: 'Nunito, sans-serif' }}
      >
        Sign in to manage API keys
      </h2>
      <p className="text-sm text-[#635F69]">
        Go back to the main dashboard and complete sign in to access this page.
      </p>
      <a
        href="/dashboard"
        className="inline-flex items-center justify-center mt-6 px-5 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all"
      >
        Go to Dashboard
      </a>
    </div>
  );

  const renderKeys = () => {
    if (loadingKeys) {
      return (
        <div className="clay-card shadow-clay-card p-8 text-center text-[#635F69]">
          Loading your API keys…
        </div>
      );
    }

    if (keysError) {
      return (
        <div className="clay-card shadow-clay-card p-8 text-center text-red-600">
          {keysError}
        </div>
      );
    }

    if (keys.length === 0) {
      return (
        <div className="clay-card shadow-clay-card p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#7C3AED]/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-[#7C3AED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
            No API keys yet
          </h3>
          <p className="text-[#635F69] mb-6">
            Click “Generate New Key” to create your first key.
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {keys.map((key) => (
          <div
            key={key.id}
            className="clay-card shadow-clay-card p-6 hover:shadow-clay-card-hover transition-all duration-300"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    {key.name}
                  </h3>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${statusColors[key.status].bg} ${statusColors[key.status].text}`}>
                    {key.status.toUpperCase()}
                  </span>
                  <span className={`text-xs font-bold ${keyTypeColors[key.keyType] || 'text-[#635F69]'}`}>
                    {key.keyType}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <code className="px-3 py-1.5 rounded-lg bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono">
                    {key.keyPreview}
                  </code>
                  <button
                    onClick={() => handleCopyPreview(key.keyPreview)}
                    className="p-2 rounded-lg hover:bg-[#7C3AED]/10 text-[#635F69] hover:text-[#7C3AED] transition-colors"
                    title="Copy key preview"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
                <div className="flex flex-wrap gap-4 mt-2 text-xs text-[#635F69]">
                  <span>Created: {formatDate(key.createdAt)}</span>
                  <span>Last used: {formatDate(key.lastUsedAt)}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDeleteKey(key.id)}
                  disabled={revokingId === key.id}
                  className="p-2.5 rounded-xl bg-white shadow-clay-card hover:shadow-clay-card-hover text-[#635F69] hover:text-[#EF4444] transition-all disabled:opacity-50"
                  title="Delete key"
                >
                  {revokingId === key.id ? (
                    <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          API Keys
        </h1>
        <p className="text-[#635F69]">
          Manage your API keys, run a health check, and rotate credentials safely.
        </p>
      </div>

      {!session?.token ? (
        renderAuthGuard()
      ) : (
        <>
          <div className="mb-8 flex flex-wrap gap-3">
            <button
              onClick={() => {
                setShowNewKeyModal(true);
                setNewKey(null);
                setCreateError(null);
              }}
              className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.98] transition-all duration-200 flex items-center gap-2"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Generate New Key
            </button>
            <button
              onClick={fetchKeys}
              className="h-12 px-6 rounded-[20px] bg-white text-[#635F69] font-bold shadow-clay-card hover:shadow-clay-card-hover transition-all flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
          {renderKeys()}
        </>
      )}

      {showNewKeyModal && session?.token && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-sm">
          <div className="clay-card shadow-clay-surface p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {!newKey ? (
              <>
                <h2 className="text-2xl font-black text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
                  Generate New API Key
                </h2>
                <p className="text-[#635F69] mb-6">
                  Give your key a name to help you identify it later.
                </p>
                {createError && (
                  <div className="mb-4 text-sm text-red-700 bg-red-100 border border-red-300 rounded-lg px-3 py-2">
                    {createError}
                  </div>
                )}
                <input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g., Production Key, Test Key"
                  className="w-full h-14 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] placeholder-[#635F69]/50 font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all mb-6"
                />
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowNewKeyModal(false)}
                    className="flex-1 h-12 rounded-[20px] bg-white text-[#635F69] font-bold shadow-clay-card hover:shadow-clay-card-hover transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleGenerateKey}
                    disabled={creatingKey}
                    className="flex-1 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all disabled:opacity-60"
                  >
                    {creatingKey ? 'Generating…' : 'Generate Key'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-full bg-[#10B981]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                      Your New API Key
                    </h2>
                    <p className="text-sm text-[#635F69]">{newKey.name}</p>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center gap-2 p-4 rounded-2xl bg-[#1e1e2e]">
                    <code className="flex-1 text-[#A78BFA] font-mono text-sm break-all">
                      {newKey.fullKey}
                    </code>
                    <button
                      onClick={() => handleCopyFullKey(newKey.fullKey)}
                      className={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${copiedFullKey
                        ? 'bg-[#10B981] text-white'
                        : 'bg-[#7C3AED] text-white hover:bg-[#6D28D9]'
                        }`}
                    >
                      {copiedFullKey ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <p className="mt-2 text-sm text-[#F59E0B] flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    Copy this key now. For your security, it will not be shown again.
                  </p>
                </div>

                <div className="mb-6">
                  <h3 className="font-bold text-[#332F3A] mb-3" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    Quick Start
                  </h3>
                  <p className="text-sm text-[#635F69] mb-4">
                    First run the health check. If it fails, submit a ticket immediately.
                  </p>

                  <div className="flex gap-1 mb-4">
                    {(['bash', 'python', 'javascript'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${activeTab === tab
                          ? 'bg-[#7C3AED] text-white'
                          : 'bg-[#EFEBF5] text-[#635F69] hover:text-[#7C3AED]'
                          }`}
                      >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                      </button>
                    ))}
                  </div>

                  <div className="space-y-4">
                    {snippetOrder.map((kind) => {
                      const snippet = codeExamples[activeTab][kind];
                      const isCopied = copiedSnippet?.tab === activeTab && copiedSnippet?.kind === kind;
                      return (
                        <div key={`${activeTab}-${kind}`} className="clay-card shadow-clay-card p-4 bg-[#110f1a]/70 border border-[#281f3c]/40">
                          <div className="flex items-center justify-between mb-3">
                            <div>
                              <p className="text-xs uppercase tracking-wide text-[#A78BFA]/80 font-bold">
                                {snippetLabels[kind]}
                              </p>
                            </div>
                            <button
                              onClick={() => handleCopySnippet(activeTab, kind, snippet)}
                              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${isCopied ? 'bg-[#10B981] text-white' : 'bg-[#7C3AED]/20 text-[#A78BFA] hover:bg-[#7C3AED]/30'
                                }`}
                            >
                              {isCopied ? 'Copied!' : 'Copy'}
                            </button>
                          </div>
                          <pre className="p-3 rounded-xl bg-[#1e1e2e] text-sm font-mono text-[#E5E1EF] overflow-x-auto">
                            <code>{snippet}</code>
                          </pre>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <a
                    href="/docs"
                    className="flex-1 h-12 rounded-[20px] bg-white text-[#7C3AED] font-bold shadow-clay-card hover:shadow-clay-card-hover transition-all flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    Go to Docs
                  </a>
                  <button
                    onClick={() => {
                      setShowNewKeyModal(false);
                      setNewKey(null);
                    }}
                    className="flex-1 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all"
                  >
                    Done
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

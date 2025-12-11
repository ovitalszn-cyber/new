'use client';

import { useMemo, useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import AuthGuard from '@/components/AuthGuard';
import { useSession } from 'next-auth/react';

type LanguageTab = 'bash' | 'python' | 'javascript';

const PUBLIC_API_BASE =
  process.env.NEXT_PUBLIC_PUBLIC_API_BASE || 'https://api.kashrock.com';

const DEMO_KEY = 'kr_YOUR_API_KEY';

interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  key_type: string;
  status: string;
  created_at: string;
  last_used_at: string | null;
}

const keyTypeColors: Record<string, string> = {
  live: 'from-[#0EA5E9] to-[#0284C7]',
  test: 'from-[#A78BFA] to-[#7C3AED]',
};

const formatDate = (value?: string | null) => {
  if (!value) return 'Never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
};

export default function ApiKeysPage() {
  const { data: session } = useSession();
  const [activeTab, setActiveTab] = useState<LanguageTab>('bash');
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newKeySecret, setNewKeySecret] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (session) {
      fetchKeys();
    }
  }, [session]);

  const getAuthToken = () => {
    if (!session) return null;
    // @ts-ignore
    return session.accessToken;
  };

  const fetchKeys = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = getAuthToken();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${PUBLIC_API_BASE}/v1/dashboard/api-keys`, {
        headers,
      });

      if (res.ok) {
        const data = await res.json();
        const keyList = Array.isArray(data) ? data : (data.keys || []);
        setKeys(keyList);
      } else {
        console.warn(`Fetch keys failed: ${res.status}`);
      }
    } catch (err) {
      console.error("Error fetching keys:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateKey = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const token = getAuthToken();
      if (!token) {
        setError("You must be logged in to generate a key.");
        return;
      }

      const res = await fetch(`${PUBLIC_API_BASE}/v1/dashboard/api-keys`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'My API Key',
          key_type: 'live',
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to generate key");
      }

      const data = await res.json();
      if (data.plain_key) {
        setNewKeySecret(data.plain_key);
        fetchKeys();
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (err) {
      console.error(err);
      setError("Failed to create a new API key. Please check your connection or login status.");
    } finally {
      setIsGenerating(false);
    }
  };

  const currentDisplayKey = newKeySecret || (keys.length > 0 ? keys[0].key_prefix : DEMO_KEY);
  const isDemo = !newKeySecret && keys.length === 0;

  const codeExamples: Record<LanguageTab, string> = {
    bash: `curl -H "Authorization: Bearer ${currentDisplayKey}" \\
  "${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba"`,
    python: `import httpx

headers = {"Authorization": "Bearer ${currentDisplayKey}"}
response = httpx.get("${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba", headers=headers)
response.raise_for_status()
print(response.json())`,
    javascript: `const headers = { Authorization: "Bearer ${currentDisplayKey}" };
const response = await fetch("${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba", { headers });
const data = await response.json();
console.log(data);`,
  };

  const activeSnippet = useMemo(
    () => codeExamples[activeTab],
    [activeTab, currentDisplayKey],
  );

  const handleCopyKey = async () => {
    if (typeof navigator === 'undefined') return;
    await navigator.clipboard.writeText(currentDisplayKey);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 1500);
  };

  const handleCopySnippet = async () => {
    if (typeof navigator === 'undefined') return;
    await navigator.clipboard.writeText(activeSnippet);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 1500);
  };

  return (
    <AuthGuard>
      <DashboardLayout>
        {/* Floating Blobs Background */}
        <div className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
          <div
            className="absolute h-[35vh] w-[35vh] rounded-full blur-3xl bg-[#A78BFA]/5 animate-clay-float"
            style={{ top: '15%', right: '10%' }}
          />
          <div
            className="absolute h-[30vh] w-[30vh] rounded-full blur-3xl bg-[#10B981]/5 animate-clay-float-delayed"
            style={{ bottom: '25%', left: '-5%' }}
          />
        </div>

        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#7C3AED]/10 text-[#7C3AED] font-semibold text-sm mb-4">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
                API Keys
              </div>
              <h1
                className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
                style={{ fontFamily: 'Nunito, sans-serif' }}
              >
                Manage Your{' '}
                <span className="bg-gradient-to-r from-[#A78BFA] via-[#7C3AED] to-[#DB2777] bg-clip-text text-transparent">
                  API Keys
                </span>
              </h1>
              <p className="text-[#635F69]">
                Generate and manage API keys to authenticate your requests.
              </p>
            </div>
            <div>
              <button
                onClick={handleGenerateKey}
                disabled={isGenerating}
                className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.95] transition-all duration-200 disabled:opacity-50 disabled:hover:translate-y-0 flex items-center gap-2"
                style={{ fontFamily: 'Nunito, sans-serif' }}
              >
                {isGenerating ? (
                  <>
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Generate New Key
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-red-50 text-red-600 font-medium border border-red-100 flex items-center gap-3">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {newKeySecret && (
          <div className="mb-8 clay-card shadow-clay-card p-6 bg-gradient-to-br from-[#10B981]/10 to-[#059669]/5 border border-[#10B981]/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#34D399] to-[#10B981] shadow-clay-orb flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-[#065F46]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                  New Key Generated!
                </h3>
                <p className="text-sm text-[#064E3B]">
                  Copy your key now. It won't be shown again.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <code className="flex-1 px-4 py-3 rounded-xl bg-white text-[#065F46] font-mono border border-[#10B981]/30 break-all text-sm">
                {newKeySecret}
              </code>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(newKeySecret);
                  setCopiedKey(true);
                  setTimeout(() => setCopiedKey(false), 1500);
                }}
                className="h-10 px-4 rounded-xl bg-[#10B981] text-white text-sm font-bold shadow-sm hover:bg-[#059669] transition-colors"
              >
                {copiedKey ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
        )}

        {/* Get Started Card */}
        {keys.length === 0 && !loading && !newKeySecret && (
          <div className="clay-card shadow-clay-card p-6 mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#0EA5E9] to-[#0284C7] shadow-clay-orb flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>Get Started</h3>
                <p className="text-sm text-[#635F69]">Generate your first API key to start making requests.</p>
              </div>
            </div>
          </div>
        )}

        {/* Current Key Card */}
        <div className="clay-card shadow-clay-card p-6 mb-8">
          <h2
            className="text-xl font-bold text-[#332F3A] mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            {isDemo ? 'Demo Key' : 'Your API Key'}
          </h2>

          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <code className="flex-1 px-4 py-3 rounded-xl bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono break-all">
              {currentDisplayKey}
            </code>
            <button
              onClick={handleCopyKey}
              className={`h-10 px-5 rounded-xl font-bold text-sm transition-all ${copiedKey
                ? 'bg-[#10B981] text-white'
                : 'bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1'
                }`}
            >
              {copiedKey ? 'Copied!' : 'Copy Key'}
            </button>
          </div>
          <p className="mt-3 text-xs text-[#635F69]">
            {isDemo
              ? "This is a placeholder. Generate a real key to access the API."
              : "Use this key in the Authorization header for API requests."}
          </p>
        </div>

        {/* Keys Overview */}
        <div className="mb-10">
          <h2
            className="text-xl font-bold text-[#332F3A] mb-5"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            Keys Overview
          </h2>
          {loading ? (
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="clay-card shadow-clay-card p-6 animate-pulse">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-6 bg-[#EFEBF5] rounded w-32" />
                    <div className="h-5 bg-[#EFEBF5] rounded-full w-16" />
                  </div>
                  <div className="h-8 bg-[#EFEBF5] rounded w-48" />
                </div>
              ))}
            </div>
          ) : keys.length === 0 ? (
            <div className="text-sm text-[#635F69] italic p-4">No active keys found.</div>
          ) : (
            <div className="space-y-4">
              {keys.map((key) => (
                <div
                  key={key.id}
                  className="clay-card shadow-clay-card p-6 hover:-translate-y-1 hover:shadow-clay-card-hover transition-all duration-300"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3
                          className="font-bold text-[#332F3A]"
                          style={{ fontFamily: 'Nunito, sans-serif' }}
                        >
                          {key.name || 'API Key'}
                        </h3>
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#10B981]/10 text-[#10B981]">
                          {key.status || 'ACTIVE'}
                        </span>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold text-white bg-gradient-to-r ${keyTypeColors[key.key_type] || 'from-gray-400 to-gray-500'}`}>
                          {key.key_type?.toUpperCase()}
                        </span>
                      </div>
                      <code className="inline-block px-3 py-1.5 rounded-lg bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono">
                        {key.key_prefix}
                      </code>
                      <div className="flex flex-wrap gap-4 mt-3 text-xs text-[#635F69]">
                        <span>Created: {formatDate(key.created_at)}</span>
                        {key.last_used_at && <span>Last used: {formatDate(key.last_used_at)}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Start */}
        <div className="clay-card shadow-clay-card p-8 relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-40 h-40 rounded-full bg-gradient-to-br from-[#7C3AED]/10 to-[#DB2777]/10 blur-3xl" />

          <div className="relative z-10">
            <h2
              className="text-xl font-bold text-[#332F3A] mb-5"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Quick Start
            </h2>

            <div className="flex gap-2 mb-5">
              {(['bash', 'python', 'javascript'] as LanguageTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => {
                    setActiveTab(tab);
                    setCopiedSnippet(false);
                  }}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${activeTab === tab
                    ? 'bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white shadow-clay-button'
                    : 'bg-[#EFEBF5] text-[#635F69] hover:text-[#7C3AED]'
                    }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div className="mb-3 flex justify-between items-center">
              <p className="text-xs uppercase tracking-wide text-[#7C3AED] font-bold">
                Example Request ({activeTab})
              </p>
              <button
                onClick={handleCopySnippet}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${copiedSnippet
                  ? 'bg-[#10B981] text-white'
                  : 'bg-[#7C3AED]/10 text-[#7C3AED] hover:bg-[#7C3AED]/20'
                  }`}
              >
                {copiedSnippet ? 'Copied!' : 'Copy Snippet'}
              </button>
            </div>

            <pre className="p-4 rounded-xl bg-[#1e1e2e] text-sm font-mono text-[#E5E1EF] overflow-x-auto">
              <code>{activeSnippet}</code>
            </pre>
          </div>
        </div>
      </DashboardLayout>
    </AuthGuard>
  );
}
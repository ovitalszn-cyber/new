'use client';

import { useMemo, useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import AuthGuard from '@/components/AuthGuard';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';

type LanguageTab = 'bash' | 'python' | 'javascript';

const PUBLIC_API_BASE =
  process.env.NEXT_PUBLIC_PUBLIC_API_BASE || 'https://api.kashrock.com';

// This is a demo key shown if no keys exist or for the demo section
const DEMO_KEY = 'kr_YOUR_API_KEY';

interface ApiKey {
  id: string;
  name: string;
  keyPreview: string;
  keyType: string;
  status: string;
  createdAt: string;
  lastUsedAt: string | null;
}

const keyTypeColors: Record<string, string> = {
  LIVE: 'text-[#0EA5E9]',
  TEST: 'text-[#7C3AED]',
};

const formatDate = (value?: string | null) => {
  if (!value) return 'Never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
};

export default function ApiKeysPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [activeTab, setActiveTab] = useState<LanguageTab>('bash');
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  // Real state
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newKeySecret, setNewKeySecret] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Load keys on session change
  useEffect(() => {
    if (session) {
      fetchKeys();
    }
  }, [session]);

  const getAuthToken = () => {
    if (!session) return null;
    // @ts-ignore
    return session.id_token || session.accessToken;
  };

  const fetchKeys = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = getAuthToken();
      // Even if no token, try fetching. The backend will handle 401.

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${PUBLIC_API_BASE}/v1/dashboard/api-keys`, {
        headers,
      });

      if (!res.ok) {
        // Gracefully handle errors (e.g. 401 or 404 if endpoint missing)
        console.warn(`Fetch keys failed: ${res.status}`);
      } else {
        const data = await res.json();
        // Support { keys: [] } or just []
        const keyList = Array.isArray(data) ? data : (data.keys || []);
        setKeys(keyList);
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
      });

      if (!res.ok) {
        throw new Error("Failed to generate key");
      }

      const data = await res.json();
      // Expected response: { key_id, key_secret, ... }
      if (data.key_secret) {
        setNewKeySecret(data.key_secret);
        fetchKeys(); // Refresh list
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

  // Determine what key to show in code snippets
  const currentDisplayKey = newKeySecret || (keys.length > 0 ? keys[0].keyPreview : DEMO_KEY);
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
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1
              className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              API Keys
            </h1>
            <p className="text-[#635F69]">
              Generate and manage your API keys.
            </p>
          </div>
          <div>
            <button
              onClick={handleGenerateKey}
              disabled={isGenerating}
              className="px-6 py-3 rounded-xl bg-[#7C3AED] text-white font-bold text-sm shadow-clay-button hover:bg-[#6D28D9] hover:-translate-y-1 transition-all disabled:opacity-50 disabled:hover:translate-y-0"
            >
              {isGenerating ? 'Generating...' : 'Generate New Key'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 text-red-600 font-medium border border-red-100">
            {error}
          </div>
        )}

        {newKeySecret && (
          <div className="mb-8 p-6 rounded-2xl bg-[#10B981]/10 border border-[#10B981]/20 animate-fade-in">
            <h3 className="text-lg font-bold text-[#065F46] mb-2">New Key Generated!</h3>
            <p className="text-sm text-[#064E3B] mb-4">
              Please copy your key now. For security reasons, it will not be shown again in full.
            </p>
            <div className="flex items-center gap-4">
              <code className="flex-1 px-4 py-3 rounded-xl bg-white text-[#065F46] font-mono border border-[#10B981]/30 break-all">
                {newKeySecret}
              </code>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(newKeySecret);
                  setCopiedKey(true);
                  setTimeout(() => setCopiedKey(false), 1500);
                }}
                className="px-4 py-2 rounded-lg bg-[#10B981] text-white text-sm font-bold shadow-sm hover:bg-[#059669]"
              >
                {copiedKey ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>
        )}

        {/* Helper Card */}
        {keys.length === 0 && !loading && !newKeySecret && (
          <div className="clay-card shadow-clay-card p-6 mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 flex-shrink-0 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
              <div>
                <h3 className="font-bold text-[#332F3A]">Get Started</h3>
                <p className="text-sm text-[#635F69]">Generate a key above to start making requests. The code snippets below use a placeholder until you generate a key.</p>
              </div>
            </div>
          </div>
        )}

        {/* Key card (Demo or User Key) */}
        <div className="clay-card shadow-clay-card p-6 mb-8">
          <h2
            className="text-xl font-bold text-[#332F3A] mb-3"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            {isDemo ? 'Demo Key' : 'Your API Key'}
          </h2>

          {/* If we have keys, we show the first one or logic to show active one. For simplicity, just showing preview logic in snippets. */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            {/* If user has new secret, we showed it above. Here we show what is used in snippets. */}
            <code className="flex-1 px-3 py-2 rounded-lg bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono break-all">
              {currentDisplayKey}
            </code>
            <button
              onClick={handleCopyKey}
              className={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${copiedKey
                ? 'bg-[#10B981] text-white'
                : 'bg-[#7C3AED] text-white hover:bg-[#6D28D9]'
                }`}
            >
              {copiedKey ? 'Copied!' : 'Copy key'}
            </button>
          </div>
          <p className="mt-3 text-xs text-[#635F69]">
            {isDemo
              ? "This is a placeholder key. Generate a real key to access the API."
              : "This is your active API key (or preview). Use it in the Authorization header."}
          </p>
        </div>

        {/* Key list */}
        <div className="mb-10">
          <h2
            className="text-lg font-bold text-[#332F3A] mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            Keys overview
          </h2>
          {loading ? (
            <div className="flex items-center gap-2 text-[#635F69]">
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Loading keys...</span>
            </div>
          ) : keys.length === 0 ? (
            <div className="text-sm text-[#635F69] italic">No active keys found.</div>
          ) : (
            <div className="space-y-4">
              {keys.map((key) => (
                <div
                  key={key.id}
                  className="clay-card shadow-clay-card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3
                        className="font-bold text-[#332F3A]"
                        style={{ fontFamily: 'Nunito, sans-serif' }}
                      >
                        {key.name || 'API Key'}
                      </h3>
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-bold bg-[#10B981]/10 text-[#10B981]`}
                      >
                        {key.status || 'ACTIVE'}
                      </span>
                      <span
                        className={`text-xs font-bold ${keyTypeColors[key.keyType] || 'text-[#635F69]'
                          }`}
                      >
                        {key.keyType}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <code className="px-3 py-1.5 rounded-lg bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono">
                        {key.keyPreview}
                      </code>
                    </div>
                    <div className="flex flex-wrap gap-4 mt-2 text-xs text-[#635F69]">
                      <span>Created: {formatDate(key.createdAt)}</span>
                      {key.lastUsedAt && <span>Last used: {formatDate(key.lastUsedAt)}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick start */}
        <div className="clay-card shadow-clay-card p-8">
          <h2
            className="text-xl font-bold text-[#332F3A] mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            Quick start
          </h2>

          <div className="flex gap-2 mb-4">
            {(['bash', 'python', 'javascript'] as LanguageTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab);
                  setCopiedSnippet(false);
                }}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${activeTab === tab
                  ? 'bg-[#7C3AED] text-white'
                  : 'bg-[#EFEBF5] text-[#635F69] hover:text-[#7C3AED]'
                  }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          <div className="mb-3 flex justify-between items-center">
            <p className="text-xs uppercase tracking-wide text-[#A78BFA]/80 font-bold">
              Example request ({activeTab})
            </p>
            <button
              onClick={handleCopySnippet}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${copiedSnippet
                ? 'bg-[#10B981] text-white'
                : 'bg-[#7C3AED]/20 text-[#A78BFA] hover:bg-[#7C3AED]/30'
                }`}
            >
              {copiedSnippet ? 'Snippet copied!' : 'Copy snippet'}
            </button>
          </div>

          <pre className="p-3 rounded-xl bg-[#1e1e2e] text-sm font-mono text-[#E5E1EF] overflow-x-auto">
            <code>{activeSnippet}</code>
          </pre>
        </div>
      </DashboardLayout>
    </AuthGuard>
  );
}
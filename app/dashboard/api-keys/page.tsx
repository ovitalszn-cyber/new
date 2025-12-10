'use client';

import { useMemo, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

type LanguageTab = 'bash' | 'python' | 'javascript';

const PUBLIC_API_BASE =
  process.env.NEXT_PUBLIC_PUBLIC_API_BASE || 'https://api.kashrock.com';

// This is a demo key shown in the UI only.
// Do NOT put a real secret here unless you truly intend it to be public.
const DEMO_KEY = 'kr_YOUR_API_KEY';

const mockKeys = [
  {
    id: 'live_prod',
    name: 'Production Key (Demo)',
    keyPreview: 'kr_live_prod_9f3c…',
    keyType: 'LIVE',
    status: 'ACTIVE',
    createdAt: '2024-11-02',
    lastUsedAt: '2024-12-09',
  },
];

const keyTypeColors: Record<string, string> = {
  LIVE: 'text-[#0EA5E9]',
  TEST: 'text-[#7C3AED]',
};

const codeExamples: Record<LanguageTab, string> = {
  bash: `curl -H "Authorization: Bearer ${DEMO_KEY}" \\
  "${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba"`,
  python: `import httpx

headers = {"Authorization": "Bearer ${DEMO_KEY}"}
response = httpx.get("${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba", headers=headers)
response.raise_for_status()
print(response.json())`,
  javascript: `const headers = { Authorization: "Bearer ${DEMO_KEY}" };
const response = await fetch("${PUBLIC_API_BASE}/v6/odds?sport=basketball_nba", { headers });
const data = await response.json();
console.log(data);`,
};

const formatDate = (value?: string | null) => {
  if (!value) return 'Never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
};

export default function ApiKeysPage() {
  const [activeTab, setActiveTab] = useState<LanguageTab>('bash');
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  const activeSnippet = useMemo(
    () => codeExamples[activeTab],
    [activeTab],
  );

  const handleCopyKey = async () => {
    if (typeof navigator === 'undefined') return;
    await navigator.clipboard.writeText(DEMO_KEY);
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
    <DashboardLayout>
      <div className="mb-8">
        <h1
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          API Keys
        </h1>
        <p className="text-[#635F69]">
          Use this demo key to try the KashRock API. No sign‑in required.
        </p>
      </div>

      {/* Key card */}
      <div className="clay-card shadow-clay-card p-6 mb-8">
        <h2
          className="text-xl font-bold text-[#332F3A] mb-3"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Your API Key
        </h2>
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <code className="flex-1 px-3 py-2 rounded-lg bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono break-all">
            {DEMO_KEY}
          </code>
          <button
            onClick={handleCopyKey}
            className={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${
              copiedKey
                ? 'bg-[#10B981] text-white'
                : 'bg-[#7C3AED] text-white hover:bg-[#6D28D9]'
            }`}
          >
            {copiedKey ? 'Copied!' : 'Copy key'}
          </button>
        </div>
        <p className="mt-3 text-xs text-[#635F69]">
          This key is shown directly in the dashboard and does not require signing in.
        </p>
      </div>

      {/* Key list (static) */}
      <div className="mb-10">
        <h2
          className="text-lg font-bold text-[#332F3A] mb-4"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Keys overview
        </h2>
        <div className="space-y-4">
          {mockKeys.map((key) => (
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
                    {key.name}
                  </h3>
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-bold bg-[#10B981]/10 text-[#10B981]`}
                  >
                    {key.status}
                  </span>
                  <span
                    className={`text-xs font-bold ${
                      keyTypeColors[key.keyType] || 'text-[#635F69]'
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
                  <span>Last used: {formatDate(key.lastUsedAt)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
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
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === tab
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
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
              copiedSnippet
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
  );
}
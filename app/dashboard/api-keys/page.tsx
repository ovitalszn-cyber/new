'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

interface ApiKey {
  id: string;
  name: string;
  keyPreview: string;
  fullKey?: string;
  status: 'ACTIVE' | 'UNVERIFIED' | 'DISABLED' | 'EXPIRED' | 'PENDING_REVIEW';
  tier: 'FREE' | 'STARTER' | 'DEVELOPER' | 'PRO' | 'ENTERPRISE';
  createdAt: string;
  lastUsed: string | null;
}

const statusColors: Record<ApiKey['status'], { bg: string; text: string }> = {
  ACTIVE: { bg: 'bg-[#10B981]/10', text: 'text-[#10B981]' },
  UNVERIFIED: { bg: 'bg-[#635F69]/10', text: 'text-[#635F69]' },
  DISABLED: { bg: 'bg-[#EF4444]/10', text: 'text-[#EF4444]' },
  EXPIRED: { bg: 'bg-[#EF4444]/10', text: 'text-[#EF4444]' },
  PENDING_REVIEW: { bg: 'bg-[#F59E0B]/10', text: 'text-[#F59E0B]' },
};

const tierColors: Record<ApiKey['tier'], string> = {
  FREE: 'text-[#635F69]',
  STARTER: 'text-[#0EA5E9]',
  DEVELOPER: 'text-[#7C3AED]',
  PRO: 'text-[#DB2777]',
  ENTERPRISE: 'text-[#F59E0B]',
};

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'Production Key',
      keyPreview: 'kr_prod_xxxx...a1b2',
      status: 'ACTIVE',
      tier: 'DEVELOPER',
      createdAt: '2024-01-15',
      lastUsed: '2024-01-20',
    },
    {
      id: '2',
      name: 'Test Key',
      keyPreview: 'kr_test_xxxx...c3d4',
      status: 'UNVERIFIED',
      tier: 'FREE',
      createdAt: '2024-01-18',
      lastUsed: null,
    },
  ]);

  const [showNewKeyModal, setShowNewKeyModal] = useState(false);
  const [newKey, setNewKey] = useState<ApiKey | null>(null);
  const [newKeyName, setNewKeyName] = useState('');
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'bash' | 'python' | 'javascript'>('bash');

  const generateKey = () => {
    const fullKey = `kr_live_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;
    const generatedKey: ApiKey = {
      id: String(keys.length + 1),
      name: newKeyName || 'New API Key',
      keyPreview: `${fullKey.substring(0, 12)}...${fullKey.substring(fullKey.length - 4)}`,
      fullKey: fullKey,
      status: 'UNVERIFIED',
      tier: 'FREE',
      createdAt: new Date().toISOString().split('T')[0],
      lastUsed: null,
    };
    setNewKey(generatedKey);
    setKeys([...keys, generatedKey]);
    setNewKeyName('');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const codeExamples = {
    bash: `curl -H "Authorization: Bearer ${newKey?.fullKey || 'kr_YOUR_API_KEY'}" \\
  "https://api.kashrock.com/v5/match?sport=basketball_nba"`,
    python: `import httpx

headers = {"Authorization": "Bearer ${newKey?.fullKey || 'kr_YOUR_API_KEY'}"}
response = httpx.get(
    "https://api.kashrock.com/v5/match?sport=basketball_nba",
    headers=headers
)
print(response.json())`,
    javascript: `const response = await fetch(
  "https://api.kashrock.com/v5/match?sport=basketball_nba",
  {
    headers: {
      "Authorization": "Bearer ${newKey?.fullKey || 'kr_YOUR_API_KEY'}"
    }
  }
);
const data = await response.json();
console.log(data);`,
  };

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          API Keys
        </h1>
        <p className="text-[#635F69]">
          Manage your API keys to access the KashRock API.
        </p>
      </div>

      {/* Generate New Key Button */}
      <div className="mb-8">
        <button
          onClick={() => setShowNewKeyModal(true)}
          className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.92] transition-all duration-200 flex items-center gap-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Generate New Key
        </button>
      </div>

      {/* Keys List */}
      {keys.length === 0 ? (
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
            Click &quot;Generate New Key&quot; to get started!
          </p>
        </div>
      ) : (
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
                      {key.status}
                    </span>
                    <span className={`text-xs font-bold ${tierColors[key.tier]}`}>
                      {key.tier}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <code className="px-3 py-1.5 rounded-lg bg-[#1e1e2e] text-[#A78BFA] text-sm font-mono">
                      {key.keyPreview}
                    </code>
                    <button
                      onClick={() => copyToClipboard(key.keyPreview)}
                      className="p-2 rounded-lg hover:bg-[#7C3AED]/10 text-[#635F69] hover:text-[#7C3AED] transition-colors"
                      title="Copy key ID"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-[#635F69]">
                    <span>Created: {key.createdAt}</span>
                    <span>Last used: {key.lastUsed || 'Never'}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  <button className="p-2.5 rounded-xl bg-white shadow-clay-card hover:shadow-clay-card-hover text-[#635F69] hover:text-[#7C3AED] transition-all" title="View Details">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button className="p-2.5 rounded-xl bg-white shadow-clay-card hover:shadow-clay-card-hover text-[#635F69] hover:text-[#F59E0B] transition-all" title="Regenerate">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <button className="p-2.5 rounded-xl bg-white shadow-clay-card hover:shadow-clay-card-hover text-[#635F69] hover:text-[#EF4444] transition-all" title="Delete">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Generate Key Modal */}
      {showNewKeyModal && (
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
                    onClick={generateKey}
                    className="flex-1 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all"
                  >
                    Generate Key
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

                {/* Full Key Display */}
                <div className="mb-4">
                  <div className="flex items-center gap-2 p-4 rounded-2xl bg-[#1e1e2e]">
                    <code className="flex-1 text-[#A78BFA] font-mono text-sm break-all">
                      {newKey.fullKey}
                    </code>
                    <button
                      onClick={() => copyToClipboard(newKey.fullKey || '')}
                      className={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${
                        copied
                          ? 'bg-[#10B981] text-white'
                          : 'bg-[#7C3AED] text-white hover:bg-[#6D28D9]'
                      }`}
                    >
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <p className="mt-2 text-sm text-[#F59E0B] flex items-center gap-2">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    Copy this key now. For your security, it will not be shown again.
                  </p>
                </div>

                {/* Quick Start */}
                <div className="mb-6">
                  <h3 className="font-bold text-[#332F3A] mb-3" style={{ fontFamily: 'Nunito, sans-serif' }}>
                    Quick Start
                  </h3>
                  <p className="text-sm text-[#635F69] mb-4">
                    Run your first request with this key:
                  </p>

                  {/* Tabs */}
                  <div className="flex gap-1 mb-3">
                    {(['bash', 'python', 'javascript'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
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

                  {/* Code Block */}
                  <div className="relative">
                    <pre className="p-4 rounded-2xl bg-[#1e1e2e] text-sm font-mono text-[#E5E1EF] overflow-x-auto">
                      <code>{codeExamples[activeTab]}</code>
                    </pre>
                    <button
                      onClick={() => copyToClipboard(codeExamples[activeTab])}
                      className="absolute top-3 right-3 px-3 py-1.5 rounded-lg bg-[#7C3AED]/20 text-[#A78BFA] text-xs font-bold hover:bg-[#7C3AED]/30 transition-colors"
                    >
                      Copy
                    </button>
                  </div>
                </div>

                {/* Actions */}
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

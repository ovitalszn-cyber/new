'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';

export default function APIKeysPage() {
  const { data: session } = useSession();
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [testKeyVisible, setTestKeyVisible] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  const userName = session?.user?.name || 'User';

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).lucide) {
      (window as any).lucide.createIcons({
        attrs: {
          'stroke-width': 1.5
        }
      });
    }
  }, []);

  const handleCopy = (key: string, type: string) => {
    navigator.clipboard.writeText(key);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
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
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">API Keys</h1>
            <p className="text-sm text-zinc-500">Manage your API keys for authentication. Keep your keys secure and never share them publicly.</p>
          </div>

          {/* Live API Key */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/10 rounded-sm border border-emerald-500/20">
                    <i data-lucide="key" className="w-4 h-4 text-emerald-400"></i>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-white">Live API Key</h3>
                    <p className="text-xs text-zinc-500">Use this key for production requests</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-medium text-emerald-400">ACTIVE</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-black/50 border border-white/5 rounded-sm px-4 py-3 font-mono text-sm text-zinc-300 flex justify-between items-center">
                  <span>{apiKeyVisible ? 'pk_live_8392xk29d8f7g3h2j4k5l6m7n8p9q0r1s2t3u4v5w6x7y8z9d2a' : 'pk_live_••••••••••••••••••••••••••••••••••••••••••••'}</span>
                </div>
                <button 
                  onClick={() => handleCopy('pk_live_8392xk29d8f7g3h2j4k5l6m7n8p9q0r1s2t3u4v5w6x7y8z9d2a', 'live')}
                  className="p-3 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-white/5" 
                  title="Copy Key"
                >
                  {copied === 'live' ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
                </button>
                <button 
                  onClick={() => setApiKeyVisible(!apiKeyVisible)}
                  className="p-3 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-white/5" 
                  title={apiKeyVisible ? 'Hide Key' : 'Show Key'}
                >
                  <i data-lucide={apiKeyVisible ? 'eye-off' : 'eye'} className="w-4 h-4"></i>
                </button>
              </div>
            </div>
            
            <div className="px-6 py-4 bg-white/[0.01] flex items-center justify-between">
              <div className="text-xs text-zinc-500">
                Created: Dec 1, 2025 • Last used: Just now
              </div>
              <button className="text-xs text-red-400 hover:text-red-300 transition-colors">
                Regenerate Key
              </button>
            </div>
          </div>

          {/* Test API Key */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-500/10 rounded-sm border border-orange-500/20">
                    <i data-lucide="flask-conical" className="w-4 h-4 text-orange-400"></i>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-white">Test API Key</h3>
                    <p className="text-xs text-zinc-500">Use this key for development and testing</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-orange-500/10 border border-orange-500/20 rounded-full text-[10px] font-medium text-orange-400">TEST MODE</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-black/50 border border-white/5 rounded-sm px-4 py-3 font-mono text-sm text-zinc-300 flex justify-between items-center">
                  <span>{testKeyVisible ? 'pk_test_9x8w7v6u5t4s3r2q1p0o9n8m7l6k5j4i3h2g1f0e9d8c7b6a5' : 'pk_test_••••••••••••••••••••••••••••••••••••••••••••'}</span>
                </div>
                <button 
                  onClick={() => handleCopy('pk_test_9x8w7v6u5t4s3r2q1p0o9n8m7l6k5j4i3h2g1f0e9d8c7b6a5', 'test')}
                  className="p-3 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-white/5" 
                  title="Copy Key"
                >
                  {copied === 'test' ? <i data-lucide="check" className="w-4 h-4 text-emerald-400"></i> : <i data-lucide="copy" className="w-4 h-4"></i>}
                </button>
                <button 
                  onClick={() => setTestKeyVisible(!testKeyVisible)}
                  className="p-3 hover:bg-white/10 rounded-sm text-zinc-400 hover:text-white transition-colors border border-white/5" 
                  title={testKeyVisible ? 'Hide Key' : 'Show Key'}
                >
                  <i data-lucide={testKeyVisible ? 'eye-off' : 'eye'} className="w-4 h-4"></i>
                </button>
              </div>
            </div>
            
            <div className="px-6 py-4 bg-white/[0.01] flex items-center justify-between">
              <div className="text-xs text-zinc-500">
                Created: Dec 1, 2025 • Last used: 2 hours ago
              </div>
              <button className="text-xs text-red-400 hover:text-red-300 transition-colors">
                Regenerate Key
              </button>
            </div>
          </div>

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
                Regenerate your keys immediately if you suspect they&apos;ve been compromised
              </li>
              <li className="flex items-start gap-2">
                <i data-lucide="check" className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0"></i>
                Use test keys during development to avoid affecting production data
              </li>
            </ul>
          </div>

          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link>
          </div>

        </div>
      </div>
    </>
  );
}

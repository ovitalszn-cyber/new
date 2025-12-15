'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useSession } from 'next-auth/react';

export default function BillingPage() {
  const { data: session } = useSession();
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

  return (
    <>
      {/* Header */}
      <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="flex items-center gap-4">
          <nav className="flex items-center text-sm font-medium text-zinc-500">
            <span className="hover:text-zinc-300 transition-colors cursor-pointer">{userName}</span>
            <span className="mx-2 text-zinc-700">/</span>
            <span className="text-white">Billing</span>
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
              <h1 className="text-2xl font-semibold tracking-tight text-white mb-1">Billing</h1>
              <p className="text-sm text-zinc-500">Manage your subscription and payment methods.</p>
            </div>
            <a href="/#pricing" className="px-4 py-2 bg-white text-black text-sm font-medium rounded-sm hover:bg-zinc-200 transition-colors">
              Upgrade Plan
            </a>
          </div>

          {/* Current Plan */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white/5 rounded-sm border border-white/5">
                    <i data-lucide="package" className="w-6 h-6 text-white"></i>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-white">Starter Plan</h3>
                    <p className="text-sm text-zinc-500">100,000 requests/month</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-semibold text-white">$49<span className="text-sm text-zinc-500 font-normal">/mo</span></div>
                  <div className="text-xs text-zinc-500">Billed monthly</div>
                </div>
              </div>
            </div>
            
            <div className="p-6 bg-white/[0.01]">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-zinc-400">Current usage</span>
                <span className="text-sm text-white">42,593 / 100,000 requests</span>
              </div>
              <div className="w-full bg-zinc-800 rounded-full h-2">
                <div className="bg-white h-2 rounded-full" style={{ width: '42.5%' }}></div>
              </div>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-zinc-500">Resets in 16 days</span>
                <span className="text-xs text-zinc-500">42.5% used</span>
              </div>
            </div>
          </div>

          {/* Payment Method */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-sm font-medium text-white mb-4">Payment Method</h3>
              <div className="flex items-center justify-between p-4 bg-black/30 border border-white/5 rounded-sm">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/10 rounded border border-blue-500/20">
                    <i data-lucide="credit-card" className="w-5 h-5 text-blue-400"></i>
                  </div>
                  <div>
                    <div className="text-sm text-white">•••• •••• •••• 4242</div>
                    <div className="text-xs text-zinc-500">Expires 12/2026</div>
                  </div>
                </div>
                <button className="text-xs text-zinc-400 hover:text-white transition-colors">
                  Update
                </button>
              </div>
            </div>
            
            <div className="px-6 py-4 bg-white/[0.01] flex items-center justify-between">
              <span className="text-xs text-zinc-500">Next billing date: January 1, 2026</span>
              <button className="text-xs text-red-400 hover:text-red-300 transition-colors">
                Cancel Subscription
              </button>
            </div>
          </div>

          {/* Billing History */}
          <div className="bg-[#0C0D0F] border border-white/5 rounded-sm overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-sm font-medium text-white">Billing History</h3>
            </div>
            
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.02] border-b border-white/5">
                <tr>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">Amount</th>
                  <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase tracking-wider text-right">Invoice</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 text-zinc-300">Dec 1, 2025</td>
                  <td className="px-6 py-4 text-zinc-400">Starter Plan - Monthly</td>
                  <td className="px-6 py-4 text-white">$49.00</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-xs text-zinc-400 hover:text-white transition-colors flex items-center gap-1 ml-auto">
                      <i data-lucide="download" className="w-3 h-3"></i> PDF
                    </button>
                  </td>
                </tr>
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 text-zinc-300">Nov 1, 2025</td>
                  <td className="px-6 py-4 text-zinc-400">Starter Plan - Monthly</td>
                  <td className="px-6 py-4 text-white">$49.00</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-xs text-zinc-400 hover:text-white transition-colors flex items-center gap-1 ml-auto">
                      <i data-lucide="download" className="w-3 h-3"></i> PDF
                    </button>
                  </td>
                </tr>
                <tr className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-6 py-4 text-zinc-300">Oct 1, 2025</td>
                  <td className="px-6 py-4 text-zinc-400">Starter Plan - Monthly</td>
                  <td className="px-6 py-4 text-white">$49.00</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-xs text-zinc-400 hover:text-white transition-colors flex items-center gap-1 ml-auto">
                      <i data-lucide="download" className="w-3 h-3"></i> PDF
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="text-center text-xs text-zinc-600 pb-8">
            © 2025 KashRock Inc. • <Link href="/legal" className="hover:text-zinc-400">Privacy</Link> • <Link href="/legal?tab=terms" className="hover:text-zinc-400">Terms</Link> • <Link href="/legal?tab=refunds" className="hover:text-zinc-400">Refund Policy</Link>
          </div>

        </div>
      </div>
    </>
  );
}

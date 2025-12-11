'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';

interface AffiliateLink {
  id: string;
  name: string;
  url: string;
  clicks: number;
  signups: number;
  commissions: number;
  conversionRate: number;
  createdAt: string;
  status: 'ACTIVE' | 'PAUSED' | 'EXPIRED';
}

export default function AffiliatePage() {
  const [links, setLinks] = useState<AffiliateLink[]>([
    {
      id: '1',
      name: 'Blog Sidebar Banner',
      url: 'https://kashrock.com?ref=blog-sidebar',
      clicks: 1247,
      signups: 23,
      commissions: 345.67,
      conversionRate: 1.84,
      createdAt: '2025-01-01',
      status: 'ACTIVE',
    },
    {
      id: '2',
      name: 'Twitter Bio Link',
      url: 'https://kashrock.com?ref=twitter-bio',
      clicks: 892,
      signups: 15,
      commissions: 225.00,
      conversionRate: 1.68,
      createdAt: '2025-01-05',
      status: 'ACTIVE',
    },
    {
      id: '3',
      name: 'YouTube Description',
      url: 'https://kashrock.com?ref=youtube-desc',
      clicks: 423,
      signups: 8,
      commissions: 120.00,
      conversionRate: 1.89,
      createdAt: '2025-01-10',
      status: 'PAUSED',
    },
  ]);

  const [showNewLinkModal, setShowNewLinkModal] = useState(false);
  const [newLinkName, setNewLinkName] = useState('');
  const [copied, setCopied] = useState<string | null>(null);

  // Mock stats
  const stats = {
    totalClicks: 2562,
    totalSignups: 46,
    totalCommissions: 690.67,
    avgConversionRate: 1.79,
    pendingPayout: 230.45,
  };

  const generateLink = () => {
    const refCode = Math.random().toString(36).substring(2, 8);
    const newLink: AffiliateLink = {
      id: String(links.length + 1),
      name: newLinkName || 'New Affiliate Link',
      url: `https://kashrock.com?ref=${refCode}`,
      clicks: 0,
      signups: 0,
      commissions: 0,
      conversionRate: 0,
      createdAt: new Date().toISOString().split('T')[0],
      status: 'ACTIVE',
    };
    setLinks([...links, newLink]);
    setNewLinkName('');
    setShowNewLinkModal(false);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const toggleLinkStatus = (id: string) => {
    setLinks(links.map(link => 
      link.id === id 
        ? { ...link, status: link.status === 'ACTIVE' ? 'PAUSED' : 'ACTIVE' }
        : link
    ));
  };

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 
          className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Affiliate Marketing
        </h1>
        <p className="text-[#635F69]">
          Track your affiliate links, clicks, and commissions.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Total Clicks</p>
          <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {stats.totalClicks.toLocaleString()}
          </p>
        </div>
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Total Signups</p>
          <p className="text-2xl font-black text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {stats.totalSignups}
          </p>
        </div>
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Total Commissions</p>
          <p className="text-2xl font-black text-[#10B981]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            ${stats.totalCommissions.toFixed(2)}
          </p>
        </div>
        <div className="clay-card shadow-clay-card p-6">
          <p className="text-sm text-[#635F69] mb-1">Pending Payout</p>
          <p className="text-2xl font-black text-[#F59E0B]" style={{ fontFamily: 'Nunito, sans-serif' }}>
            ${stats.pendingPayout.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Generate New Link Button */}
      <div className="mb-8">
        <button
          onClick={() => setShowNewLinkModal(true)}
          className="h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.92] transition-all duration-200 flex items-center gap-2"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Generate New Link
        </button>
      </div>

      {/* Links Table */}
      {links.length === 0 ? (
        <div className="clay-card shadow-clay-card p-12 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#7C3AED]/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-[#7C3AED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
            No affiliate links yet
          </h3>
          <p className="text-[#635F69]">
            Click "Generate New Link" to create your first affiliate link!
          </p>
        </div>
      ) : (
        <div className="clay-card shadow-clay-card p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#E5E1EF]">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Link Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">URL</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Clicks</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Signups</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Commission</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Conv. Rate</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-[#635F69]">Actions</th>
                </tr>
              </thead>
              <tbody>
                {links.map((link) => (
                  <tr key={link.id} className="border-b border-[#E5E1EF]/50 hover:bg-[#7C3AED]/5 transition-colors">
                    <td className="py-4 px-4">
                      <div>
                        <p className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
                          {link.name}
                        </p>
                        <p className="text-xs text-[#635F69]">Created {link.createdAt}</p>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <code className="text-sm text-[#7C3AED] font-mono truncate max-w-[200px]">
                          {link.url}
                        </code>
                        <button
                          onClick={() => copyToClipboard(link.url, link.id)}
                          className={`p-2 rounded-lg text-xs font-bold transition-all ${
                            copied === link.id
                              ? 'bg-[#10B981] text-white'
                              : 'bg-[#7C3AED]/10 text-[#7C3AED] hover:bg-[#7C3AED]/20'
                          }`}
                        >
                          {copied === link.id ? 'Copied!' : 'Copy'}
                        </button>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-[#635F69] font-medium">
                      {link.clicks.toLocaleString()}
                    </td>
                    <td className="py-4 px-4 text-[#635F69] font-medium">
                      {link.signups}
                    </td>
                    <td className="py-4 px-4 text-[#10B981] font-medium">
                      ${link.commissions.toFixed(2)}
                    </td>
                    <td className="py-4 px-4 text-[#635F69] font-medium">
                      {link.conversionRate.toFixed(2)}%
                    </td>
                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                        link.status === 'ACTIVE' 
                          ? 'bg-[#10B981]/10 text-[#10B981]'
                          : link.status === 'PAUSED'
                          ? 'bg-[#F59E0B]/10 text-[#F59E0B]'
                          : 'bg-[#EF4444]/10 text-[#EF4444]'
                      }`}>
                        {link.status}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => toggleLinkStatus(link.id)}
                          className={`p-2 rounded-lg text-xs font-bold transition-all ${
                            link.status === 'ACTIVE'
                              ? 'bg-[#F59E0B]/10 text-[#F59E0B] hover:bg-[#F59E0B]/20'
                              : 'bg-[#10B981]/10 text-[#10B981] hover:bg-[#10B981]/20'
                          }`}
                        >
                          {link.status === 'ACTIVE' ? 'Pause' : 'Activate'}
                        </button>
                        <button className="p-2 rounded-lg bg-[#EF4444]/10 text-[#EF4444] text-xs font-bold hover:bg-[#EF4444]/20 transition-all">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Generate Link Modal */}
      {showNewLinkModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-sm">
          <div className="clay-card shadow-clay-surface p-8 max-w-md w-full">
            <h2 className="text-2xl font-black text-[#332F3A] mb-4" style={{ fontFamily: 'Nunito, sans-serif' }}>
              Generate New Link
            </h2>
            <p className="text-[#635F69] mb-6">
              Give your affiliate link a name to help you track its performance.
            </p>
            <input
              type="text"
              value={newLinkName}
              onChange={(e) => setNewLinkName(e.target.value)}
              placeholder="e.g., Blog Sidebar Banner"
              className="w-full h-14 px-5 rounded-[16px] bg-[#EFEBF5] shadow-clay-pressed text-[#332F3A] placeholder-[#635F69]/50 font-medium focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all mb-6"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowNewLinkModal(false)}
                className="flex-1 h-12 rounded-[20px] bg-white text-[#635F69] font-bold shadow-clay-card hover:shadow-clay-card-hover transition-all"
              >
                Cancel
              </button>
              <button
                onClick={generateLink}
                className="flex-1 h-12 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all"
              >
                Generate Link
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

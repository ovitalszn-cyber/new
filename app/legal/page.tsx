'use client';

import Script from 'next/script';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

export default function LegalPage() {
  const searchParams = useSearchParams();
  const [activePage, setActivePage] = useState<'privacy' | 'terms' | 'refunds'>('privacy');

  useEffect(() => {
    // Check URL param for tab
    const tab = searchParams.get('tab');
    if (tab === 'terms') {
      setActivePage('terms');
    } else if (tab === 'refunds') {
      setActivePage('refunds');
    }
  }, [searchParams]);

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
      <Script src="https://unpkg.com/lucide@latest" strategy="beforeInteractive" />
      
      <div className="antialiased selection:bg-white/20 selection:text-white h-screen flex overflow-hidden" style={{ 
        fontFamily: 'Inter, sans-serif',
        backgroundColor: '#08090A',
        color: '#E3E5E7'
      }}>
        <style jsx global>{`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
          
          body { font-family: 'Inter', sans-serif; background-color: #08090A; color: #E3E5E7; }
          
          ::-webkit-scrollbar { width: 6px; height: 6px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
          ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

          .prose-content h2 { margin-top: 2.5rem; margin-bottom: 1rem; }
          .prose-content h3 { margin-top: 2rem; margin-bottom: 0.75rem; }
          .prose-content p { margin-bottom: 1.25rem; line-height: 1.7; }
          .prose-content ul { margin-bottom: 1.25rem; list-style-type: disc; padding-left: 1.5rem; }
          .prose-content li { margin-bottom: 0.5rem; }
        `}</style>

        {/* Sidebar */}
        <aside className="w-64 border-r border-white/5 bg-[#050505] flex flex-col justify-between shrink-0 transition-all duration-300">
          <div>
            {/* Logo Area */}
            <div className="h-16 flex items-center px-6 border-b border-white/5">
              <Link href="/" className="flex items-center gap-2.5">
                <img src="/kashrock-logo.svg" alt="KashRock" className="h-6 w-auto" />
              </Link>
            </div>

            {/* Navigation */}
            <div className="p-3 space-y-1">
              <Link href="/console" className="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02] text-sm font-medium rounded-sm transition-all group">
                <i data-lucide="layout-grid" className="w-4 h-4 text-zinc-500 group-hover:text-zinc-300 transition-colors"></i>
                Overview
              </Link>
              
              <div className="h-px bg-white/5 my-2 mx-3"></div>
              
              <div className="px-3 py-2 text-xs font-medium text-zinc-500 uppercase tracking-wider">Legal</div>
              
              <button 
                onClick={() => setActivePage('privacy')} 
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm transition-all group ${
                  activePage === 'privacy' 
                    ? 'bg-white/5 text-white border border-white/5' 
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02]'
                }`}
              >
                <i data-lucide="shield" className={`w-4 h-4 ${activePage === 'privacy' ? 'text-white' : 'text-zinc-500 group-hover:text-zinc-300'} transition-colors`}></i>
                Privacy Policy
              </button>
              
              <button 
                onClick={() => setActivePage('terms')} 
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm transition-all group ${
                  activePage === 'terms' 
                    ? 'bg-white/5 text-white border border-white/5' 
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02]'
                }`}
              >
                <i data-lucide="file-text" className={`w-4 h-4 ${activePage === 'terms' ? 'text-white' : 'text-zinc-500 group-hover:text-zinc-300'} transition-colors`}></i>
                Terms of Service
              </button>
              
              <button 
                onClick={() => setActivePage('refunds')} 
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm transition-all group ${
                  activePage === 'refunds' 
                    ? 'bg-white/5 text-white border border-white/5' 
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02]'
                }`}
              >
                <i data-lucide="credit-card" className={`w-4 h-4 ${activePage === 'refunds' ? 'text-white' : 'text-zinc-500 group-hover:text-zinc-300'} transition-colors`}></i>
                No Refunds Policy
              </button>
            </div>
          </div>

          {/* Bottom Links */}
          <div className="p-3 border-t border-white/5">
            <Link href="/console" className="flex items-center gap-3 px-3 py-2 text-zinc-500 hover:text-zinc-300 text-sm font-medium rounded-sm transition-all">
              <i data-lucide="arrow-left" className="w-4 h-4"></i>
              Back to Dashboard
            </Link>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#08090A]">
          
          {/* Header */}
          <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#08090A]/80 backdrop-blur-sm sticky top-0 z-20">
            <div className="flex items-center gap-4">
              <nav className="flex items-center text-sm font-medium text-zinc-500">
                <Link href="/" className="hover:text-zinc-300 transition-colors cursor-pointer">KashRock</Link>
                <span className="mx-2 text-zinc-700">/</span>
                <span className="text-white">{activePage === 'privacy' ? 'Privacy Policy' : activePage === 'terms' ? 'Terms of Service' : 'No Refunds Policy'}</span>
              </nav>
            </div>
            <div className="text-xs text-zinc-500">
              Last updated: December 15, 2025
            </div>
          </header>

          {/* Document Scroll Area */}
          <div className="flex-1 overflow-y-auto p-8 lg:p-12">
            <div className="max-w-3xl mx-auto">
              
              {/* Privacy Policy Content */}
              {activePage === 'privacy' && (
                <article className="prose-content text-zinc-400 text-sm animate-fade-in">
                  <h1 className="text-3xl font-semibold tracking-tight text-white mb-8">Privacy Policy</h1>
                  
                  <p className="text-base text-zinc-300 leading-relaxed">
                    At KashRock, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website or use our API services. Please read this privacy policy carefully.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">1. Information We Collect</h2>
                  <p>
                    We collect information that identifies, relates to, describes, references, is capable of being associated with, or could reasonably be linked, directly or indirectly, with a particular consumer or device (&quot;personal information&quot;).
                  </p>
                  <ul className="list-disc pl-5 space-y-1">
                    <li><strong className="text-zinc-300">Account Information:</strong> We collect your name, email address, and password when you register for an account.</li>
                    <li><strong className="text-zinc-300">API Usage Data:</strong> We automatically log information about your API requests, including timestamps, IP addresses, and endpoint usage to monitor rate limits and performance.</li>
                    <li><strong className="text-zinc-300">Payment Information:</strong> We use third-party payment processors (Stripe) and do not store full credit card details on our servers.</li>
                  </ul>

                  <h2 className="text-lg font-medium text-white tracking-tight">2. How We Use Your Information</h2>
                  <p>
                    We use the information we collect for various purposes, including to:
                  </p>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Provide, operate, and maintain our services.</li>
                    <li>Improve, personalize, and expand our API offerings.</li>
                    <li>Understand and analyze how you use our services.</li>
                    <li>Develop new products, services, features, and functionality.</li>
                    <li>Communicate with you regarding updates, security alerts, and support messages.</li>
                  </ul>

                  <h2 className="text-lg font-medium text-white tracking-tight">3. Data Retention</h2>
                  <p>
                    We will retain your personal information only for as long as is necessary for the purposes set out in this Privacy Policy. We will retain and use your information to the extent necessary to comply with our legal obligations, resolve disputes, and enforce our policies. Logs of API usage are generally retained for 30 days before being aggregated or deleted.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">4. Security of Your Data</h2>
                  <p>
                    The security of your data is important to us, but remember that no method of transmission over the Internet, or method of electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your Personal Data, we cannot guarantee its absolute security. We employ industry-standard encryption (TLS 1.2+) for all data in transit.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">5. Contact Us</h2>
                  <p>
                    If you have any questions about this Privacy Policy, you can contact us:
                  </p>
                  <div className="mt-4 p-4 bg-white/[0.02] rounded-sm border border-white/5 inline-block">
                    <p className="mb-0 text-zinc-300">By email: <a href="mailto:privacy@kashrock.com" className="text-white hover:underline">privacy@kashrock.com</a></p>
                  </div>
                </article>
              )}

              {/* Terms of Service Content */}
              {activePage === 'terms' && (
                <article className="prose-content text-zinc-400 text-sm animate-fade-in">
                  <h1 className="text-3xl font-semibold tracking-tight text-white mb-8">Terms of Service</h1>
                  
                  <p className="text-base text-zinc-300 leading-relaxed">
                    Please read these Terms of Service (&quot;Terms&quot;, &quot;Terms of Service&quot;) carefully before using the KashRock API operated by KashRock Inc. (&quot;us&quot;, &quot;we&quot;, or &quot;our&quot;). Your access to and use of the Service is conditioned on your acceptance of and compliance with these Terms.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">1. API Usage &amp; Limits</h2>
                  <p>
                    We grant you a limited, non-exclusive, non-transferable, revocable license to use our API.
                  </p>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service without express written permission by us.</li>
                    <li>You must respect the rate limits associated with your subscription plan. Excessive requests may result in temporary or permanent suspension of your API key.</li>
                    <li>You are responsible for maintaining the security of your API keys.</li>
                  </ul>

                  <h2 className="text-lg font-medium text-white tracking-tight">2. Intellectual Property</h2>
                  <p>
                    The Service and its original content (excluding Content provided by users), features and functionality are and will remain the exclusive property of KashRock Inc. and its licensors. The Service is protected by copyright, trademark, and other laws of both the United States and foreign countries.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">3. Termination</h2>
                  <p>
                    We may terminate or suspend access to our Service immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms. All provisions of the Terms which by their nature should survive termination shall survive termination, including, without limitation, ownership provisions, warranty disclaimers, indemnity and limitations of liability.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">4. Disclaimer</h2>
                  <p>
                    Your use of the Service is at your sole risk. The Service is provided on an &quot;AS IS&quot; and &quot;AS AVAILABLE&quot; basis. The Service is provided without warranties of any kind, whether express or implied, including, but not limited to, implied warranties of merchantability, fitness for a particular purpose, non-infringement or course of performance.
                  </p>
                  <p>
                    KashRock Inc. does not warrant that a) the Service will function uninterrupted, secure or available at any particular time or location; b) any errors or defects will be corrected; c) the Service is free of viruses or other harmful components; or d) the results of using the Service will meet your requirements.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">5. Changes</h2>
                  <p>
                    We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material we will try to provide at least 30 days notice prior to any new terms taking effect. What constitutes a material change will be determined at our sole discretion.
                  </p>
                </article>
              )}

              {/* No Refunds Policy Content */}
              {activePage === 'refunds' && (
                <article className="prose-content text-zinc-400 text-sm animate-fade-in">
                  <h1 className="text-3xl font-semibold tracking-tight text-white mb-8">No Refunds Policy</h1>
                  
                  <p className="text-base text-zinc-300 leading-relaxed">
                    KashRock provides subscription access to API services that may be used immediately upon purchase. For this reason, all payments are final except in the limited cases listed below.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">Monthly Subscriptions</h2>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Monthly subscription payments are non-refundable.</li>
                    <li>You may cancel at any time, and your plan will remain active until the end of your current billing period.</li>
                    <li>We do not provide refunds or credits for unused time, unused requests, partial months, downgrades, or cancellations.</li>
                  </ul>

                  <h2 className="text-lg font-medium text-white tracking-tight">Exceptions (Limited)</h2>
                  <p>
                    We may issue a refund or reversal only for:
                  </p>
                  <ul className="list-disc pl-5 space-y-1">
                    <li><strong className="text-zinc-300">Duplicate charges</strong></li>
                    <li><strong className="text-zinc-300">Billing errors</strong> (incorrect amount charged due to a technical issue)</li>
                    <li><strong className="text-zinc-300">Unauthorized charges</strong> (subject to investigation and account security requirements)</li>
                  </ul>
                  <p>
                    If an exception applies, our remedy may be a refund, credit, or correction, at our discretion.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">How to Request a Billing Review</h2>
                  <p>
                    Email: <a href="mailto:support@kashrock.com" className="text-white hover:underline">support@kashrock.com</a>
                  </p>
                  <p>Include:</p>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>The account email</li>
                    <li>The charge date and amount</li>
                    <li>The last 4 digits of the payment method (if available)</li>
                    <li>A brief description of the issue</li>
                  </ul>

                  <h2 className="text-lg font-medium text-white tracking-tight">Chargebacks</h2>
                  <p>
                    If you believe a charge is incorrect, contact us first. Filing a chargeback may result in immediate suspension of API access for the associated account while the dispute is reviewed.
                  </p>

                  <h2 className="text-lg font-medium text-white tracking-tight">Updates to This Policy</h2>
                  <p>
                    We may update this policy from time to time. The latest version will always be posted on this page with the effective date above.
                  </p>
                </article>
              )}

              {/* Footer area inside content */}
              <div className="mt-16 pt-8 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center text-xs text-zinc-600">
                <div>© 2025 KashRock Inc. All rights reserved.</div>
                <div className="flex gap-4 mt-2 sm:mt-0">
                  <Link href="/support" className="hover:text-zinc-400 transition-colors">Support</Link>
                  <Link href="/" className="hover:text-zinc-400 transition-colors">Home</Link>
                </div>
              </div>

            </div>
          </div>
        </main>
      </div>
    </>
  );
}

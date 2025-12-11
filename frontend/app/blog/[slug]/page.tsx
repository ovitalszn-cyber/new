'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  content: string;
  date: string;
  readTime: string;
  category: string;
  author: {
    name: string;
    avatar?: string;
  };
}

// Blog posts data
const blogPosts: Record<string, BlogPost> = {
  'why-builders-need-faster-sports-data': {
    slug: 'why-builders-need-faster-sports-data',
    title: 'Why Builders Need Faster Access to Sports Data (And What We\'re Fixing at KashRock)',
    excerpt: 'Sports data is messy. Anyone who has ever tried building a prediction model, odds scraper, or betting tool knows the pain. That\'s the exact problem KashRock is solving.',
    content: `
Sports data is messy. Anyone who has ever tried building a prediction model, odds scraper, or betting tool knows the pain:

- inconsistent formats across sportsbooks
- slow endpoints
- rate limits
- missing historical stats
- player props scattered everywhere
- and zero tools built for actual developers

Most APIs today weren't designed for people building at speed. They were designed for sportsbooks — not independent developers, model builders, or founders trying to ship.

That's the exact problem KashRock is solving.

## What we're building

KashRock is a sports data engine built for builders, not enterprises.

Our goal is simple: **Make sports data fast, complete, normalized, and easy to use.**

From one place, you'll be able to access:

- live odds
- historical odds
- player props
- team stats
- game metadata
- US + EU books
- export tools
- normalized formats
- and long-term — your own models on top of our data

No more stitching 15 sources together. No more cleaning data for hours before you can even build.

## Why the waitlist matters

We launched the waitlist before the full product because we needed one thing:

**Direction from real users, not assumptions.**

Within the first wave of signups, we learned:

- builders want historical data exportable
- they need cleaned/normalized formats
- they hate rate limits
- they want player props and live odds in the same feed
- they want an affordable alternative to enterprise APIs

This feedback is shaping the MVP.

## What's next

As we finish testing, early users will receive:

- discounted pricing (up to 75% off)
- access to the export engine
- early documentation
- API keys for the first version

KashRock was built for the people who actually build things — the developers and founders shaping the future of sports tech.

If that's you, join the waitlist.
    `,
    date: '2025-01-15',
    readTime: '4 min read',
    category: 'Announcements',
    author: { name: 'KashRock Team' },
  },
  'why-your-sports-betting-app-needs-realtime-odds': {
    slug: 'why-your-sports-betting-app-needs-realtime-odds',
    title: 'Why Your Sports Betting App Needs a Real-Time Odds Backbone',
    excerpt: 'The sports betting market is exploding, but most new apps still struggle with the same problem: unreliable data pipelines. You need an infrastructure-level backbone, not a spreadsheet of scripts.',
    content: `
## 1. Real-time odds matter more than features

Every UX improvement, every fancy chart, every parlay builder collapses the moment your odds lag behind competitors. Users will trust the source with the freshest and most accurate lines. If you're off by 30–60 seconds, you lose.

## 2. Scraping breaks at scale

When five people scrape a site, it's fine. When 5,000 do it, the whole system collapses. Captchas. Rate limits. IP bans. Unreliable latency.

It's not sustainable.

**You need a clean, push-based feed with millisecond delivery.**

## 3. Developers need time to build, not fight blockers

The future of sports betting is not owned by sportsbooks. It's owned by builders—the indie devs creating tools, analytics platforms, prediction engines, and automation.

Those devs shouldn't waste time building infrastructure. They should build the product on top of it.

## 4. The betting market rewards speed

- The fastest data wins.
- The richest datasets win.
- The most developer-friendly APIs win.

That's why the backbone matters. That's why you need an infrastructure layer—not a patchwork of scrapers.
    `,
    date: '2025-01-12',
    readTime: '3 min read',
    category: 'Engineering',
    author: { name: 'KashRock Team' },
  },
  'how-to-build-sports-data-startup': {
    slug: 'how-to-build-sports-data-startup',
    title: 'How To Build a Sports Data Startup Without Spending Millions',
    excerpt: 'Everyone thinks you need a massive engineering team, enterprise data providers, and a giant budget to enter the sports data industry. You don\'t. What you need is leverage.',
    content: `
## 1. Start with one sport and one feature

Most startups fail because they try to launch everything at once. Start with:

- NFL live odds
- NBA shot charts
- UFC fighter stats
- NCAA historical data

Pick one lane and dominate it.

## 2. Use a third-party data backbone instead of building from scratch

Building scrapers, rate-limit handlers, massive historical archives, real-time pipelines, and database scaling is a full-time job.

Instead, use an existing data backbone so your time goes toward product, not pipes.

## 3. Your real moat is UX and insights

Two companies can have the same data. Only one will package it in a way the user actually loves.

Your job is not collecting data. **Your job is turning it into something useful, fast, and easy to build with.**

## 4. Monetize early with developers

The fastest path to revenue:

- Sell API access
- Sell historical datasets
- Sell models
- Sell tools for devs to plug in

You don't need a million customers. You need 100 devs building on your platform.

## 5. Scale only when the usage demands it

Infrastructure is expensive when it's premature. Wait until you have:

- consistent traffic
- customers using your API
- builders asking for more

Then scale.

**Building smart beats building big.**
    `,
    date: '2025-01-08',
    readTime: '4 min read',
    category: 'Guides',
    author: { name: 'KashRock Team' },
  },
};

export default function BlogPostPage() {
  const params = useParams();
  const slug = params.slug as string;
  const post = blogPosts[slug];
  const [copied, setCopied] = useState<string | null>(null);

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  if (!post) {
    return (
      <div className="min-h-screen bg-[#F4F1FA] flex items-center justify-center">
        <div className="clay-card shadow-clay-card p-12 text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#EF4444]/10 flex items-center justify-center">
            <svg className="w-8 h-8 text-[#EF4444]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
            Post Not Found
          </h1>
          <p className="text-[#635F69] mb-6">
            The blog post you&apos;re looking for doesn&apos;t exist.
          </p>
          <Link
            href="/blog"
            className="inline-flex h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover transition-all items-center"
          >
            Back to Blog
          </Link>
        </div>
      </div>
    );
  }

  // Simple markdown-like rendering
  const renderContent = (content: string) => {
    const lines = content.trim().split('\n');
    const elements: React.ReactElement[] = [];
    let inCodeBlock = false;
    let codeContent = '';
    let codeLanguage = '';
    let codeBlockId = 0;

    lines.forEach((line, index) => {
      // Code block start/end
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          // End code block
          const currentId = `code-${codeBlockId++}`;
          const code = codeContent.trim();
          elements.push(
            <div key={index} className="relative my-6 group">
              <pre className="p-4 rounded-2xl bg-[#1e1e2e] text-sm font-mono text-[#E5E1EF] overflow-x-auto">
                <code>{code}</code>
              </pre>
              <button
                onClick={() => copyCode(code, currentId)}
                className={`absolute top-3 right-3 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  copied === currentId
                    ? 'bg-[#10B981] text-white'
                    : 'bg-[#7C3AED]/20 text-[#A78BFA] hover:bg-[#7C3AED]/30'
                }`}
              >
                {copied === currentId ? 'Copied!' : 'Copy'}
              </button>
            </div>
          );
          codeContent = '';
          inCodeBlock = false;
        } else {
          // Start code block
          codeLanguage = line.slice(3);
          inCodeBlock = true;
        }
        return;
      }

      if (inCodeBlock) {
        codeContent += line + '\n';
        return;
      }

      // Headers
      if (line.startsWith('# ')) {
        elements.push(
          <h1 key={index} className="text-3xl sm:text-4xl font-black text-[#332F3A] mb-6 mt-8" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {line.slice(2)}
          </h1>
        );
      } else if (line.startsWith('## ')) {
        elements.push(
          <h2 key={index} className="text-2xl font-bold text-[#332F3A] mb-4 mt-8" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {line.slice(3)}
          </h2>
        );
      } else if (line.startsWith('### ')) {
        elements.push(
          <h3 key={index} className="text-xl font-bold text-[#332F3A] mb-3 mt-6" style={{ fontFamily: 'Nunito, sans-serif' }}>
            {line.slice(4)}
          </h3>
        );
      } else if (line.startsWith('- ')) {
        // List item
        elements.push(
          <li key={index} className="text-[#635F69] ml-4 mb-2 flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#7C3AED] mt-2 flex-shrink-0" />
            <span>{renderInlineElements(line.slice(2))}</span>
          </li>
        );
      } else if (line.match(/^\d+\. /)) {
        // Numbered list
        const match = line.match(/^(\d+)\. (.*)$/);
        if (match) {
          elements.push(
            <li key={index} className="text-[#635F69] ml-4 mb-2 flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-[#7C3AED] text-white text-xs font-bold flex items-center justify-center flex-shrink-0">
                {match[1]}
              </span>
              <span>{renderInlineElements(match[2])}</span>
            </li>
          );
        }
      } else if (line.trim() === '') {
        // Empty line
        elements.push(<div key={index} className="h-4" />);
      } else {
        // Paragraph
        elements.push(
          <p key={index} className="text-[#635F69] leading-relaxed mb-4">
            {renderInlineElements(line)}
          </p>
        );
      }
    });

    return elements;
  };

  // Render inline elements like bold, code, links
  const renderInlineElements = (text: string) => {
    // Handle inline code
    const parts = text.split(/(`[^`]+`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="px-1.5 py-0.5 rounded bg-[#7C3AED]/10 text-[#7C3AED] text-sm font-mono">
            {part.slice(1, -1)}
          </code>
        );
      }
      // Handle bold
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((bp, j) => {
        if (bp.startsWith('**') && bp.endsWith('**')) {
          return <strong key={`${i}-${j}`} className="font-bold text-[#332F3A]">{bp.slice(2, -2)}</strong>;
        }
        // Handle links
        const linkMatch = bp.match(/\[([^\]]+)\]\(([^)]+)\)/);
        if (linkMatch) {
          const before = bp.slice(0, linkMatch.index);
          const after = bp.slice((linkMatch.index || 0) + linkMatch[0].length);
          return (
            <span key={`${i}-${j}`}>
              {before}
              <Link href={linkMatch[2]} className="text-[#7C3AED] hover:underline font-medium">
                {linkMatch[1]}
              </Link>
              {after}
            </span>
          );
        }
        return bp;
      });
    });
  };

  return (
    <div className="min-h-screen bg-[#F4F1FA]">
      {/* Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 px-6 py-4">
        <div className="clay-card shadow-clay-card h-16 px-6 flex items-center justify-between max-w-6xl mx-auto">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] shadow-clay-orb flex items-center justify-center">
              <span className="text-white font-black text-xl" style={{ fontFamily: 'Nunito, sans-serif' }}>K</span>
            </div>
            <span className="font-bold text-lg text-[#332F3A] hidden sm:block" style={{ fontFamily: 'Nunito, sans-serif' }}>
              KashRock
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-[#635F69] hover:text-[#7C3AED] font-medium transition-colors">
              Home
            </Link>
            <Link href="/blog" className="text-[#7C3AED] font-medium">
              Blog
            </Link>
            <Link href="/docs" className="text-[#635F69] hover:text-[#7C3AED] font-medium transition-colors">
              Docs
            </Link>
          </nav>

          <Link
            href="/dashboard"
            className="h-10 px-5 rounded-[16px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold text-sm shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-0.5 transition-all flex items-center"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            Dashboard
          </Link>
        </div>
      </header>

      <main className="pt-28 pb-20 px-6">
        <article className="max-w-3xl mx-auto">
          {/* Back Link */}
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-[#635F69] hover:text-[#7C3AED] font-medium mb-8 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Blog
          </Link>

          {/* Post Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <span className="px-3 py-1 rounded-full bg-[#7C3AED]/10 text-[#7C3AED] text-xs font-bold">
                {post.category}
              </span>
            </div>
            
            <h1 
              className="text-3xl sm:text-4xl md:text-5xl font-black text-[#332F3A] mb-4"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              {post.title}
            </h1>
            
            <p className="text-lg text-[#635F69] mb-6">
              {post.excerpt}
            </p>
            
            <div className="flex items-center gap-4 text-sm text-[#635F69] pb-8 border-b border-[#E5E1EF]">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] flex items-center justify-center">
                  <span className="text-white font-bold text-xs">K</span>
                </div>
                <span className="font-medium text-[#332F3A]">{post.author.name}</span>
              </div>
              <span>•</span>
              <span>{new Date(post.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
              <span>•</span>
              <span>{post.readTime}</span>
            </div>
          </div>

          {/* Post Content */}
          <div className="prose-custom">
            {renderContent(post.content)}
          </div>

          {/* CTA */}
          <div className="clay-card shadow-clay-card p-8 mt-12 text-center">
            <h3 
              className="text-xl font-bold text-[#332F3A] mb-2"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              Ready to get started?
            </h3>
            <p className="text-[#635F69] mb-6">
              Get your API key and start building today.
            </p>
            <Link
              href="/dashboard/api-keys"
              className="inline-flex h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 transition-all items-center gap-2"
            >
              Get Your API Key
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </article>
      </main>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-[#E5E1EF]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-[#635F69]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] flex items-center justify-center">
              <span className="text-white font-black text-sm" style={{ fontFamily: 'Nunito, sans-serif' }}>K</span>
            </div>
            <span>© 2025 KashRock. All rights reserved.</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/" className="hover:text-[#7C3AED] transition-colors">Home</Link>
            <Link href="/docs" className="hover:text-[#7C3AED] transition-colors">Docs</Link>
            <Link href="/dashboard" className="hover:text-[#7C3AED] transition-colors">Dashboard</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

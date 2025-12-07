'use client';

import Link from 'next/link';
import Image from 'next/image';

interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  readTime: string;
  category: string;
  author: {
    name: string;
    avatar?: string;
  };
  featured?: boolean;
}

// Blog posts data
const blogPosts: BlogPost[] = [
  {
    slug: 'why-builders-need-faster-sports-data',
    title: 'Why Builders Need Faster Access to Sports Data (And What We\'re Fixing at KashRock)',
    excerpt: 'Sports data is messy. Anyone who has ever tried building a prediction model, odds scraper, or betting tool knows the pain. That\'s the exact problem KashRock is solving.',
    date: '2025-01-15',
    readTime: '4 min read',
    category: 'Announcements',
    author: { name: 'KashRock Team' },
    featured: true,
  },
  {
    slug: 'why-your-sports-betting-app-needs-realtime-odds',
    title: 'Why Your Sports Betting App Needs a Real-Time Odds Backbone',
    excerpt: 'The sports betting market is exploding, but most new apps still struggle with the same problem: unreliable data pipelines. You need an infrastructure-level backbone, not a spreadsheet of scripts.',
    date: '2025-01-12',
    readTime: '3 min read',
    category: 'Engineering',
    author: { name: 'KashRock Team' },
  },
  {
    slug: 'how-to-build-sports-data-startup',
    title: 'How To Build a Sports Data Startup Without Spending Millions',
    excerpt: 'Everyone thinks you need a massive engineering team, enterprise data providers, and a giant budget to enter the sports data industry. You don\'t. What you need is leverage.',
    date: '2025-01-08',
    readTime: '4 min read',
    category: 'Guides',
    author: { name: 'KashRock Team' },
  },
];

const categories = ['All', 'Announcements', 'Guides', 'Engineering', 'Case Studies'];

export default function BlogPage() {
  const featuredPost = blogPosts.find(post => post.featured);
  const regularPosts = blogPosts.filter(post => !post.featured);

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
        <div className="max-w-6xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-12">
            <h1 
              className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight mb-4"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              <span className="text-[#332F3A]">The </span>
              <span className="clay-text-gradient-accent">KashRock</span>
              <span className="text-[#332F3A]"> Blog</span>
            </h1>
            <p className="text-lg text-[#635F69] max-w-2xl mx-auto">
              Product updates, engineering insights, and guides for building with the KashRock API.
            </p>
          </div>

          {/* Categories */}
          <div className="flex flex-wrap justify-center gap-2 mb-12">
            {categories.map((category, index) => (
              <button
                key={category}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  index === 0
                    ? 'bg-[#7C3AED] text-white shadow-clay-button'
                    : 'bg-white text-[#635F69] shadow-clay-card hover:text-[#7C3AED] hover:shadow-clay-card-hover'
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Featured Post */}
          {featuredPost && (
            <Link
              href={`/blog/${featuredPost.slug}`}
              className="block clay-card shadow-clay-card p-8 mb-8 hover:shadow-clay-card-hover hover:-translate-y-1 transition-all duration-300 group"
            >
              <div className="flex flex-col lg:flex-row gap-8">
                {/* Placeholder for featured image */}
                <div className="lg:w-1/2 aspect-video bg-gradient-to-br from-[#A78BFA]/20 to-[#7C3AED]/20 rounded-2xl flex items-center justify-center">
                  <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] shadow-clay-orb flex items-center justify-center">
                    <span className="text-white font-black text-3xl" style={{ fontFamily: 'Nunito, sans-serif' }}>K</span>
                  </div>
                </div>
                
                <div className="lg:w-1/2 flex flex-col justify-center">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="px-3 py-1 rounded-full bg-[#7C3AED]/10 text-[#7C3AED] text-xs font-bold">
                      Featured
                    </span>
                    <span className="px-3 py-1 rounded-full bg-[#10B981]/10 text-[#10B981] text-xs font-bold">
                      {featuredPost.category}
                    </span>
                  </div>
                  
                  <h2 
                    className="text-2xl sm:text-3xl font-black text-[#332F3A] mb-3 group-hover:text-[#7C3AED] transition-colors"
                    style={{ fontFamily: 'Nunito, sans-serif' }}
                  >
                    {featuredPost.title}
                  </h2>
                  
                  <p className="text-[#635F69] mb-4 line-clamp-3">
                    {featuredPost.excerpt}
                  </p>
                  
                  <div className="flex items-center gap-4 text-sm text-[#635F69]">
                    <span>{featuredPost.author.name}</span>
                    <span>•</span>
                    <span>{new Date(featuredPost.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    <span>•</span>
                    <span>{featuredPost.readTime}</span>
                  </div>
                </div>
              </div>
            </Link>
          )}

          {/* Blog Posts Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {regularPosts.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="clay-card shadow-clay-card p-6 hover:shadow-clay-card-hover hover:-translate-y-2 transition-all duration-300 group flex flex-col"
              >
                {/* Placeholder for post image */}
                <div className="aspect-video bg-gradient-to-br from-[#A78BFA]/10 to-[#7C3AED]/10 rounded-xl mb-4 flex items-center justify-center">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] shadow-clay-orb flex items-center justify-center opacity-50 group-hover:opacity-100 transition-opacity">
                    <span className="text-white font-black text-lg" style={{ fontFamily: 'Nunito, sans-serif' }}>K</span>
                  </div>
                </div>
                
                <span className="px-3 py-1 rounded-full bg-[#7C3AED]/10 text-[#7C3AED] text-xs font-bold w-fit mb-3">
                  {post.category}
                </span>
                
                <h3 
                  className="text-lg font-bold text-[#332F3A] mb-2 group-hover:text-[#7C3AED] transition-colors line-clamp-2"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {post.title}
                </h3>
                
                <p className="text-sm text-[#635F69] mb-4 line-clamp-2 flex-1">
                  {post.excerpt}
                </p>
                
                <div className="flex items-center gap-3 text-xs text-[#635F69] mt-auto">
                  <span>{new Date(post.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                  <span>•</span>
                  <span>{post.readTime}</span>
                </div>
              </Link>
            ))}
          </div>

          {/* Empty State (for when no posts) */}
          {blogPosts.length === 0 && (
            <div className="clay-card shadow-clay-card p-12 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#7C3AED]/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-[#7C3AED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-[#332F3A] mb-2" style={{ fontFamily: 'Nunito, sans-serif' }}>
                No posts yet
              </h3>
              <p className="text-[#635F69]">
                Check back soon for updates!
              </p>
            </div>
          )}
        </div>
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

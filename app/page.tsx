'use client';

import Link from 'next/link';
import { useState } from 'react';

// ============================================
// FLOATING BLOBS BACKGROUND
// ============================================
function FloatingBlobs() {
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
      {/* Primary violet blob - top left */}
      <div 
        className="absolute h-[60vh] w-[60vh] rounded-full blur-3xl bg-[#8B5CF6]/10 animate-clay-float"
        style={{ top: '-10%', left: '-10%' }}
      />
      {/* Pink blob - top right */}
      <div 
        className="absolute h-[50vh] w-[50vh] rounded-full blur-3xl bg-[#EC4899]/10 animate-clay-float-delayed animation-delay-2000"
        style={{ top: '10%', right: '-5%' }}
      />
      {/* Blue blob - center left */}
      <div 
        className="absolute h-[45vh] w-[45vh] rounded-full blur-3xl bg-[#0EA5E9]/10 animate-clay-float animation-delay-4000"
        style={{ top: '40%', left: '-8%' }}
      />
      {/* Green blob - bottom right */}
      <div 
        className="absolute h-[55vh] w-[55vh] rounded-full blur-3xl bg-[#10B981]/8 animate-clay-float-delayed animation-delay-6000"
        style={{ bottom: '-15%', right: '-10%' }}
      />
      {/* Amber blob - bottom center */}
      <div 
        className="absolute h-[40vh] w-[40vh] rounded-full blur-3xl bg-[#F59E0B]/8 animate-clay-float-slow"
        style={{ bottom: '5%', left: '30%' }}
      />
    </div>
  );
}

// ============================================
// NAVIGATION
// ============================================
function Navigation() {
  return (
    <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-3rem)] max-w-5xl">
      <div className="clay-card shadow-clay-card h-16 sm:h-20 px-4 sm:px-8 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] shadow-clay-orb flex items-center justify-center"
          >
            <span className="text-white font-black text-xl sm:text-2xl" style={{ fontFamily: 'Nunito, sans-serif' }}>K</span>
          </div>
          <span className="font-bold text-lg sm:text-xl text-[#332F3A] hidden sm:block" style={{ fontFamily: 'Nunito, sans-serif' }}>
            KashRock
          </span>
        </div>
        
        {/* Nav Links - Hidden on mobile */}
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-[#635F69] hover:text-[#7C3AED] font-medium transition-colors">Features</a>
          <a href="#blog" className="text-[#635F69] hover:text-[#7C3AED] font-medium transition-colors">Blog</a>
          <a href="#faq" className="text-[#635F69] hover:text-[#7C3AED] font-medium transition-colors">FAQ</a>
        </div>
        
        {/* CTA Button */}
        <button 
          onClick={() => {
            const emailInput = document.getElementById('waitlist-email');
            if (emailInput) {
              emailInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
              setTimeout(() => emailInput.focus(), 500);
            }
          }}
          className="h-11 sm:h-12 px-5 sm:px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.92] active:shadow-clay-pressed transition-all duration-200 flex items-center justify-center"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          Join Waitlist
        </button>
      </div>
    </nav>
  );
}

// ============================================
// HERO SECTION
// ============================================
function HeroSection() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setStatus('error');
      setMessage('Please enter a valid email address');
      return;
    }

    setStatus('loading');
    setMessage('');

    try {
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(typeof data?.error === 'string' ? data.error : 'Something went wrong. Please try again.');
      }

      setStatus('success');
      setMessage("You're on the list! We'll be in touch soon.");
      setEmail('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Something went wrong. Please try again.';
      setStatus('error');
      setMessage(errorMessage);
    }
  };

  return (
    <section id="waitlist" className="min-h-screen flex items-center justify-center pt-32 pb-20 px-6">
      <div className="max-w-5xl mx-auto text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/70 backdrop-blur-xl shadow-clay-card mb-8 animate-clay-breathe">
          <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
          <span className="text-sm font-semibold text-[#635F69]">Built for AI-Native Developers</span>
        </div>
        
        {/* Main Headline */}
        <h1 
          className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight leading-[1.1] mb-6"
          style={{ fontFamily: 'Nunito, sans-serif' }}
        >
          <span className="clay-text-gradient">AI-First Sports Data.</span>
          <br />
          <span className="text-[#332F3A]">Designed for Builders.</span>
          <br />
          <span className="text-[#7C3AED]">No Integration Headaches.</span>
        </h1>
        
        {/* Subheading */}
        <p className="text-lg sm:text-xl md:text-2xl text-[#635F69] max-w-3xl mx-auto mb-10 leading-relaxed font-medium">
          Focus on product and prompts, not plumbing. KashRock provides a single, consistent feed across 29+ US and EU books—including Pinnacle, PrizePicks, Underdog, Dabble, Bet365, 1xBet and more—with real-time odds, deep player props, and EV metrics, ready for your models, agents, and dashboards.
          <span className="text-[#7C3AED] font-semibold"> You ship faster while we handle coverage, latency, and normalization across markets.</span>
        </p>
        
        {/* Waitlist Form */}
        <form onSubmit={handleSubmit} className="max-w-lg mx-auto mb-6">
          <div className="flex flex-col sm:flex-row gap-3 items-stretch">
            <input
              id="waitlist-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              disabled={status === 'loading'}
              className="w-full sm:flex-1 h-16 px-6 rounded-[20px] bg-white shadow-clay-pressed text-[#332F3A] placeholder-[#635F69]/50 font-medium text-lg focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all disabled:opacity-50"
              style={{ fontFamily: 'DM Sans, sans-serif' }}
            />
            <button 
              type="submit"
              disabled={status === 'loading'}
              className="w-full sm:w-auto h-16 px-10 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold text-lg shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.92] active:shadow-clay-pressed transition-all duration-200 disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-3"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              {status === 'loading' ? (
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                <>
                  <span>Join Waitlist</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </>
              )}
            </button>
          </div>
          
          {/* Status Message */}
          {status !== 'idle' && status !== 'loading' && (
            <div className={`mt-4 p-3 rounded-xl text-sm font-medium ${
              status === 'success' 
                ? 'bg-[#10B981]/10 text-[#10B981]' 
                : 'bg-[#EF4444]/10 text-[#EF4444]'
            }`}>
              {message}
            </div>
          )}
        </form>
        
        {/* Trust indicators */}
        <p className="text-sm text-[#635F69]">
          🔒 No spam, ever. Unsubscribe anytime.
        </p>
      </div>
    </section>
  );
}

// ============================================
// STATS SECTION
// ============================================
function StatsSection() {
  const stats = [
    { value: '50+', label: 'Sports Covered', color: 'from-blue-400 to-blue-600' },
    { value: '29+', label: 'Sportsbooks', color: 'from-purple-400 to-purple-600' },
    { value: '1', label: 'API Call', color: 'from-pink-400 to-pink-600' },
    { value: '<2s', label: 'Response Time', color: 'from-emerald-400 to-emerald-600' },
  ];

  return (
    <section className="py-16 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
          {stats.map((stat, index) => (
            <div 
              key={index}
              className="clay-card shadow-clay-card p-6 sm:p-8 text-center hover:-translate-y-2 hover:shadow-clay-card-hover transition-all duration-500 group"
            >
              <div 
                className={`w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4 rounded-full bg-gradient-to-br ${stat.color} shadow-clay-orb flex items-center justify-center animate-clay-breathe group-hover:scale-110 transition-transform duration-300`}
              >
                <span 
                  className="text-white font-black text-lg sm:text-xl"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {stat.value}
                </span>
              </div>
              <p className="text-[#635F69] font-semibold text-sm sm:text-base">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================
// FEATURES BENTO GRID
// ============================================
function FeaturesSection() {
  const features = [
    {
      title: 'AI-Ready Sports Data',
      description: 'Tell AI "build me a betting tracker" and get instant access to 29+ books, player props, alt lines, and EV calculations. No API docs needed.',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      gradient: 'from-amber-400 to-orange-500',
      span: 'md:col-span-2 md:row-span-2',
      isHero: true,
    },
    {
      title: 'No More Scraping',
      description: 'Stop reverse-engineering DraftKings endpoints or scraping Props.cash. We deliver all the deep markets developers are hacking together.',
      icon: (
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      gradient: 'from-blue-400 to-cyan-500',
    },
    {
      title: 'Real-Time WebSocket Feeds',
      description: 'Sub-second updates with diff-only changes and heartbeat pings. No more 5-10 minute REST delays that kill live betting apps.',
      icon: (
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      gradient: 'from-cyan-400 to-teal-500',
    },
    {
      title: 'Complete Player Props',
      description: 'Every alt line, player prop, and team total that exists. No more "missing markets" forcing you to juggle multiple APIs.',
      icon: (
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      gradient: 'from-purple-400 to-violet-500',
    },
    {
      title: 'No Rate Limit Headaches',
      description: 'Unlimited requests for serious builders. No more $20/month for slow NBA data or losing access when Pinnacle changes rules.',
      icon: (
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      gradient: 'from-emerald-400 to-green-500',
    },
    {
      title: 'Built for AI Models',
      description: 'Consistent IDs, complete timestamps, historical depth, and normalized schemas. Everything AI needs to train winning models.',
      icon: (
        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      gradient: 'from-pink-400 to-rose-500',
    },
  ];

  return (
    <section id="features" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 
            className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            <span className="text-[#332F3A]">The Data Backbone for </span>
            <span className="clay-text-gradient-accent">AI Betting Products</span>
          </h2>
          <p className="text-lg text-[#635F69] max-w-2xl mx-auto">
            No more scraping, rate limits, missing markets, or slow updates. One unified layer for the data and infrastructure your AI-powered apps depend on.
          </p>
        </div>
        
        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div 
              key={index}
              className={`clay-card shadow-clay-card p-6 sm:p-8 hover:-translate-y-2 hover:shadow-clay-card-hover transition-all duration-500 group ${feature.span || ''} ${feature.isHero ? 'flex flex-col justify-between' : ''}`}
            >
              {/* Icon */}
              <div 
                className={`w-14 h-14 ${feature.isHero ? 'sm:w-20 sm:h-20' : ''} rounded-2xl bg-gradient-to-br ${feature.gradient} shadow-clay-orb flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
              >
                <span className="text-white">{feature.icon}</span>
              </div>
              
              {/* Content */}
              <div>
                <h3 
                  className={`font-bold mb-3 text-[#332F3A] ${feature.isHero ? 'text-2xl sm:text-3xl' : 'text-xl'}`}
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {feature.title}
                </h3>
                <p className={`text-[#635F69] leading-relaxed ${feature.isHero ? 'text-lg' : ''}`}>
                  {feature.description}
                </p>
              </div>
              
              {/* Hero card extra content */}
              {feature.isHero && (
                <div className="mt-8 p-4 rounded-2xl bg-[#EFEBF5] shadow-clay-pressed">
                  <code className="text-sm text-[#7C3AED] font-mono block">
                    "Build me a live betting tracker"
                  </code>
                  <div className="text-xs text-[#635F69] mt-2">
                    → AI gets everything instantly
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================
// COMPETITORS COMPARISON
// ============================================
function ComparisonSection() {
  const painPoints = [
    { icon: '🔗', title: 'Scraping Workarounds', description: 'Reverse-engineering DraftKings JSON endpoints and scraping Props.cash because APIs don\'t have the markets' },
    { icon: '⏰', title: 'Slow Updates', description: '$20/month for NBA data that lags 5-10 minutes behind the books, killing live betting apps' },
    { icon: '🚫', title: 'Missing Markets', description: 'No player props, alt lines, or team totals forcing you to juggle 10+ incomplete APIs' },
    { icon: '🔐', title: 'Access Lockouts', description: 'Pinnacle changed rules mid-2025, cutting off developers without affiliate status' },
  ];

  return (
    <section className="py-20 px-6 bg-gradient-to-b from-transparent via-[#EDE9F5] to-transparent">
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Pain Points */}
          <div>
            <h2 
              className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-6"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              <span className="text-[#332F3A]">Stop </span>
              <span className="text-[#DB2777]">Hacking Together</span>
              <span className="text-[#332F3A]"> Data</span>
            </h2>
            <p className="text-lg text-[#635F69] mb-8 leading-relaxed">
              Developers in 2025 are still scraping sites, reverse-engineering APIs, and dealing with rate limits just to get basic sports data. 
              <span className="font-semibold text-[#7C3AED]"> We give you everything in one AI-friendly endpoint.</span>
            </p>
            
            <div className="space-y-4">
              {painPoints.map((point, index) => (
                <div 
                  key={index}
                  className="flex items-start gap-4 p-4 rounded-[24px] bg-white/50 backdrop-blur-sm shadow-clay-card hover:-translate-y-1 transition-all duration-300"
                >
                  <span className="text-2xl">{point.icon}</span>
                  <div>
                    <h4 className="font-bold text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>{point.title}</h4>
                    <p className="text-sm text-[#635F69]">{point.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Right: Solution */}
          <div className="clay-card shadow-clay-surface p-8 sm:p-10 relative overflow-hidden">
            {/* Decorative gradient */}
            <div className="absolute -top-20 -right-20 w-40 h-40 rounded-full bg-gradient-to-br from-[#7C3AED]/20 to-[#DB2777]/20 blur-3xl" />
            
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#10B981]/10 text-[#10B981] font-semibold text-sm mb-6">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                The KashRock Way
              </div>
              
              <h3 
                className="text-2xl sm:text-3xl font-black text-[#332F3A] mb-4"
                style={{ fontFamily: 'Nunito, sans-serif' }}
              >
                Just Tell AI What to Build
              </h3>
              
              <ul className="space-y-3 mb-8">
                {['Real-time WebSocket feeds (no 5-min delays)', 'Every player prop & alt line (no scraping)', 'Unlimited requests (no rate limits)', 'AI-ready schemas (no integration hell)', 'Complete historical data (perfect for models)'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-[#635F69]">
                    <span className="w-6 h-6 rounded-full bg-[#10B981] flex items-center justify-center flex-shrink-0">
                      <svg className="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
              
              <div className="p-4 rounded-2xl bg-[#1e1e2e] text-sm font-mono overflow-x-auto">
                <div className="text-[#635F69]">// Tell AI: "Build a betting tracker"</div>
                <div>
                  <span className="text-[#7C3AED]">GET</span>
                  <span className="text-white"> /v5/event/</span>
                  <span className="text-[#10B981]">&#123;id&#125;</span>
                </div>
                <div className="text-[#635F69] mt-1 text-xs">
                  → Everything you need. Zero setup.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============================================
// TECHNICAL FEATURES (v5 Architecture)
// ============================================
function TechnicalFeaturesSection() {
  const techFeatures = [
    {
      title: 'Entity Resolution Pipeline',
      description: 'Exact → normalized → fuzzy matching across 29 sources. Handles "LAL", "Lakers", "Los Angeles Lakers" automatically.',
      badge: 'Smart Matching'
    },
    {
      title: 'Vig Removal Engine',
      description: 'Weighted consensus from sharp books (Pinnacle, Novig). Get true probabilities, not inflated house odds.',
      badge: 'Fair Odds'
    },
    {
      title: 'Correlation Guards',
      description: 'Automatic detection of correlated bets. No more accidentally parlaying same-game props.',
      badge: 'Risk Management'
    },
    {
      title: 'Hot Cache Layer',
      description: 'Redis-backed caching with TTL invalidation. Sub-2s responses even with 29 concurrent sources.',
      badge: 'Performance'
    },
  ];

  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 
            className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            <span className="text-[#332F3A]">Built for </span>
            <span className="clay-text-gradient-accent">Production</span>
          </h2>
          <p className="text-lg text-[#635F69] max-w-2xl mx-auto">
            Enterprise-grade infrastructure that handles the complexity so you don&apos;t have to.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {techFeatures.map((feature, index) => (
            <div 
              key={index}
              className="clay-card shadow-clay-card p-6 sm:p-8 hover:-translate-y-2 hover:shadow-clay-card-hover transition-all duration-500 group relative overflow-hidden"
            >
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#7C3AED]/10 text-[#7C3AED] text-xs font-bold mb-4">
                {feature.badge}
              </div>
              
              {/* Content */}
              <h3 
                className="text-xl font-bold mb-3 text-[#332F3A]"
                style={{ fontFamily: 'Nunito, sans-serif' }}
              >
                {feature.title}
              </h3>
              <p className="text-[#635F69] leading-relaxed">
                {feature.description}
              </p>
              
              {/* Decorative gradient */}
              <div className="absolute -bottom-10 -right-10 w-32 h-32 rounded-full bg-gradient-to-br from-[#7C3AED]/5 to-transparent blur-2xl group-hover:scale-150 transition-transform duration-500" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================
// BLOG SECTION
// ============================================
function BlogSection() {
  const posts = [
    {
      slug: 'why-builders-need-faster-sports-data',
      title: 'Why Builders Need Faster Access to Sports Data (And What We\'re Fixing at KashRock)',
      excerpt: 'Sports data is messy. We built KashRock because builders deserve clean, fast, normalized data without maintaining 10 scrapers.',
      date: 'Jan 15, 2025',
      readTime: '4 min read',
      category: 'Announcements',
    },
    {
      slug: 'why-your-sports-betting-app-needs-realtime-odds',
      title: 'Why Your Sports Betting App Needs a Real-Time Odds Backbone',
      excerpt: 'Your UX dies when your odds are 30 seconds late. Here’s why a real-time backbone matters and how we designed ours.',
      date: 'Jan 12, 2025',
      readTime: '3 min read',
      category: 'Engineering',
    },
    {
      slug: 'how-to-build-sports-data-startup',
      title: 'How To Build a Sports Data Startup Without Spending Millions',
      excerpt: 'You don’t need a Fortune 500 budget to launch a sports data product. Start with leverage, not headcount.',
      date: 'Jan 8, 2025',
      readTime: '4 min read',
      category: 'Guides',
    },
  ];

  return (
    <section id="blog" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <p className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#7C3AED]/10 text-[#7C3AED] text-sm font-bold mb-4">
            Latest from the Blog
          </p>
          <h2 
            className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            <span className="text-[#332F3A]">Build faster with</span>{' '}
            <span className="clay-text-gradient-accent">real insights</span>
          </h2>
          <p className="text-lg text-[#635F69] max-w-3xl mx-auto">
            Roadmaps, engineering deep-dives, and playbooks for people building sports betting products with KashRock.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="clay-card shadow-clay-card p-6 flex flex-col hover:-translate-y-2 hover:shadow-clay-card-hover transition-all duration-300"
            >
              <span className="text-xs font-bold text-[#7C3AED] bg-[#7C3AED]/10 px-3 py-1 rounded-full w-fit mb-4">
                {post.category}
              </span>
              <h3 
                className="text-xl font-bold text-[#332F3A] mb-3"
                style={{ fontFamily: 'Nunito, sans-serif' }}
              >
                {post.title}
              </h3>
              <p className="text-sm text-[#635F69] leading-relaxed flex-1">
                {post.excerpt}
              </p>
              <div className="text-xs text-[#635F69] mt-6 flex items-center justify-between">
                <span>{post.date}</span>
                <span>{post.readTime}</span>
              </div>
            </Link>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            href="/blog"
            className="inline-flex h-12 px-6 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 transition-all"
          >
            View all posts
          </Link>
        </div>
      </div>
    </section>
  );
}

// ============================================
// PRICING SECTION
// ============================================
function PricingSection() {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: '/month',
      description: 'Prototype freely with full market coverage',
      features: [
        '1,000 API requests/day',
        'All integrated books',
        'All sports & market types (incl. props)',
        'No EV slips',
        'No export engine or historical data',
        'Standard rate limits'
      ],
      cta: 'Start Free',
      highlighted: false,
    },
    {
      name: 'Starter',
      price: '$49',
      period: '/month',
      description: 'For hobbyists ready for actionable EV insights',
      features: [
        '25,000 API requests/day',
        'All integrated books',
        'All sports & market types',
        'Basic EV slips (single-leg)',
        'Historical access',
        'Standard rate limits'
      ],
      cta: 'Upgrade to Starter',
      highlighted: false,
    },
    {
      name: 'Developer',
      price: '$99',
      period: '/month',
      description: 'Most popular for professional builders',
      features: [
        '100,000 API requests/day',
        'All integrated books (US + EU/Global)',
        'All sports & market types',
        'Advanced EV slips (multi-leg + guards)',
        'Historical access',
        'Export engine (10k rows/day)',
        'Faster rate limits'
      ],
      cta: 'Choose Developer',
      highlighted: true,
    },
    {
      name: 'Pro',
      price: '$249',
      period: '/month',
      description: 'For power users scaling across global markets',
      features: [
        '500,000 API requests/day',
        'All integrated books (US + EU/Global)',
        'All sports & market types',
        'Full historical archive',
        'Full export engine (global)',
        'Expanded EV features (global)',
        'Priority support & higher concurrency'
      ],
      cta: 'Scale Globally',
      highlighted: false,
    },
    
  ];

  return (
    <section id="pricing" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 
            className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            <span className="text-[#332F3A]">Simple, </span>
            <span className="clay-text-gradient-accent">Transparent</span>
            <span className="text-[#332F3A]"> Pricing</span>
          </h2>
          <p className="text-lg text-[#635F69] max-w-2xl mx-auto">
            Choose the plan that fits your needs. Upgrade or downgrade anytime.
          </p>
        </div>
        
        {/* Pricing Cards */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {plans.map((plan, index) => (
            <div 
              key={index}
              className={`clay-card shadow-clay-card p-8 relative transition-all duration-300 hover:-translate-y-2 hover:shadow-clay-card-hover flex flex-col h-full ${
                plan.highlighted 
                  ? 'ring-2 ring-[#7C3AED]/60 bg-gradient-to-br from-white to-[#F4F1FA]' 
                  : ''
              }`}
            >
              {/* Popular badge */}
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full bg-gradient-to-r from-[#7C3AED] to-[#DB2777] text-white text-sm font-bold shadow-clay-button">
                  Most Popular
                </div>
              )}
              
              <div className="text-center mb-6">
                <h3 
                  className="text-xl font-bold text-[#332F3A] mb-2"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {plan.name}
                </h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span 
                    className="text-4xl sm:text-5xl font-black text-[#7C3AED]"
                    style={{ fontFamily: 'Nunito, sans-serif' }}
                  >
                    {plan.price}
                  </span>
                  <span className="text-[#635F69]">{plan.period}</span>
                </div>
                <p className="text-sm text-[#635F69] mt-2">{plan.description}</p>
              </div>
              
              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-3 text-[#635F69]">
                    <span className="w-5 h-5 rounded-full bg-[#10B981]/10 flex items-center justify-center flex-shrink-0">
                      <svg className="w-3 h-3 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </span>
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <button 
                className={`mt-auto w-full h-14 rounded-[20px] font-bold transition-all duration-200 hover:-translate-y-1 active:scale-[0.92] active:shadow-clay-pressed ${
                  plan.highlighted
                    ? 'bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white shadow-clay-button hover:shadow-clay-button-hover'
                    : 'bg-white text-[#7C3AED] shadow-clay-card hover:shadow-clay-card-hover active:shadow-clay-pressed'
                }`}
                style={{ fontFamily: 'Nunito, sans-serif' }}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
        
        <p className="text-center text-sm text-[#635F69] mt-8">
          No surprise overages. No hidden fees. Cancel anytime.
        </p>
      </div>
    </section>
  );
}

// ============================================
// FAQ SECTION
// ============================================
function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  
  const faqs = [
    {
      question: 'How does the unified v5 endpoint work?',
      answer: 'One call to /v5/event/{id} returns all 29+ sportsbooks, player props, consensus fair odds (vig-removed), and EV slip candidates. We handle event matching, vig removal, and EV calculation automatically. No more calling 10+ APIs and stitching data together.',
    },
    {
      question: 'What is "canonical event matching"?',
      answer: 'We automatically match events across all sources using a 3-stage pipeline: exact match → normalized tokens → fuzzy matching. This means "LAL", "Lakers", and "Los Angeles Lakers" all resolve to the same canonical event. You never have to write matching logic.',
    },
    {
      question: 'How do you calculate consensus fair odds?',
      answer: 'We remove vig from sharp books (Pinnacle, Novig) and compute a weighted consensus. Sharp books get higher weight (1.0), soft books get lower weight (0.3-0.8). The result is true probability, not inflated house odds.',
    },
    {
      question: 'What is the EV engine and how does it work?',
      answer: 'Our built-in EV engine compares soft book odds (FanDuel, DraftKings, PrizePicks) against consensus fair odds to find +EV opportunities. It includes correlation guards to prevent same-game parlays and generates 1-3 leg slip candidates automatically.',
    },
    {
      question: 'How fast is the API with 29 concurrent sources?',
      answer: 'Sub-2 seconds. We fetch all sources concurrently using async I/O and cache hot data in Redis with TTL invalidation. Even with 29 books, responses are fast enough for real-time applications.',
    },
  ];

  return (
    <section id="faq" className="py-20 px-6">
      <div className="max-w-3xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 
            className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-4"
            style={{ fontFamily: 'Nunito, sans-serif' }}
          >
            <span className="text-[#332F3A]">Got </span>
            <span className="clay-text-gradient-accent">Questions?</span>
          </h2>
        </div>
        
        {/* FAQ Items */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div 
              key={index}
              className={`clay-card overflow-hidden transition-all duration-300 ${
                openIndex === index ? 'shadow-clay-pressed' : 'shadow-clay-card hover:shadow-clay-card-hover'
              }`}
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full p-6 text-left flex items-center justify-between gap-4"
              >
                <span 
                  className="font-bold text-[#332F3A]"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {faq.question}
                </span>
                <span 
                  className={`w-8 h-8 rounded-full bg-[#7C3AED]/10 flex items-center justify-center flex-shrink-0 transition-transform duration-300 ${
                    openIndex === index ? 'rotate-180' : ''
                  }`}
                >
                  <svg className="w-4 h-4 text-[#7C3AED]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </button>
              
              <div 
                className={`overflow-hidden transition-all duration-300 ${
                  openIndex === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <p className="px-6 pb-6 text-[#635F69] leading-relaxed">
                  {faq.answer}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ============================================
// FINAL CTA SECTION
// ============================================
function CTASection() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setStatus('error');
      setMessage('Please enter a valid email address');
      return;
    }

    setStatus('loading');
    setMessage('');

    try {
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(typeof data?.error === 'string' ? data.error : 'Something went wrong. Please try again.');
      }

      setStatus('success');
      setMessage("You're on the list! We'll be in touch soon.");
      setEmail('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Something went wrong. Please try again.';
      setStatus('error');
      setMessage(errorMessage);
    }
  };

  return (
    <section className="py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="clay-card shadow-clay-surface p-10 sm:p-16 text-center relative overflow-hidden">
          {/* Decorative blobs */}
          <div className="absolute -top-20 -left-20 w-40 h-40 rounded-full bg-gradient-to-br from-[#7C3AED]/20 to-transparent blur-3xl" />
          <div className="absolute -bottom-20 -right-20 w-40 h-40 rounded-full bg-gradient-to-br from-[#DB2777]/20 to-transparent blur-3xl" />
          
          <div className="relative z-10">
            <h2 
              className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-4"
              style={{ fontFamily: 'Nunito, sans-serif' }}
            >
              <span className="text-[#332F3A]">Ready to </span>
              <span className="clay-text-gradient-accent">Build?</span>
            </h2>
            <p className="text-lg text-[#635F69] max-w-xl mx-auto mb-8">
              Join the waitlist and be the first to know when we launch.
            </p>
            
            {/* Waitlist Form */}
            <form onSubmit={handleSubmit} className="max-w-lg mx-auto">
              <div className="flex flex-col sm:flex-row gap-3 items-stretch">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  disabled={status === 'loading'}
                  className="w-full sm:flex-1 h-16 px-6 rounded-[20px] bg-white shadow-clay-pressed text-[#332F3A] placeholder-[#635F69]/50 font-medium text-lg focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/30 transition-all disabled:opacity-50"
                  style={{ fontFamily: 'DM Sans, sans-serif' }}
                />
                <button 
                  type="submit"
                  disabled={status === 'loading'}
                  className="w-full sm:w-auto h-16 px-10 rounded-[20px] bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] text-white font-bold text-lg shadow-clay-button hover:shadow-clay-button-hover hover:-translate-y-1 active:scale-[0.92] active:shadow-clay-pressed transition-all duration-200 disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-3"
                  style={{ fontFamily: 'Nunito, sans-serif' }}
                >
                  {status === 'loading' ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                  ) : (
                    <>
                      <span>Join Waitlist</span>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </>
                  )}
                </button>
              </div>
              
              {/* Status Message */}
              {status !== 'idle' && status !== 'loading' && (
                <div className={`mt-4 p-3 rounded-xl text-sm font-medium ${
                  status === 'success' 
                    ? 'bg-[#10B981]/10 text-[#10B981]' 
                    : 'bg-[#EF4444]/10 text-[#EF4444]'
                }`}>
                  {message}
                </div>
              )}
            </form>
            
            <p className="mt-6 text-sm text-[#635F69]">
              🔒 No spam, ever. Unsubscribe anytime.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

// ============================================
// FOOTER
// ============================================
function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-[#E5E1EF]">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#A78BFA] to-[#7C3AED] shadow-clay-orb flex items-center justify-center">
              <span className="text-white font-black text-lg" style={{ fontFamily: 'Nunito, sans-serif' }}>K</span>
            </div>
            <span className="font-bold text-lg text-[#332F3A]" style={{ fontFamily: 'Nunito, sans-serif' }}>
              KashRock API
            </span>
          </div>
          
          {/* Links */}
          <div className="flex items-center gap-8 text-sm">
            <a href="#" className="text-[#635F69] hover:text-[#7C3AED] transition-colors">Documentation</a>
            <a href="#" className="text-[#635F69] hover:text-[#7C3AED] transition-colors">Status</a>
            <a href="#" className="text-[#635F69] hover:text-[#7C3AED] transition-colors">Privacy</a>
            <a href="#" className="text-[#635F69] hover:text-[#7C3AED] transition-colors">Terms</a>
          </div>
          
          {/* Copyright */}
          <p className="text-sm text-[#635F69]">
            © 2025 KashRock. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

// ============================================
// MAIN PAGE
// ============================================
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#F4F1FA] overflow-x-hidden">
      <FloatingBlobs />
      <Navigation />
      <main>
        <HeroSection />
        <StatsSection />
        <FeaturesSection />
        <ComparisonSection />
        <TechnicalFeaturesSection />
        <BlogSection />
        <FAQSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}

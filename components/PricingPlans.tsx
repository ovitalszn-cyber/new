'use client'

import SubscribeButton from '@/components/SubscribeButton'

/** Shared plan grid — homepage pricing section and /pricing page. */
export default function PricingPlans() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-white/10 bg-[#0C0D0F]">
      <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col relative">
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-zinc-700 text-zinc-200 text-xs font-medium rounded-full whitespace-nowrap">
          Free Forever
        </div>
        <div className="mb-4 mt-2">
          <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Sandbox</h3>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-medium text-white">$0</span>
            <span className="text-zinc-500">/mo</span>
          </div>
          <p className="text-sm font-bold text-zinc-300 mt-2">2 requests / minute</p>
          <p className="text-sm text-zinc-500 mt-3">
            Try the API for free with CS2 player props — see the data shape before you pay.
          </p>
        </div>
        <ul className="space-y-3 mb-8 flex-1">
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">CS2 player props only (no schedules or live games)</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Same response format as paid plans</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">No credit card required</span>
          </li>
        </ul>
        <div className="mt-auto">
          <SubscribeButton
            plan="sandbox"
            label="Get Sandbox Key"
            className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block disabled:opacity-50"
          />
        </div>
      </div>

      <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col">
        <div className="mb-4">
          <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Hobby</h3>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-medium text-white">$29</span>
            <span className="text-zinc-500">/mo</span>
          </div>
          <p className="text-sm font-bold text-zinc-300 mt-2">50 requests / minute</p>
          <p className="text-sm text-zinc-500 mt-3">
            Player props and match odds across every title we cover — CS2, League, Dota 2, and more.
          </p>
        </div>
        <ul className="space-y-3 mb-8 flex-1">
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Player props for every sport we support</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Player photos and team logos in every response</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Match odds from sportsbooks and prediction markets</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Email support</span>
          </li>
        </ul>
        <div className="mt-auto">
          <SubscribeButton
            plan="hobby"
            label="Subscribe"
            className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block disabled:opacity-50"
          />
        </div>
      </div>

      <div className="p-8 md:p-6 border-b md:border-b-0 md:border-r border-white/10 hover:bg-white/[0.02] transition-colors flex flex-col relative">
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-500 text-white text-xs font-medium rounded-full">
          Most Popular
        </div>
        <div className="mb-4 mt-2">
          <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Builder</h3>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-medium text-white">$99</span>
            <span className="text-zinc-500">/mo</span>
          </div>
          <p className="text-sm font-bold text-zinc-300 mt-2">100 requests / minute</p>
          <p className="text-sm text-zinc-500 mt-3">
            Live scoreboards, past matches, and prop results so you can build and check apps end to end.
          </p>
        </div>
        <ul className="space-y-3 mb-8 flex-1">
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Everything in Hobby</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Live player kills, deaths, and assists in under 2 seconds</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Upcoming, live, and finished match schedules</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Per-player map history and full match box scores</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">See if a prop hit, missed, or pushed after the game</span>
          </li>
        </ul>
        <div className="mt-auto">
          <SubscribeButton
            plan="builder"
            label="Subscribe"
            className="w-full px-6 py-3 bg-white text-black rounded-sm hover:bg-zinc-200 transition-colors text-center block disabled:opacity-50"
          />
        </div>
      </div>

      <div className="p-8 md:p-6 hover:bg-white/[0.02] transition-colors flex flex-col">
        <div className="mb-4">
          <h3 className="text-base font-medium text-white uppercase tracking-wider mb-2">Pro</h3>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-medium text-white">$249</span>
            <span className="text-zinc-500">/mo</span>
          </div>
          <p className="text-sm font-bold text-zinc-300 mt-2">250 requests / minute</p>
          <p className="text-sm text-zinc-500 mt-3">
            More requests per minute for live products, plus first look at new sports we add.
          </p>
        </div>
        <ul className="space-y-3 mb-8 flex-1">
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">Everything in Builder</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">2.5× more requests per minute than Builder</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5 shrink-0">✓</span>
            <span className="text-zinc-300">First access when we add new sports</span>
          </li>
        </ul>
        <div className="mt-auto">
          <SubscribeButton
            plan="pro"
            label="Subscribe"
            className="w-full px-6 py-3 bg-white/5 border border-white/10 text-white rounded-sm hover:bg-white/10 transition-colors text-center block disabled:opacity-50"
          />
        </div>
      </div>
    </div>
  )
}

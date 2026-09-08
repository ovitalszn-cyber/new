import { LIVE_CS2_PROP_PATH, LIVE_CS2_PROP_SAMPLE } from "@/lib/seo/live-cs2-prop"

export function PropCode() {
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-sm overflow-hidden shadow-2xl">
      <div className="flex items-center px-4 py-3 border-b border-white/5 bg-white/[0.02]">
        <div className="flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/50" />
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
          <div className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/50" />
        </div>
        <div className="ml-4 text-xs font-mono text-zinc-500">GET {LIVE_CS2_PROP_PATH}</div>
      </div>
      <pre className="p-5 font-mono text-xs leading-normal overflow-x-auto text-zinc-300">
        {JSON.stringify(LIVE_CS2_PROP_SAMPLE, null, 2)}
      </pre>
    </div>
  )
}

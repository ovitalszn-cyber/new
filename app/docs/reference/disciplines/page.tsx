import { DocsShell } from '@/components/docs/DocsShell'
import { Curl } from '@/components/docs/Code'
import { SPORTS } from '@/lib/docs'

export default function SportsPage() {
  return (
    <DocsShell active="sports">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Sports</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Path param <code className="text-white">sport</code>. Props also accept <code className="text-white">game=</code>.
      </p>
      <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-zinc-500">
            <tr>
              <th className="py-3 px-4">Slug</th>
              <th className="py-3 px-4">Name</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {SPORTS.map((s) => (
              <tr key={s.id}>
                <td className="py-3 px-4 font-mono text-emerald-400">{s.id}</td>
                <td className="py-3 px-4 text-white">{s.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Curl path="/v6/esports/valorant/fixtures" />
    </DocsShell>
  )
}

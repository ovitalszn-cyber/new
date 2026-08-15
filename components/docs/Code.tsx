import { API_BASE } from '@/lib/docs'

export function Curl({ path }: { path: string }) {
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden font-mono text-sm mb-8">
      <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 flex justify-between">
        <span>cURL</span>
        <span className="text-[10px] uppercase">GET</span>
      </div>
      <pre className="p-4 overflow-x-auto text-zinc-300 whitespace-pre-wrap">{`curl -H "X-API-Key: YOUR_API_KEY" \\
  "${API_BASE}${path}"`}</pre>
    </div>
  )
}

export function JsonBlock({
  title,
  data,
}: {
  title: string
  data: unknown
}) {
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-md overflow-hidden mb-8">
      <div className="bg-white/5 px-4 py-2 border-b border-white/5 text-zinc-500 text-xs">
        {title}
      </div>
      <pre className="p-4 font-mono text-xs leading-relaxed overflow-x-auto text-emerald-400">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}

export function Params({
  rows,
}: {
  rows: { name: string; type: string; required?: boolean; note: string }[]
}) {
  return (
    <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
      <table className="w-full text-left text-sm">
        <thead className="bg-white/5 text-zinc-500">
          <tr>
            <th className="px-4 py-3">Param</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Required</th>
            <th className="px-4 py-3">Description</th>
          </tr>
        </thead>
        <tbody className="text-zinc-400 divide-y divide-white/5">
          {rows.map((row) => (
            <tr key={row.name}>
              <td className="px-4 py-3 font-mono text-white">{row.name}</td>
              <td className="px-4 py-3 italic">{row.type}</td>
              <td className="px-4 py-3">{row.required ? 'Yes' : '—'}</td>
              <td className="px-4 py-3">{row.note}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function Route({ method = 'GET', path }: { method?: string; path: string }) {
  return (
    <div className="bg-[#0C0D0F] border border-white/10 rounded-md p-4 font-mono text-sm mb-8">
      <span className="text-emerald-400">{method}</span>
      <span className="text-zinc-300 ml-3">{path}</span>
    </div>
  )
}

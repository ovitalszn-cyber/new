import { DocsShell } from '@/components/docs/DocsShell'
import { Curl, JsonBlock } from '@/components/docs/Code'
import { BOOKS } from '@/lib/docs'

const SAMPLE = {
  book_id: 1,
  key: 'prizepicks',
  display_name: 'PrizePicks',
  status: 'active',
}

export default function BooksPage() {
  return (
    <DocsShell active="books">
      <h1 className="text-4xl font-semibold text-white mb-4 tracking-tight">Books</h1>
      <p className="text-lg text-zinc-400 mb-8">
        Filter props with <code className="text-white">book=</code>. Registry: <code className="text-white">GET /v6/books</code>.
      </p>
      <div className="overflow-x-auto border border-white/5 rounded-lg bg-[#0C0D0F] mb-8">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-zinc-500">
            <tr>
              <th className="py-3 px-4">ID</th>
              <th className="py-3 px-4">Name</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {BOOKS.map((b) => (
              <tr key={b.id}>
                <td className="py-3 px-4 font-mono text-emerald-400">{b.id}</td>
                <td className="py-3 px-4 text-white">{b.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Curl path="/v6/books" />
      <JsonBlock title="200 · live" data={SAMPLE} />
      <Curl path="/v6/esports/props?game=cs2&book=prizepicks" />
    </DocsShell>
  )
}

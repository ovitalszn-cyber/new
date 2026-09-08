type CompareTableProps = {
  headers: readonly string[]
  rows: readonly (readonly string[])[]
}

export function CompareTable({ headers, rows }: CompareTableProps) {
  return (
    <div className="overflow-x-auto bg-[#0C0D0F] border border-white/10 rounded-sm">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-white/10">
            {headers.map((header, i) => (
              <th key={i} className="px-6 py-4 font-medium text-white">
                {header || "\u00a0"}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row[0]} className="border-b border-white/5 last:border-0">
              {row.map((cell, i) => (
                <td
                  key={`${row[0]}-${i}`}
                  className={i === 0 ? "px-6 py-4 text-white font-medium" : "px-6 py-4 text-zinc-400"}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

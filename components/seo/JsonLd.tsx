export function JsonLd({ data }: { data: unknown[] | Record<string, unknown> }) {
  const payload = Array.isArray(data) ? data : [data]
  return (
    <>
      {payload.map((block, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(block) }}
        />
      ))}
    </>
  )
}

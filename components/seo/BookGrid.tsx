import { BOOK_LOGOS } from "@/lib/seo/book-logos"

export function BookGrid() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
      {BOOK_LOGOS.map((book) => (
        <div
          key={book.name}
          className="bg-[#0C0D0F] border border-white/10 rounded-sm px-4 py-4 flex flex-col items-center gap-2"
        >
          <img src={book.src} alt={book.name} className="h-12 w-12 rounded-xl object-cover" />
          <span className="text-sm text-white">{book.name}</span>
        </div>
      ))}
    </div>
  )
}

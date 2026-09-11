import { BOOK_LOGOS } from "@/lib/seo/book-logos"

export default function BookMarquee() {
  return (
    <div
      aria-label="Books on KashRock: PrizePicks, Underdog, Betr, Sleeper, Dabble, Boom, Pick6, Thunderpick, Kalshi, Polymarket"
      className="mt-14 mb-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-4"
    >
      {BOOK_LOGOS.map((book) => (
        <img
          key={book.name}
          src={book.src}
          alt={book.name}
          className="h-14 w-14 rounded-sm border border-white/10 object-cover"
        />
      ))}
    </div>
  )
}

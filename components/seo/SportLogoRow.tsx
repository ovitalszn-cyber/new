import { GAME_LOGOS } from "@/lib/seo/game-logos"

export function SportLogoRow({ className = "" }: { className?: string }) {
  return (
    <div
      aria-label="Sports: CS2, Valorant, League of Legends, Dota 2, Call of Duty, Rainbow Six, Mobile Legends, Deadlock"
      className={`flex flex-wrap items-center justify-center gap-x-8 gap-y-4 ${className}`}
    >
      {GAME_LOGOS.map((logo) => (
        <img
          key={logo.id}
          src={logo.src}
          alt={logo.alt}
          className={`h-8 w-auto ${logo.invert ? "invert" : ""}`}
        />
      ))}
    </div>
  )
}

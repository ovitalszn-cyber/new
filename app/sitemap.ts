import type { MetadataRoute } from "next"

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://www.kashrock.com"
  const routes = [
    "/",
    "/pricing",
    "/features",
    "/how-it-works",
    "/build-esports-app",
    "/quickstart",
    "/esports-data-api",
    "/dfs-esports-api",
    "/cs2-api",
    "/cs2-props-api",
    "/league-of-legends-api",
    "/dota-2-api",
    "/valorant-api",
    "/esports-odds-api",
    "/esports-consensus-api",
    "/esports-api-pricing",
    "/esports-api-free-tier",
    "/prizepicks-api",
    "/underdog-api",
    "/sleeper-api",
    "/betr-api",
    "/boom-api",
    "/pick6-api",
    "/thunderpick-api",
    "/kalshi-api",
    "/polymarket-api",
    "/coverage",
    "/historical-esports-data-api",
    "/blog/how-to-get-prizepicks-props-api",
    "/blog/cs2-player-props-without-scraping",
    "/blog/build-esports-props-app-in-a-weekend",
    "/blog/how-to-build-an-esports-betting-app",
    "/abios-alternative",
    "/pandascore-alternative",
    "/sportradar-alternative",
    "/grid-alternative",
    "/mcp",
    "/docs",
    "/docs/api-reference",
    "/docs/markets",
    "/docs/reference/sportsbooks",
    "/docs/endpoints/props",
    "/docs/endpoints/lines",
    "/docs/endpoints/matches",
    "/docs/endpoints/players",
    "/docs/endpoints/rankings",
    "/docs/endpoints/results",
    "/docs/endpoints/research",
    "/docs/endpoints/history",
    "/console",
  ]
  return routes.map((path) => ({
    url: path === "/" ? base : `${base}${path}`,
    lastModified: new Date(),
    changeFrequency: path === "/" ? "daily" : "weekly",
    priority:
      path === "/"
        ? 1
        : path === "/pricing" ||
            path === "/build-esports-app" ||
            path === "/quickstart"
          ? 0.9
          : path === "/console"
            ? 0.7
            : 0.8,
  }))
}

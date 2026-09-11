import type { MetadataRoute } from "next"

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://www.kashrock.com"
  const routes = [
    "/",
    "/esports-data-api",
    "/dfs-esports-api",
    "/cs2-props-api",
    "/esports-odds-api",
    "/prizepicks-api",
    "/underdog-api",
    "/sleeper-api",
    "/betr-api",
    "/coverage",
    "/historical-esports-data-api",
    "/blog/how-to-get-prizepicks-props-api",
    "/blog/cs2-player-props-without-scraping",
    "/abios-alternative",
    "/pandascore-alternative",
    "/mcp",
    "/docs",
    "/console",
  ]
  return routes.map((path) => ({
    url: path === "/" ? base : `${base}${path}`,
    lastModified: new Date(),
    changeFrequency: path === "/" ? "daily" : "weekly",
    priority: path === "/" ? 1 : path === "/console" ? 0.7 : 0.8,
  }))
}

import type { MetadataRoute } from "next"

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://www.kashrock.com"
  const routes = [
    "/",
    "/esports-data-api",
    "/dfs-esports-api",
    "/cs2-props-api",
    "/esports-odds-api",
    "/abios-alternative",
    "/pandascore-alternative",
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

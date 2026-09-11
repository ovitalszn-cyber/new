/** Edge-safe JWT helpers — decode only, no signature verify. */

function decodeJwtPayloadJson(token: string): string | null {
  const raw = token.trim()
  if (!raw) return null
  const parts = raw.split(".")
  if (parts.length < 2) return null
  try {
    const part = parts[1]
    const padded = part + "=".repeat((4 - (part.length % 4)) % 4)
    const b64 = padded.replace(/-/g, "+").replace(/_/g, "/")
    if (typeof atob === "function") {
      return atob(b64)
    }
    return Buffer.from(part, "base64url").toString("utf8")
  } catch {
    return null
  }
}

export function jwtExpiresAt(token: string | undefined | null): number | null {
  const json = decodeJwtPayloadJson(token || "")
  if (!json) return null
  try {
    const payload = JSON.parse(json) as { exp?: unknown }
    const exp = Number(payload.exp)
    return Number.isFinite(exp) ? exp : null
  } catch {
    return null
  }
}

export function jwtUnexpired(
  token: string | undefined | null,
  skewSeconds = 30,
): boolean {
  const exp = jwtExpiresAt(token)
  if (exp === null) return false
  return exp > Math.floor(Date.now() / 1000) + skewSeconds
}

export function hasUsableSessionCookies(input: {
  access?: string
  refresh?: string
}): boolean {
  if (jwtUnexpired(input.access)) return true
  if (jwtUnexpired(input.refresh)) return true
  return false
}

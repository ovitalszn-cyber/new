/**
 * Local proofs for auth friction fixes. Run: npx tsx scripts/prove-auth-friction.ts
 * Or: node --import tsx scripts/prove-auth-friction.ts
 */
import assert from "node:assert/strict"
import { createKeyDeliveryHtml } from "../lib/auth/key-delivery"
import {
  AUTH_COMPLETE_KEY,
  AUTH_COMPLETE_RETURN,
} from "../lib/auth/complete-storage"
import {
  hasUsableSessionCookies,
  jwtUnexpired,
} from "../lib/auth/jwt"
import { safeReturnTo } from "../lib/auth/navigation"

function fakeJwt(exp: number) {
  const header = Buffer.from(JSON.stringify({ alg: "none", typ: "JWT" })).toString(
    "base64url",
  )
  const payload = Buffer.from(JSON.stringify({ exp, type: "access" })).toString(
    "base64url",
  )
  return `${header}.${payload}.sig`
}

function main() {
  const now = Math.floor(Date.now() / 1000)
  assert.equal(jwtUnexpired(fakeJwt(now + 3600)), true)
  assert.equal(jwtUnexpired(fakeJwt(now - 60)), false)
  assert.equal(jwtUnexpired("not-a-jwt"), false)
  assert.equal(
    hasUsableSessionCookies({ access: fakeJwt(now - 10), refresh: fakeJwt(now + 100) }),
    true,
  )
  assert.equal(
    hasUsableSessionCookies({ access: fakeJwt(now - 10), refresh: fakeJwt(now - 5) }),
    false,
  )
  assert.equal(safeReturnTo("/login"), "/console")
  assert.equal(safeReturnTo("/console?x=1"), "/console?x=1")

  const delivery = createKeyDeliveryHtml("kr_live_test_key", "/console")
  assert.match(delivery.html, new RegExp(AUTH_COMPLETE_KEY))
  assert.match(delivery.html, new RegExp(AUTH_COMPLETE_RETURN))
  assert.match(delivery.html, /history\.replaceState\(\{\}, '', '\/auth\/complete'\)/)
  assert.match(delivery.html, /sessionStorage\.setItem/)
  assert.match(delivery.html, /kr_live_test_key/)

  console.log("prove-auth-friction: OK")
}

main()

import {
  createHash,
  createPublicKey,
  randomBytes,
  timingSafeEqual,
  verify,
  type JsonWebKey as CryptoJsonWebKey,
} from 'node:crypto'

import { requireGoogleConfig } from './config'

interface GoogleTokenResponse {
  id_token?: string
  error_description?: string
}

interface GoogleClaims {
  aud: string
  exp: number
  iss: string
  email_verified?: boolean
  nonce?: string
}

interface GoogleKeySet {
  keys: Array<CryptoJsonWebKey & { kid?: string }>
}

function base64url(bytes: Buffer) {
  return bytes.toString('base64url')
}

export function createOAuthValues() {
  const verifier = base64url(randomBytes(32))
  return {
    state: base64url(randomBytes(32)),
    nonce: base64url(randomBytes(32)),
    verifier,
    challenge: base64url(createHash('sha256').update(verifier).digest()),
  }
}

export function secureEqual(left: string, right: string) {
  const leftBuffer = Buffer.from(left)
  const rightBuffer = Buffer.from(right)
  return (
    leftBuffer.length === rightBuffer.length &&
    timingSafeEqual(leftBuffer, rightBuffer)
  )
}

export function buildGoogleAuthorizationUrl(
  redirectUri: string,
  values: ReturnType<typeof createOAuthValues>,
) {
  const { clientId } = requireGoogleConfig()
  const url = new URL('https://accounts.google.com/o/oauth2/v2/auth')
  url.search = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: 'openid email profile',
    state: values.state,
    nonce: values.nonce,
    code_challenge: values.challenge,
    code_challenge_method: 'S256',
    prompt: 'select_account',
  }).toString()
  return url
}

export async function exchangeGoogleCode(
  code: string,
  verifier: string,
  redirectUri: string,
) {
  const { clientId, clientSecret } = requireGoogleConfig()
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
      grant_type: 'authorization_code',
      code_verifier: verifier,
    }),
    cache: 'no-store',
  })
  const result = (await response.json()) as GoogleTokenResponse
  if (!response.ok || !result.id_token) {
    throw new Error(result.error_description ?? 'Google token exchange failed')
  }
  return result.id_token
}

function decodeJwtPart<T>(part: string) {
  return JSON.parse(Buffer.from(part, 'base64url').toString()) as T
}

async function verifySignature(idToken: string) {
  const [headerPart, payloadPart, signaturePart] = idToken.split('.')
  if (!headerPart || !payloadPart || !signaturePart) return null
  const header = decodeJwtPart<{ alg?: string; kid?: string }>(headerPart)
  if (header.alg !== 'RS256' || !header.kid) return null
  const response = await fetch('https://www.googleapis.com/oauth2/v3/certs', {
    cache: 'no-store',
  })
  if (!response.ok) throw new Error('Unable to load Google signing keys')
  const keySet = (await response.json()) as GoogleKeySet
  const jwk = keySet.keys.find((key) => key.kid === header.kid)
  if (!jwk) return null
  const valid = verify(
    'RSA-SHA256',
    Buffer.from(`${headerPart}.${payloadPart}`),
    createPublicKey({ key: jwk, format: 'jwk' }),
    Buffer.from(signaturePart, 'base64url'),
  )
  return valid ? decodeJwtPart<GoogleClaims>(payloadPart) : null
}

export async function validateGoogleIdToken(idToken: string, nonce: string) {
  const { clientId } = requireGoogleConfig()
  const claims = await verifySignature(idToken)
  const issuerValid =
    claims?.iss === 'https://accounts.google.com' ||
    claims?.iss === 'accounts.google.com'
  const valid =
    claims &&
    issuerValid &&
    claims.aud === clientId &&
    claims.email_verified === true &&
    claims.exp > Math.floor(Date.now() / 1000) &&
    claims.nonce === nonce
  if (!valid) throw new Error('Google identity validation failed')
}

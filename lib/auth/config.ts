const DEFAULT_BACKEND_URL = 'http://localhost:8000'

export const authConfig = {
  backendUrl:
    process.env.API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    DEFAULT_BACKEND_URL,
  appUrl: process.env.APP_URL,
  googleClientId: process.env.GOOGLE_CLIENT_ID ?? '',
  googleClientSecret: process.env.GOOGLE_CLIENT_SECRET ?? '',
}

export function requireGoogleConfig() {
  if (!authConfig.googleClientId || !authConfig.googleClientSecret) {
    throw new Error('Google OAuth is not configured')
  }
  return {
    clientId: authConfig.googleClientId,
    clientSecret: authConfig.googleClientSecret,
  }
}

export function getRequestOrigin(requestUrl: string) {
  return authConfig.appUrl ?? new URL(requestUrl).origin
}

export function backendUrl(path: string) {
  return `${authConfig.backendUrl.replace(/\/$/, '')}/v1/dev${path}`
}

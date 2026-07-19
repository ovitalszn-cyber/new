const ALLOWED_RETURN_PREFIXES = ['/console', '/settings', '/checkout']

export function safeReturnTo(value: string | null | undefined) {
  if (!value || !value.startsWith('/') || value.startsWith('//')) {
    return '/console'
  }
  const pathname = value.split('?')[0]
  return ALLOWED_RETURN_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  )
    ? value
    : '/console'
}

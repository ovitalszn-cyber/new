import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { saveSessionTokens, clearSessionTokens } from './auth-storage'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Single shared instance
let _supabaseInstance: SupabaseClient | null = null

function createSupabaseClient() {
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error('[Supabase] Missing environment variables')
    return null
  }

  const client = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
      flowType: 'implicit',
      debug: process.env.NODE_ENV === 'development',
      storage: typeof window !== 'undefined' ? window.localStorage : undefined,
      storageKey: 'supabase.auth.token'
    }
  })

  // Listen for auth state changes
  if (typeof window !== 'undefined') {
    client.auth.onAuthStateChange((event, session) => {
      console.log('[Supabase] Auth state change:', event, session?.user?.email || 'no session')
      if (session) {
        saveSessionTokens(session)
      } else if (event === 'SIGNED_OUT') {
        clearSessionTokens()
      }
    })
  }

  return client
}

// Initialize once on client side
if (typeof window !== 'undefined' && !_supabaseInstance) {
  _supabaseInstance = createSupabaseClient()
  console.log('[Supabase] Client initialized')
}

export const getSupabase = () => {
  if (!_supabaseInstance && typeof window !== 'undefined') {
    _supabaseInstance = createSupabaseClient()
  }
  return _supabaseInstance
}

export const supabase = _supabaseInstance || (null as unknown as SupabaseClient)

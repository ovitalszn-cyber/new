import { createClient, SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Create a lazy-loaded supabase client to avoid build-time errors
let _supabase: SupabaseClient | null = null

export const getSupabase = () => {
  if (!_supabase && supabaseUrl && supabaseAnonKey) {
    _supabase = createClient(supabaseUrl, supabaseAnonKey)
  }
  return _supabase
}

// For backwards compatibility - will be null during build if env vars missing
export const supabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null as unknown as SupabaseClient

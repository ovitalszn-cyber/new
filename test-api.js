// Test script to verify API authentication
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://wleoennwnjvhvtbquimh.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsZW9lbm53bmp2aHZ0YnF1aW1oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0Njg1MzEsImV4cCI6MjA4MTA0NDUzMX0.nnn7gSYklXX1rE8eWQ-THrw3V75pGkF33IkZYe8sjgM';

const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    flowType: 'pkce'
  }
});

async function testAuthFlow() {
  console.log('Testing Supabase auth...');
  
  // Test 1: Check if we can create a session
  try {
    const { data, error } = await supabase.auth.getSession();
    console.log('Session check:', {
      hasSession: !!data.session,
      error: error?.message
    });
    
    if (data.session) {
      console.log('Session found:', {
        email: data.session.user.email,
        hasAccessToken: !!data.session.access_token,
        tokenPreview: data.session.access_token ? data.session.access_token.substring(0, 50) + '...' : 'none'
      });
      
      // Test 2: Try to use the token to call the backend
      const response = await fetch('https://api.kashrock.com/v1/dev/usage/summary', {
        headers: {
          'Authorization': `Bearer ${data.session.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('API Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        const text = await response.text();
        console.log('Error body:', text);
      }
    }
  } catch (e) {
    console.error('Test failed:', e);
  }
}

testAuthFlow();

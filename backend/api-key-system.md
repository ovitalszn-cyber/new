+ 1. User signs in with Google


Dashboard is protected. No one gets in without OAuth.

Google returns:

email
Google user ID
name (optional)


Your backend receives the OAuth token → verifies it → creates a user record if it doesn’t already exist.

Result:
You now have a guaranteed unique user in your database.



2. Store them in your users table


Your users table contains:

id (your internal user ID)
google_id
email
created_at
plan/tier (future)


This is the anchor for EVERYTHING that happens next.

Result:
You always know exactly who is making requests.



3. When they generate an API key


They must already be signed in with Google.
The dashboard sends a “create key” request → backend sees their user ID → assigns the key to them.

api_keys table includes:

id
user_id
hashed_key
created_at
last_used_at
status


Result:
Every key is tied to a real user.



4. When they call the API


Middleware receives the raw key:

Hash it
Look up the key
Find the associated user_id
Attach the user_id to the request context
Track usage under that user


Result:
You know exactly which user made the call even if they have multiple keys.



5. Dashboard = purely user-scoped


Because they authenticated with Google, your backend can:

Fetch their keys
Show usage per key
Show total calls
Manage revokes
Manage rotations


Result:
No confusion. Every dashboard session is mapped to one real, verified user.



6. Why Google Sign-In is the best move


Zero friction for developers
No passwords → no headache
You get validated emails
Prevents spammers + fake signups
Easiest way to map identity → usage → billing


This is how Stripe, Vercel, Supabase, and all serious dev tools play it.

# KashRock API (Beginner Friendly)

Welcome! This guide assumes you've never used an API before. Follow the steps below to test the API on Render and make your first request in a few minutes.

## What is this?

- An API is a program you can ask for data using simple URLs.
- The KashRock API gives you sports markets and player props from multiple books.
- **This API is hosted on Render** - no local installation required!

## You'll need

- A web browser or terminal
- curl (usually already installed on macOS/Linux/Windows)
- Optional: `jq` for pretty-printing JSON (`brew install jq` on macOS)
- **Your API key** (contact admin for access)

## Step 1: Get your API key

Contact the admin to receive your personal API key for testing.

## Step 2: Test the API health

Check if the service is running:

```bash
curl -s https://kashrock-api.onrender.com/health | jq
```

You should get a small JSON response showing the service is healthy.

## Step 3: Your first API call (with auth header)

All endpoints require an Authorization header with your API key.

Fetch upcoming markets from a specific book (here: ProphetX, NFL):

```bash
curl -s 'https://kashrock-api.onrender.com/v1/odds/upcoming?sport=football_nfl&books=prophetx' \
  -H 'Authorization: Bearer YOUR_API_KEY' | jq
```

Try NBA from PrizePicks and NoVig:

```bash
curl -s 'https://kashrock-api.onrender.com/v1/odds/upcoming?sport=basketball_nba&books=prizepicks&books=novig' \
  -H 'Authorization: Bearer YOUR_API_KEY' | jq
```

What you'll see:
- A top-level object with `sport`, `books`, and `generated_at`.
- Inside `books`, each selected book returns its own raw payload.

## Changing the sport or book

- Change `sport=` to one of: `football_nfl`, `football_ncaaf`, `basketball_nba`, `basketball_wnba`, `baseball_mlb`.
- Add or change `books=` to one or more of: `novig`, `prophetx`, `splashsports`, `prizepicks`, `dabble`, `bovada`, `betonline`, `rebet`, `propscash`, `hardrock`.

Example (WNBA from NoVig):

```bash
curl -s 'https://kashrock-api.onrender.com/v1/odds/upcoming?sport=basketball_wnba&books=novig' \
  -H 'Authorization: Bearer YOUR_API_KEY' | jq
```

## Optional: Use Postman (no code)

1. Open Postman (or Insomnia)
2. Create a GET request to: `https://kashrock-api.onrender.com/v1/odds/upcoming?sport=football_nfl&books=prophetx`
3. Headers tab → add `Authorization` with value `Bearer YOUR_API_KEY`
4. Send. You'll see a JSON response in the right pane.

## Troubleshooting

- 401 Unauthorized: Add the header `Authorization: Bearer YOUR_API_KEY` to your request.
- 503 or empty data for a book: Some books require live sessions or may have no markets at that moment. Try another book or sport.
- Pretty printing not working: Install jq (`brew install jq`) or remove `| jq` from the command.
- Slow responses: Render free tier has cold starts; first request may take 30+ seconds.

## Where to find more endpoints

See the detailed guide with more examples and book-specific endpoints:
- `docs/USAGE.md`

That file shows how to call individual book routes under `/api/v1/streams/...` if you want to go deeper.

## Safety & sharing

- **Never share your API key publicly.**
- Each user gets a unique API key for testing.
- API keys are rate-limited to prevent abuse.

## New: HardRock WNBA Support

The API now includes comprehensive WNBA data from HardRock Sportsbook:

```bash
curl -s 'https://kashrock-api.onrender.com/v1/odds/upcoming?sport=basketball_wnba&books=hardrock' \
  -H 'Authorization: Bearer YOUR_API_KEY' | jq
```

This includes:
- Team futures (Winner, Season Wins, Playoffs)
- Player props (Points, Assists, Rebounds, Three-pointers)
- Awards markets (MVP, Coach of Year, Rookie of Year)

You're set! If you can run the curl examples above and see JSON, you're successfully using an API.

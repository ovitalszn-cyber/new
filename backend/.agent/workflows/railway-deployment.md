---
description: Deploy KashRock API to Railway with Historical Database Volume
---

# Railway Deployment Guide for KashRock API

This workflow deploys the KashRock API to Railway with the 11GB historical SQLite database mounted on a persistent volume.

## Prerequisites

1. Railway account with CLI installed: `npm install -g @railway/cli`
2. GitHub repository pushed and accessible
3. Local `kashrock_historical.db` file (11GB) ready for upload
4. Railway project created

## Step 1: Install Railway CLI (if not already installed)

```bash
npm install -g @railway/cli
```

## Step 2: Login to Railway

```bash
railway login
```

## Step 3: Initialize Railway Project

```bash
cd /Users/drax/Downloads/kashrock-main
railway init
```

Select or create a new project when prompted.

## Step 4: Create Persistent Volume for Historical Database

```bash
railway volume create kashrock-historical-db --mount-path /data
```

This creates a persistent volume mounted at `/data` in the container.

## Step 5: Link the Volume to Your Service

In Railway dashboard:
1. Go to your project
2. Click on your service
3. Go to "Variables" tab
4. Add environment variable: `HISTORICAL_DB_PATH=/data/kashrock_historical.db`

Or via CLI:
```bash
railway variables set HISTORICAL_DB_PATH=/data/kashrock_historical.db
```

## Step 6: Configure Environment Variables

Set all required environment variables:

```bash
# Core configuration
railway variables set PORT=8000
railway variables set HOST=0.0.0.0
railway variables set WORKERS=2
railway variables set DEBUG=false

# Database URLs (Railway will provide DATABASE_URL for PostgreSQL)
railway variables set REDIS_URL=<your-redis-url>

# API Keys
railway variables set ODDS_API_KEY=<your-odds-api-key>
railway variables set ESPN_API_KEY=<your-espn-api-key>

# Security
railway variables set SECRET_KEY=<generate-strong-secret>
railway variables set ADMIN_SECRET=<generate-admin-secret>
railway variables set GOOGLE_CLIENT_ID=<your-google-client-id>

# Historical Database Path (already set above)
# HISTORICAL_DB_PATH=/data/kashrock_historical.db
```

## Step 7: Update Code to Use Volume-Mounted Database

The code needs to check for the `HISTORICAL_DB_PATH` environment variable and use it instead of the local file path.

Update `v6/historical/database.py` to use:
```python
import os
db_path = os.getenv("HISTORICAL_DB_PATH", "kashrock_historical.db")
database_url = f"sqlite+aiosqlite:///{db_path}"
```

## Step 8: Deploy to Railway (Initial Deployment)

```bash
railway up
```

This will:
- Build the Docker container using your Dockerfile
- Deploy to Railway
- The volume will be mounted but empty initially

## Step 9: Upload Historical Database to Volume

**Option A: Using Railway CLI (Recommended)**

1. Get a shell into the running container:
```bash
railway run bash
```

2. From your local machine, use `scp` or Railway's file upload:
```bash
# This requires the Railway service to be running
railway run --service <service-name> -- bash -c "cat > /data/kashrock_historical.db" < kashrock_historical.db
```

**Option B: Using Railway Dashboard**

1. Stop the service temporarily
2. Use Railway's volume management interface to upload the file
3. Restart the service

**Option C: Using a One-Time Upload Script (Most Reliable)**

Create a temporary upload service:

1. Create `scripts/upload_historical_db.py`:
```python
#!/usr/bin/env python3
"""Upload historical database to Railway volume."""
import os
import sys
from pathlib import Path

def upload_db():
    source = Path("kashrock_historical.db")
    target = Path(os.getenv("HISTORICAL_DB_PATH", "/data/kashrock_historical.db"))
    
    if not source.exists():
        print(f"Source file not found: {source}")
        sys.exit(1)
    
    print(f"Uploading {source} ({source.stat().st_size / 1e9:.2f} GB) to {target}...")
    
    # Ensure target directory exists
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file in chunks
    chunk_size = 1024 * 1024 * 10  # 10MB chunks
    with open(source, 'rb') as src, open(target, 'wb') as dst:
        while True:
            chunk = src.read(chunk_size)
            if not chunk:
                break
            dst.write(chunk)
            print(".", end="", flush=True)
    
    print(f"\nUpload complete! File size: {target.stat().st_size / 1e9:.2f} GB")

if __name__ == "__main__":
    upload_db()
```

2. Deploy with this script as the start command temporarily:
```bash
railway run python scripts/upload_historical_db.py
```

## Step 10: Verify Database Upload

Check that the database is accessible:

```bash
railway run ls -lh /data/
```

You should see `kashrock_historical.db` with ~11GB size.

## Step 11: Update Dockerfile for Production

Ensure the Dockerfile doesn't copy the large database file:

Update `.dockerignore`:
```
kashrock_historical.db
*.db
!db/auth.db
```

## Step 12: Deploy Final Configuration

```bash
railway up --detach
```

## Step 13: Run Smoke Tests

Test the API endpoints that use historical data:

```bash
# Get the Railway URL
RAILWAY_URL=$(railway status --json | jq -r '.url')

# Test historical data endpoint
curl -H "Authorization: Bearer <your-api-key>" \
  "$RAILWAY_URL/v6/historical/games?sport=nba&limit=10"

# Test box scores
curl -H "Authorization: Bearer <your-api-key>" \
  "$RAILWAY_URL/v6/boxscore/401584876?sport=nba"

# Test esports matches
curl -H "Authorization: Bearer <your-api-key>" \
  "$RAILWAY_URL/v6/esports/matches?discipline=lol&limit=10"
```

## Step 14: Monitor Resource Usage

Monitor the deployment during the 2 PM tester wave:

```bash
# View logs
railway logs

# Monitor metrics in Railway dashboard
# - CPU usage
# - Memory usage
# - Disk I/O
# - Response times
```

## Step 15: Set Up Monitoring Alerts

In Railway dashboard:
1. Go to Settings → Notifications
2. Set up alerts for:
   - High CPU usage (>80%)
   - High memory usage (>80%)
   - Service crashes
   - High error rates

## Troubleshooting

### Database File Not Found
- Verify volume is mounted: `railway run ls -la /data`
- Check environment variable: `railway run env | grep HISTORICAL_DB_PATH`

### Out of Memory
- Increase Railway plan or optimize queries
- Add connection pooling limits in database.py

### Slow Read Performance
- Ensure SQLite is in WAL mode for better concurrency
- Add indexes to frequently queried tables
- Consider upgrading to PostgreSQL for production

### Volume Full
- Check volume size: `railway run df -h /data`
- Increase volume size in Railway dashboard

## Production Optimizations

1. **Enable SQLite WAL Mode** (in database.py):
```python
await conn.execute(text("PRAGMA journal_mode=WAL"))
await conn.execute(text("PRAGMA synchronous=NORMAL"))
```

2. **Add Read-Only Mode** for historical DB:
```python
database_url = f"sqlite+aiosqlite:///{db_path}?mode=ro"
```

3. **Connection Pooling**:
```python
# Already configured in database.py for non-SQLite
pool_size=10
max_overflow=20
```

4. **Caching Layer**:
- Historical data rarely changes
- Add Redis caching for frequently accessed queries

## Backup Strategy

1. **Automated Backups**:
```bash
# Set up daily backups via Railway cron job
railway run --cron "0 2 * * *" -- bash -c "cp /data/kashrock_historical.db /data/backups/kashrock_historical_$(date +%Y%m%d).db"
```

2. **Manual Backup**:
```bash
railway run cat /data/kashrock_historical.db > kashrock_historical_backup.db
```

## Scaling Considerations

- **Read Replicas**: Consider PostgreSQL for better scaling
- **CDN**: Cache static historical data via CDN
- **Sharding**: Split by sport/date if database grows beyond 50GB
- **Archive Old Data**: Move data older than 2 years to cold storage

## Cost Optimization

- Railway volume pricing: ~$0.25/GB/month
- 11GB volume = ~$2.75/month
- Consider compressing old data or archiving to S3

## Next Steps

1. Set up CI/CD pipeline for automatic deployments
2. Configure custom domain
3. Set up SSL/TLS certificates
4. Implement rate limiting
5. Add comprehensive logging and monitoring

#!/usr/bin/env python3
"""
Upload database via Railway shell.
This script is meant to be run INSIDE the Railway container.
"""
import os
import sys
from pathlib import Path

# Check if we're in Railway environment
if not os.path.exists('/data'):
    print("❌ Error: /data directory not found")
    print("This script must be run inside the Railway container")
    print("\nTo upload the database:")
    print("1. Use Railway dashboard to upload the file directly to the volume")
    print("2. Or use railway shell and scp/wget to transfer the file")
    sys.exit(1)

print("✅ /data directory exists")
print(f"📊 Available space: {os.statvfs('/data').f_bavail * os.statvfs('/data').f_frsize / (1024**3):.2f} GB")

# Check if database already exists
db_path = Path("/data/kashrock_historical.db")
if db_path.exists():
    size_gb = db_path.stat().st_size / (1024**3)
    print(f"✅ Database already exists: {size_gb:.2f} GB")
else:
    print("⚠️  Database not found at /data/kashrock_historical.db")
    print("Please upload the database file to the volume")

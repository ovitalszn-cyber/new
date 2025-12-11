#!/usr/bin/env python3
"""
Upload historical database to Railway volume.

This script uploads the large kashrock_historical.db file to the Railway
persistent volume mounted at /data.

Usage:
    python scripts/upload_historical_db.py [--source PATH] [--target PATH]
"""

import os
import sys
from pathlib import Path
import argparse
import time


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def upload_db(source_path: str, target_path: str, chunk_size: int = 10 * 1024 * 1024):
    """
    Upload database file to Railway volume.
    
    Args:
        source_path: Path to source database file
        target_path: Path to target location on volume
        chunk_size: Size of chunks to read/write (default 10MB)
    """
    source = Path(source_path)
    target = Path(target_path)
    
    # Validate source file
    if not source.exists():
        print(f"❌ Source file not found: {source}")
        sys.exit(1)
    
    if not source.is_file():
        print(f"❌ Source is not a file: {source}")
        sys.exit(1)
    
    source_size = source.stat().st_size
    print(f"📁 Source: {source}")
    print(f"📊 Size: {format_size(source_size)}")
    print(f"🎯 Target: {target}")
    print()
    
    # Ensure target directory exists
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if target already exists
    if target.exists():
        target_size = target.stat().st_size
        print(f"⚠️  Target file already exists ({format_size(target_size)})")
        response = input("Overwrite? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Upload cancelled")
            sys.exit(0)
        print()
    
    # Upload with progress
    print(f"🚀 Starting upload...")
    start_time = time.time()
    bytes_written = 0
    
    try:
        with open(source, 'rb') as src, open(target, 'wb') as dst:
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                
                dst.write(chunk)
                bytes_written += len(chunk)
                
                # Progress indicator
                progress = (bytes_written / source_size) * 100
                elapsed = time.time() - start_time
                speed = bytes_written / elapsed if elapsed > 0 else 0
                
                print(
                    f"\r📤 Progress: {progress:.1f}% "
                    f"({format_size(bytes_written)}/{format_size(source_size)}) "
                    f"@ {format_size(speed)}/s",
                    end='',
                    flush=True
                )
        
        print()  # New line after progress
        
        # Verify upload
        target_size = target.stat().st_size
        elapsed = time.time() - start_time
        
        if target_size == source_size:
            print(f"✅ Upload complete!")
            print(f"📊 Uploaded: {format_size(target_size)}")
            print(f"⏱️  Time: {elapsed:.1f}s")
            print(f"🚄 Average speed: {format_size(target_size / elapsed)}/s")
            
            # Set read-only permissions for safety
            target.chmod(0o444)
            print(f"🔒 Set read-only permissions on target file")
            
        else:
            print(f"❌ Upload failed: size mismatch")
            print(f"   Expected: {format_size(source_size)}")
            print(f"   Got: {format_size(target_size)}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Upload interrupted by user")
        if target.exists():
            target.unlink()
            print("🗑️  Cleaned up partial file")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        if target.exists():
            target.unlink()
            print("🗑️  Cleaned up partial file")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Upload historical database to Railway volume"
    )
    parser.add_argument(
        '--source',
        default='kashrock_historical.db',
        help='Path to source database file (default: kashrock_historical.db)'
    )
    parser.add_argument(
        '--target',
        default=None,
        help='Path to target location (default: from HISTORICAL_DB_PATH env var or /data/kashrock_historical.db)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=10 * 1024 * 1024,
        help='Chunk size in bytes (default: 10MB)'
    )
    
    args = parser.parse_args()
    
    # Determine target path
    if args.target:
        target_path = args.target
    else:
        target_path = os.getenv(
            'HISTORICAL_DB_PATH',
            '/data/kashrock_historical.db'
        )
    
    print("=" * 60)
    print("📦 KashRock Historical Database Upload")
    print("=" * 60)
    print()
    
    upload_db(args.source, target_path, args.chunk_size)
    
    print()
    print("=" * 60)
    print("✨ Upload complete! Database is ready for use.")
    print("=" * 60)


if __name__ == "__main__":
    main()

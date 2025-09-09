#!/usr/bin/env python3
"""
Database verification script for Railway deployment.
"""

import sys
import os
import sqlite3
from pathlib import Path

def verify_database():
    """Verify database setup on Railway."""
    print("🔍 Verifying Database Setup on Railway")
    print("=" * 50)
    
    # Check environment variables
    print("🔧 Environment Variables:")
    db_path = os.getenv('DATABASE_PATH', '/app/reading_tracker.db')
    print(f"  DATABASE_PATH: {db_path}")
    print(f"  BOT_TOKEN: {'Set' if os.getenv('BOT_TOKEN') else 'Not set'}")
    print(f"  ADMIN_USER_IDS: {os.getenv('ADMIN_USER_IDS', 'Not set')}")
    print()
    
    # Check if database file exists
    print("📁 Database File Check:")
    print(f"  Path: {db_path}")
    print(f"  Exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print(f"  Size: {os.path.getsize(db_path):,} bytes")
        print(f"  Readable: {os.access(db_path, os.R_OK)}")
        print(f"  Writable: {os.access(db_path, os.W_OK)}")
    else:
        print("  ❌ Database file does not exist!")
        print("  🔄 Attempting to create database file...")
        
        try:
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Directory created: {Path(db_path).parent}")
            
            # Create database file
            conn = sqlite3.connect(db_path)
            conn.close()
            print(f"  ✅ Database file created: {db_path}")
            
        except Exception as e:
            print(f"  ❌ Failed to create database file: {e}")
            return False
    
    print()
    
    # Check database tables
    print("🗂️ Database Tables Check:")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"  Found {len(tables)} tables:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"    • {table_name}: {count} records")
        else:
            print("  ❌ No tables found in database!")
            print("  🔄 Database needs to be initialized")
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ Error checking database tables: {e}")
        return False
    
    print()
    print("✅ Database verification completed!")
    return True

if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)

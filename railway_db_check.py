#!/usr/bin/env python3
"""
Railway Database Check Script
This script can be run on Railway to check the database.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def check_railway_database():
    """Check database on Railway deployment."""
    print("🚀 Railway Database Check")
    print("=" * 40)
    
    # Check environment variables
    print("🔧 Environment Variables:")
    print(f"  DATABASE_PATH: {os.getenv('DATABASE_PATH', 'Not set')}")
    print(f"  BOT_TOKEN: {'Set' if os.getenv('BOT_TOKEN') else 'Not set'}")
    print(f"  ADMIN_USER_IDS: {os.getenv('ADMIN_USER_IDS', 'Not set')}")
    print()
    
    try:
        from src.database.database import db_manager
        
        # Check if database file exists
        db_path = db_manager.db_path
        print(f"📁 Database Path: {db_path}")
        print(f"📁 Database Exists: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            print(f"💾 Database Size: {os.path.getsize(db_path):,} bytes")
        
        print()
        
        # Get database info
        info = db_manager.get_database_info()
        
        print("📊 Database Information:")
        print(f"  Size: {info.get('database_size_mb', 0)} MB")
        print()
        
        # Check table counts
        table_counts = info.get('table_counts', {})
        if table_counts:
            print("📋 Table Records:")
            for table, count in table_counts.items():
                print(f"  • {table}: {count} records")
        else:
            print("❌ No table information found")
        
        print()
        print("✅ Railway database check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking Railway database: {e}")
        return False

if __name__ == "__main__":
    check_railway_database()

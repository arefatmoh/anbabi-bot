#!/usr/bin/env python3
"""
Database inspection script for Read & Revive Bot.
Run this to check your database tables and data.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.database import db_manager

def check_database():
    """Check database tables and data."""
    print("🔍 Checking Read & Revive Bot Database...")
    print("=" * 50)
    
    try:
        # Get database info
        info = db_manager.get_database_info()
        
        print(f"📁 Database Path: {info.get('database_path', 'Unknown')}")
        print(f"💾 Database Size: {info.get('database_size_mb', 0)} MB")
        print()
        
        # Check table counts
        table_counts = info.get('table_counts', {})
        if table_counts:
            print("📋 Table Information:")
            for table, count in table_counts.items():
                print(f"  • {table}: {count} records")
        else:
            print("❌ No table information found")
        
        print()
        
        # Test database connection
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"🗂️  Found {len(tables)} tables:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  • {table_name}: {count} records")
        
        print()
        print("✅ Database check completed successfully!")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)

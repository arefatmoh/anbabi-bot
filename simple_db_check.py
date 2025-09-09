#!/usr/bin/env python3
"""
Simple database check script.
"""

import sqlite3
import os

def check_database():
    """Simple database check."""
    db_file = "reading_tracker.db"
    
    if not os.path.exists(db_file):
        print(f"❌ Database file '{db_file}' not found!")
        return False
    
    print(f"✅ Database file '{db_file}' exists!")
    print(f"📁 File size: {os.path.getsize(db_file)} bytes")
    print()
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"🗂️ Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  • {table_name}: {count} records")
        
        conn.close()
        print("\n✅ Database check completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_database()

#!/usr/bin/env python3
"""
Detailed database inspection script.
"""

import sqlite3
import os
from datetime import datetime

def detailed_database_check():
    """Detailed database inspection."""
    db_file = "reading_tracker.db"
    
    if not os.path.exists(db_file):
        print(f"❌ Database file '{db_file}' not found!")
        return False
    
    print("🔍 Detailed Database Inspection")
    print("=" * 50)
    print(f"📁 Database: {db_file}")
    print(f"💾 Size: {os.path.getsize(db_file):,} bytes")
    print(f"📅 Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables with detailed info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"🗂️ Database Tables ({len(tables)} total):")
        print("-" * 30)
        
        total_records = 0
        for table in tables:
            table_name = table[0]
            
            # Skip system tables
            if table_name.startswith('sqlite_'):
                continue
                
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"📋 {table_name}: {count} records")
            print(f"   Columns: {len(columns)}")
            
            # Show sample data for key tables
            if table_name in ['users', 'books', 'leagues'] and count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    print(f"   Sample: {sample[:2]}...")  # Show first 2 fields
            print()
        
        print(f"📊 Total Records: {total_records:,}")
        print()
        
        # Check specific important data
        print("🎯 Key Data Check:")
        print("-" * 20)
        
        # Users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Users: {user_count}")
        
        # Books
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        print(f"📚 Books: {book_count}")
        
        # Active leagues
        cursor.execute("SELECT COUNT(*) FROM leagues WHERE status = 'active'")
        active_leagues = cursor.fetchone()[0]
        print(f"🏆 Active Leagues: {active_leagues}")
        
        # Recent reading sessions
        cursor.execute("SELECT COUNT(*) FROM reading_sessions WHERE session_date >= date('now', '-7 days')")
        recent_sessions = cursor.fetchone()[0]
        print(f"📖 Recent Sessions (7 days): {recent_sessions}")
        
        # Achievements
        cursor.execute("SELECT COUNT(*) FROM achievements")
        achievements = cursor.fetchone()[0]
        print(f"🏅 Achievements: {achievements}")
        
        conn.close()
        print()
        print("✅ Detailed database check completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    detailed_database_check()

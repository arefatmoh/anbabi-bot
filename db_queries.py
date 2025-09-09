#!/usr/bin/env python3
"""
Database query script for Read & Revive Bot.
"""

import sqlite3
import sys

def run_query(query, description=""):
    """Run a database query and display results."""
    try:
        conn = sqlite3.connect('reading_tracker.db')
        cursor = conn.cursor()
        
        if description:
            print(f"\n🔍 {description}")
            print("-" * 40)
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            # Get column names
            columns = [description[0] for description in cursor.description]
            print(f"Columns: {', '.join(columns)}")
            print()
            
            for row in results:
                print(row)
        else:
            print("No results found.")
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main function with common queries."""
    print("🔍 Read & Revive Bot - Database Queries")
    print("=" * 50)
    
    # Common queries
    queries = [
        ("SELECT user_id, full_name, nickname, city FROM users LIMIT 5", "Recent Users"),
        ("SELECT title, author, total_pages FROM books LIMIT 5", "Featured Books"),
        ("SELECT name, status, daily_goal FROM leagues", "All Leagues"),
        ("SELECT user_id, book_id, pages_read, status FROM user_books LIMIT 5", "User Reading Progress"),
        ("SELECT user_id, session_date, pages_read FROM reading_sessions ORDER BY session_date DESC LIMIT 5", "Recent Reading Sessions"),
        ("SELECT user_id, type, title FROM achievements LIMIT 5", "Recent Achievements"),
    ]
    
    for query, description in queries:
        run_query(query, description)
    
    print("\n✅ Database queries completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom query from command line
        custom_query = " ".join(sys.argv[1:])
        run_query(custom_query, "Custom Query")
    else:
        main()

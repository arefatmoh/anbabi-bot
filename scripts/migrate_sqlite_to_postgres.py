
import sqlite3
import psycopg2
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SQLITE_DB_PATH = "reading_tracker.db"
PG_HOST = os.getenv("DB_HOST", "localhost")
PG_PORT = os.getenv("DB_PORT", "5432")
PG_NAME = os.getenv("DB_NAME", "anbabi_bot")
PG_USER = os.getenv("DB_USER", "postgres")
PG_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_sqlite_conn():
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite database not found at {SQLITE_DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_conn():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_NAME,
            user=PG_USER,
            password=PG_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

def migrate_table(sqlite_cursor, pg_cursor, table_name, pk_column, bool_columns=None):
    if bool_columns is None:
        bool_columns = []
        
    print(f"🔄 Migrating table: {table_name}...")
    
    # Get SQLite data
    try:
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
    except sqlite3.OperationalError:
        print(f"⚠️ Table {table_name} not found in SQLite. Skipping.")
        return

    if not rows:
        print(f"   ℹ️ No rows to migrate for {table_name}.")
        return

    success_count = 0
    skipped_count = 0
    
    # Get column names from first row
    columns = list(rows[0].keys())
    cols_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    
    # Prepare INSERT query
    insert_query = f"""
        INSERT INTO {table_name} ({cols_str})
        VALUES ({placeholders})
        ON CONFLICT ({pk_column}) DO NOTHING
    """
    
    # Special handling for composite PK in league_members if needed, but usually it has a rowid? 
    # Actually league_members PK is (league_id, user_id).
    if table_name == 'league_members':
         insert_query = f"""
            INSERT INTO {table_name} ({cols_str})
            VALUES ({placeholders})
            ON CONFLICT (league_id, user_id) DO NOTHING
        """

    for row in rows:
        data = list(row)
        # Convert boolean columns
        for idx, col in enumerate(columns):
            if col in bool_columns:
                # SQLite has 0/1, Postgres needs True/False (though psycopg2 handles 0/1 fine usually, explicit is better)
                val = data[idx]
                data[idx] = bool(val) if val is not None else None
        
        try:
            pg_cursor.execute(insert_query, tuple(data))
            if pg_cursor.rowcount > 0:
                success_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"   ❌ Failed to insert row in {table_name}: {e}")

    print(f"   ✅ Migrated {success_count} rows (Skipped {skipped_count} duplicates).")

def main():
    print("🚀 Starting Data Migration from SQLite to PostgreSQL...")
    
    sqlite_conn = get_sqlite_conn()
    sqlite_cur = sqlite_conn.cursor()
    
    pg_conn = get_postgres_conn()
    pg_cur = pg_conn.cursor()
    
    try:
        # 0. Clean slate - Truncate tables to remove seeded data that conflicts with migration
        print("🧹 Cleaning existing data (TRUNCATE)...")
        tables_to_truncate = ['users', 'books', 'achievement_definitions', 'leagues', 'motivation_messages', 'reminders', 'reading_sessions', 'user_books', 'user_stats', 'achievements', 'visual_elements', 'league_members']
        for table in tables_to_truncate:
             pg_cur.execute(f"TRUNCATE TABLE {table} CASCADE")
        print("   ✅ Tables truncated.")

        # 1. Users
        migrate_table(sqlite_cur, pg_cur, "users", "user_id", 
                      bool_columns=["is_active", "is_admin", "is_banned", "show_achievements", "show_reading_stats"])
        
        # 2. Books
        migrate_table(sqlite_cur, pg_cur, "books", "book_id", 
                      bool_columns=["is_featured"])
        
        # 3. Achievement Definitions
        migrate_table(sqlite_cur, pg_cur, "achievement_definitions", "id", 
                      bool_columns=["is_active"])
        
        # 4. Leagues
        migrate_table(sqlite_cur, pg_cur, "leagues", "league_id")
        
        # 5. League Members
        migrate_table(sqlite_cur, pg_cur, "league_members", "league_id", # composite pk handled in function
                      bool_columns=["is_active"])
        
        # 6. User Books
        migrate_table(sqlite_cur, pg_cur, "user_books", "id")
        
        # 7. Reading Sessions
        migrate_table(sqlite_cur, pg_cur, "reading_sessions", "id")
        
        # 8. Achievements
        migrate_table(sqlite_cur, pg_cur, "achievements", "id", 
                      bool_columns=["is_notified"])
        
        # 9. User Stats
        migrate_table(sqlite_cur, pg_cur, "user_stats", "user_id")
        
        # 10. Motivation Messages
        migrate_table(sqlite_cur, pg_cur, "motivation_messages", "id", 
                      bool_columns=["is_read"])
        
        # 11. Visual Elements
        migrate_table(sqlite_cur, pg_cur, "visual_elements", "id", 
                      bool_columns=["is_active"])
        
        # 12. Reminders
        migrate_table(sqlite_cur, pg_cur, "reminders", "id", 
                      bool_columns=["is_active"])

        # Reset sequences (Important for SERIAL columns after manual inserts)
        print("🔄 Resetting sequences...")
        tables_with_id = ['books', 'leagues', 'user_books', 'reading_sessions', 
                          'achievements', 'motivation_messages', 'visual_elements', 
                          'achievement_definitions', 'reminders']
        for table in tables_with_id:
            try:
                pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table}")
            except Exception as e:
                # Might fail if table is empty or doesn't have 'id' sequence the standard way
                # books PK is book_id, leagues is league_id.
                pass
        
        # Handle specific PK names
        try:
            pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('books', 'book_id'), COALESCE(MAX(book_id), 1)) FROM books")
        except: pass
        try:
            pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('leagues', 'league_id'), COALESCE(MAX(league_id), 1)) FROM leagues")
        except: pass


        pg_conn.commit()
        print("✅ Data migration completed successfully!")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main()

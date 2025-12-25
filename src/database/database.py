"""
Database connection and setup with PostgreSQL support.

This module handles database initialization and connection management for both SQLite and PostgreSQL.
"""

import sqlite3
import logging
import os
from pathlib import Path
from typing import Optional, Any
from contextlib import contextmanager
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

from src.config.settings import (
    DB_TYPE, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, SQLITE_DB_PATH
)


class SQLiteConnectionWrapper:
    """Wrapper for SQLite connection to return wrapped cursors."""
    
    def __init__(self, connection):
        self._conn = connection
        
    def __getattr__(self, name):
        return getattr(self._conn, name)
        
    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())
    
    def close(self):
        self._conn.close()
        
    def commit(self):
        self._conn.commit()
    
    def rollback(self):
        self._conn.rollback()


class SQLiteCursorWrapper:
    """Wrapper for SQLite cursor to translate PostgreSQL style queries."""
    
    def __init__(self, cursor):
        self._cursor = cursor
    
    def __getattr__(self, name):
        return getattr(self._cursor, name)
        
    def execute(self, sql, parameters=None):
        # Translate %s to ?
        if isinstance(sql, str):
            sql = sql.replace('%s', '?')
            
        if parameters is None:
            return self._cursor.execute(sql)
        else:
            return self._cursor.execute(sql, parameters)
            
    def executemany(self, sql, parameters):
        if isinstance(sql, str):
            sql = sql.replace('%s', '?')
        return self._cursor.executemany(sql, parameters)


class DatabaseManager:
    """Manages database connections and initialization for both SQLite and Postgres."""
    
    def __init__(self):
        """Initialize database manager."""
        self.logger = logging.getLogger(__name__)
        self.db_type = DB_TYPE
        
        if self.db_type == 'sqlite':
            # Ensure database directory exists
            Path(SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Using SQLite database at {SQLITE_DB_PATH}")
        elif self.db_type == 'postgres':
            if not HAS_POSTGRES:
                self.logger.error("psycopg2 not installed. Falling back to SQLite.")
                self.db_type = 'sqlite'
            else:
                self.logger.info(f"Using PostgreSQL database at {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = None
        try:
            if self.db_type == 'postgres':
                # PostgreSQL Connection
                conn = psycopg2.connect(
                    host=DB_HOST,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    port=DB_PORT,
                    cursor_factory=RealDictCursor
                )
                yield conn
            else:
                # SQLite Connection
                real_conn = sqlite3.connect(SQLITE_DB_PATH)
                real_conn.row_factory = sqlite3.Row
                
                # Wrap connection properly
                conn = SQLiteConnectionWrapper(real_conn)
                
                yield conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_database(self):
        """Initialize database tables."""
        try:
            # For Postgres, we check connection first
            if self.db_type == 'postgres':
                try:
                    with self.get_connection() as conn:
                        pass
                except Exception as e:
                    self.logger.error(f"Could not connect to PostgreSQL. Please check credentials. Error: {e}")
                    return

            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create tables
                self._create_tables(cursor)
                
                # Insert default data
                self._insert_default_data(cursor)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def _create_tables(self, cursor: Any):
        """Create all database tables with dialect-specific SQL."""
        
        # Dialect specific types
        if self.db_type == 'postgres':
            AUTO_INC_PK = "SERIAL PRIMARY KEY"
            TIMESTAMP_DEFAULT = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            BOOLEAN_TRUE = "TRUE"
            BOOLEAN_FALSE = "FALSE"
        else:
            AUTO_INC_PK = "INTEGER PRIMARY KEY AUTOINCREMENT"
            TIMESTAMP_DEFAULT = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            BOOLEAN_TRUE = "1"
            BOOLEAN_FALSE = "0"

        # Users table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY, -- Telegram ID is big
                full_name TEXT NOT NULL,
                nickname TEXT,
                city TEXT,
                contact TEXT,
                reading_mode TEXT DEFAULT 'individual',
                daily_goal INTEGER DEFAULT 20,
                reminder_time TEXT,
                reminder_frequency TEXT DEFAULT 'daily',
                registration_date {TIMESTAMP_DEFAULT},
                last_activity {TIMESTAMP_DEFAULT},
                is_active BOOLEAN DEFAULT {BOOLEAN_TRUE},
                is_admin BOOLEAN DEFAULT {BOOLEAN_FALSE},
                is_banned BOOLEAN DEFAULT {BOOLEAN_FALSE},
                bio TEXT,
                reading_goal_pages_per_day INTEGER DEFAULT 20,
                preferred_reading_time TEXT,
                favorite_genres TEXT,
                reading_level TEXT,
                privacy_level TEXT DEFAULT 'public',
                show_achievements BOOLEAN DEFAULT {BOOLEAN_TRUE},
                show_reading_stats BOOLEAN DEFAULT {BOOLEAN_TRUE}
            )
        ''')
        
        # Books table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS books (
                book_id {AUTO_INC_PK},
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                category TEXT,
                description TEXT,
                cover_image TEXT,
                is_featured BOOLEAN DEFAULT {BOOLEAN_FALSE},
                created_by BIGINT,
                created_at {TIMESTAMP_DEFAULT},
                FOREIGN KEY (created_by) REFERENCES users (user_id)
            )
        ''')
        
        # Leagues table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS leagues (
                league_id {AUTO_INC_PK},
                name TEXT NOT NULL,
                description TEXT,
                admin_id BIGINT NOT NULL,
                created_by BIGINT,
                current_book_id INTEGER,
                start_date DATE,
                end_date DATE,
                daily_goal INTEGER DEFAULT 20,
                max_members INTEGER DEFAULT 50,
                status TEXT DEFAULT 'active',
                created_at {TIMESTAMP_DEFAULT},
                FOREIGN KEY (admin_id) REFERENCES users (user_id),
                FOREIGN KEY (created_by) REFERENCES users (user_id),
                FOREIGN KEY (current_book_id) REFERENCES books (book_id)
            )
        ''')

        # League members table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS league_members (
                league_id INTEGER,
                user_id BIGINT,
                joined_at {TIMESTAMP_DEFAULT},
                is_active BOOLEAN DEFAULT {BOOLEAN_TRUE},
                PRIMARY KEY (league_id, user_id),
                FOREIGN KEY (league_id) REFERENCES leagues (league_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User books table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS user_books (
                id {AUTO_INC_PK},
                user_id BIGINT,
                book_id INTEGER,
                league_id INTEGER,
                start_date {TIMESTAMP_DEFAULT},
                last_updated {TIMESTAMP_DEFAULT},
                pages_read INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                target_completion_date DATE,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (league_id) REFERENCES leagues (league_id)
            )
        ''')
        
        # Reading sessions table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS reading_sessions (
                id {AUTO_INC_PK},
                user_id BIGINT,
                book_id INTEGER,
                league_id INTEGER,
                session_date DATE NOT NULL,
                pages_read INTEGER NOT NULL,
                reading_time_minutes INTEGER,
                notes TEXT,
                timestamp {TIMESTAMP_DEFAULT},
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (league_id) REFERENCES leagues (league_id)
            )
        ''')
        
        # Achievements table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS achievements (
                id {AUTO_INC_PK},
                user_id BIGINT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                earned_at {TIMESTAMP_DEFAULT},
                metadata TEXT,
                is_notified BOOLEAN DEFAULT {BOOLEAN_FALSE},
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User statistics table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id BIGINT PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_achievements INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                books_completed INTEGER DEFAULT 0,
                total_pages_read INTEGER DEFAULT 0,
                last_reading_date DATE,
                streak_start_date DATE,
                created_at {TIMESTAMP_DEFAULT},
                updated_at {TIMESTAMP_DEFAULT},
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Motivation messages table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS motivation_messages (
                id {AUTO_INC_PK},
                user_id BIGINT,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                sent_at {TIMESTAMP_DEFAULT},
                is_read BOOLEAN DEFAULT {BOOLEAN_FALSE},
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Visual elements table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS visual_elements (
                id {AUTO_INC_PK},
                user_id BIGINT,
                element_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at {TIMESTAMP_DEFAULT},
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT {BOOLEAN_TRUE},
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Achievement definitions table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS achievement_definitions (
                id {AUTO_INC_PK},
                type TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT,
                xp_reward INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT {BOOLEAN_TRUE},
                created_at {TIMESTAMP_DEFAULT}
            )
        ''')
        
        # Reminders table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS reminders (
                id {AUTO_INC_PK},
                user_id BIGINT,
                reminder_time TIME NOT NULL,
                frequency TEXT DEFAULT 'daily',
                is_active BOOLEAN DEFAULT {BOOLEAN_TRUE},
                last_sent TIMESTAMP,
                created_at {TIMESTAMP_DEFAULT},
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Indexes (Syntax is mostly compatible)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_books_user ON user_books(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reading_sessions_user_date ON reading_sessions(user_id, session_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_league_members_league ON league_members(league_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_stats_user ON user_stats(user_id)')


    def _insert_default_data(self, cursor: Any):
        """Insert default data into the database."""
        from src.config.constants import DEFAULT_FEATURED_BOOKS
        
        # Postgres ON CONFLICT syntax differs from SQLite INSERT OR IGNORE
        if self.db_type == 'postgres':
            insert_book_sql = '''
                INSERT INTO books (title, author, total_pages, category, description, is_featured)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                ON CONFLICT DO NOTHING
            '''
            insert_ach_sql = '''
                INSERT INTO achievement_definitions (type, title, description, icon, xp_reward)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (type) DO NOTHING
            '''
            placeholders = ("%s", "%s", "%s", "%s", "%s") # Not used directly but conceptual
        else:
            insert_book_sql = '''
                INSERT OR IGNORE INTO books (title, author, total_pages, category, description, is_featured)
                VALUES (?, ?, ?, ?, ?, 1)
            '''
            insert_ach_sql = '''
                INSERT OR IGNORE INTO achievement_definitions (type, title, description, icon, xp_reward)
                VALUES (?, ?, ?, ?, ?)
            '''
            
        # Insert default featured books
        for book in DEFAULT_FEATURED_BOOKS:
            cursor.execute(insert_book_sql, (
                book['title'], book['author'], book['total_pages'], book['category'], book['description']
            ))
        
        # Insert default achievement definitions
        default_achievements = [
            # Bronze Level (1-30 days)
            ('1_day_streak', '🥉 First Step', 'Started your reading journey', '🥉', 10),
            ('3_day_streak', '🥉 First Spark', 'You\'ve built your first streak 🔥 Keep going!', '🥉', 25),
            ('7_day_streak', '🥉 One Week Reader', '1 full week of reading! Consistency pays off 🌱', '🥉', 50),
            ('14_day_streak', '🥉 Two-Week Challenger', 'Two weeks strong! Building momentum', '🥉', 100),
            ('21_day_streak', '🥉 Habit Builder', '21 days = new habit formed 💪', '🥉', 150),
            ('30_day_streak', '🥉 One Month Champion', 'One month of consistent reading!', '🥉', 200),
            # Silver Level (31-100 days)
            ('50_day_streak', '🥈 Golden Streak', '50 days of dedication! Shining bright', '🥈', 400),
            ('75_day_streak', '🥈 Dedicated Reader', '75 days! Your dedication is inspiring', '🥈', 600),
            ('100_day_streak', '🥈 Century Club', '100 days! Welcome to the Century Club 🎉', '🥈', 1000),
            # Gold Level (101-250 days)
            ('150_day_streak', '🥇 Unstoppable', '150 days! You are truly unstoppable', '🥇', 1500),
            ('200_day_streak', '🥇 Marathon Mind', '200 days! Your mind is a reading marathon', '🥇', 2000),
            ('250_day_streak', '🥇 Knowledge Seeker', '250 days! A true seeker of knowledge', '🥇', 2500),
            # Diamond Level (251+ days)
            ('300_day_streak', '💎 Book Sage', '300 days! You are a true book sage', '💎', 3000),
            ('365_day_streak', '💎 One-Year Legend', '365 days! You are a reading legend 👑', '💎', 5000),
            # Book completion achievements
            ('first_book', '📖 First Book', 'Complete your first book', '📖', 100),
            ('5_books', '📚 Book Collector', 'Complete 5 books', '📚', 300),
            ('10_books', '📚 Book Lover', 'Complete 10 books', '📚', 600),
            ('25_books', '📚 Book Enthusiast', 'Complete 25 books', '📚', 1500),
            ('50_books', '📚 Book Master', 'Complete 50 books', '📚', 3000),
            # Page reading achievements
            ('100_pages', '📄 Page Turner', 'Read 100 pages', '📄', 50),
            ('500_pages', '📄 Page Reader', 'Read 500 pages', '📄', 200),
            ('1000_pages', '📄 Page Devourer', 'Read 1000 pages', '📄', 500),
            ('5000_pages', '📄 Page Master', 'Read 5000 pages', '📄', 2000),
            # Reading style achievements
            ('speed_reader', '⚡ Speed Reader', 'Read 50+ pages in a single day', '⚡', 100),
            ('consistent_reader', '📅 Consistent Reader', 'Read every day for a week', '📅', 150),
            ('marathon_reader', '🏃 Marathon Reader', 'Read 100+ pages in a single day', '🏃', 200),
            # Community achievements
            ('community_contributor', '🌟 Community Star', 'Participate in a reading league', '🌟', 100),
            ('league_champion', '🏆 League Champion', 'Win a reading league', '🏆', 500),
            # League-specific achievements
            ('league_100_pages', '🏆 League 100 Pages', 'Read 100 pages in a league', '🏆', 20),
            ('league_500_pages', '🏆 League 500 Pages', 'Read 500 pages in a league', '🏆', 100),
            ('league_1000_pages', '🏆 League 1000 Pages', 'Read 1000 pages in a league', '🏆', 200),
            ('league_2000_pages', '🏆 League 2000 Pages', 'Read 2000 pages in a league', '🏆', 400),
            ('league_first_book', '📚 League First Book', 'Complete your first book in a league', '📚', 150),
            ('league_weekly_leader', '👑 Weekly Leader', 'Top reader for a week in a league', '👑', 300),
            ('league_monthly_champion', '🏆 Monthly Champion', 'Top reader for a month in a league', '🏆', 600),
        ]
        
        for achievement_type, title, description, icon, xp_reward in default_achievements:
            cursor.execute(insert_ach_sql, (achievement_type, title, description, icon, xp_reward))
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        if self.db_type == 'postgres':
            self.logger.warning("PostgreSQL backup not implemented via file copy.")
            return False
            
        try:
            import shutil
            shutil.copy2(SQLITE_DB_PATH, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """Get database information and statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table counts
                tables = ['users', 'books', 'leagues', 'user_books', 'reading_sessions', 'achievements',
                          'user_stats', 'motivation_messages', 'visual_elements', 'achievement_definitions']
                table_counts = {}
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    # Handle both dictionary and tuple results
                    row = cursor.fetchone()
                    if hasattr(row, 'keys'): # RealDictCursor
                        table_counts[table] = row['count']
                    else:
                        table_counts[table] = row[0]
                
                return {
                    'database_type': self.db_type,
                    'table_counts': table_counts
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()

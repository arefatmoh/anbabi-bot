"""
Database connection and setup.

This module handles database initialization and connection management.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

from src.config.settings import DATABASE_PATH


class DatabaseManager:
    """Manages database connections and initialization."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager."""
        self.db_path = db_path or DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            return conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def init_database(self):
        """Initialize database tables."""
        try:
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
    
    def _create_tables(self, cursor: sqlite3.Cursor):
        """Create all database tables."""
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT NOT NULL,
                city TEXT NOT NULL,
                contact TEXT,
                reading_mode TEXT DEFAULT 'individual',
                daily_goal INTEGER DEFAULT 20,
                reminder_time TEXT,
                reminder_frequency TEXT DEFAULT 'daily',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0
            )
        ''')
        
        # Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                category TEXT,
                description TEXT,
                cover_image TEXT,
                is_featured BOOLEAN DEFAULT 0,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (user_id)
            )
        ''')
        
        # Leagues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leagues (
                league_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                admin_id INTEGER NOT NULL,
                current_book_id INTEGER,
                start_date DATE,
                end_date DATE,
                daily_goal INTEGER DEFAULT 20,
                max_members INTEGER DEFAULT 50,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (user_id),
                FOREIGN KEY (current_book_id) REFERENCES books (book_id)
            )
        ''')
        
        # League members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS league_members (
                league_id INTEGER,
                user_id INTEGER,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                PRIMARY KEY (league_id, user_id),
                FOREIGN KEY (league_id) REFERENCES leagues (league_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                league_id INTEGER,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pages_read INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                target_completion_date DATE,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (league_id) REFERENCES leagues (league_id)
            )
        ''')
        
        # Reading sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                league_id INTEGER,
                session_date DATE NOT NULL,
                pages_read INTEGER NOT NULL,
                reading_time_minutes INTEGER,
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (league_id) REFERENCES leagues (league_id)
            )
        ''')
        
        # Achievements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reminder_time TIME NOT NULL,
                frequency TEXT DEFAULT 'daily',
                is_active BOOLEAN DEFAULT 1,
                last_sent TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_books_user ON user_books(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reading_sessions_user_date ON reading_sessions(user_id, session_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_league_members_league ON league_members(league_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(user_id)')
    
    def _insert_default_data(self, cursor: sqlite3.Cursor):
        """Insert default data into the database."""
        from src.config.constants import DEFAULT_FEATURED_BOOKS
        
        # Insert default featured books
        for book in DEFAULT_FEATURED_BOOKS:
            cursor.execute('''
                INSERT OR IGNORE INTO books (title, author, total_pages, category, description, is_featured)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (book['title'], book['author'], book['total_pages'], book['category'], book['description']))
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
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
                tables = ['users', 'books', 'leagues', 'user_books', 'reading_sessions', 'achievements']
                table_counts = {}
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size_mb = (page_count * page_size) / (1024 * 1024)
                
                return {
                    'database_size_mb': round(db_size_mb, 2),
                    'table_counts': table_counts,
                    'database_path': str(self.db_path)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()

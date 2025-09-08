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
                full_name TEXT NOT NULL,
                nickname TEXT,
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
                is_banned BOOLEAN DEFAULT 0,
                -- Extended profile fields
                bio TEXT,
                reading_goal_pages_per_day INTEGER DEFAULT 20,
                preferred_reading_time TEXT,
                favorite_genres TEXT,
                reading_level TEXT,
                privacy_level TEXT DEFAULT 'public',
                show_achievements BOOLEAN DEFAULT 1,
                show_reading_stats BOOLEAN DEFAULT 1
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
                created_by INTEGER,
                current_book_id INTEGER,
                start_date DATE,
                end_date DATE,
                daily_goal INTEGER DEFAULT 20,
                max_members INTEGER DEFAULT 50,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (user_id),
                FOREIGN KEY (created_by) REFERENCES users (user_id),
                FOREIGN KEY (current_book_id) REFERENCES books (book_id)
            )
        ''')

        # Backfill missing columns for existing databases
        try:
            cursor.execute("PRAGMA table_info(leagues)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            if 'created_by' not in existing_cols:
                cursor.execute('ALTER TABLE leagues ADD COLUMN created_by INTEGER')
        except Exception:
            pass
        
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
                is_notified BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User statistics table for gamification
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                total_achievements INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                books_completed INTEGER DEFAULT 0,
                total_pages_read INTEGER DEFAULT 0,
                last_reading_date DATE,
                streak_start_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Motivation messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motivation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Visual elements table for progress bars, badges, certificates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visual_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                element_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Achievement definitions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievement_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT,
                xp_reward INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                display_name TEXT,
                nickname TEXT,
                bio TEXT,
                reading_goal_pages_per_day INTEGER DEFAULT 20,
                preferred_reading_time TEXT,
                favorite_genres TEXT,
                reading_level TEXT,
                privacy_level TEXT DEFAULT 'public',
                show_achievements BOOLEAN DEFAULT 1,
                show_reading_stats BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_type ON achievements(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_stats_user ON user_stats(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_motivation_messages_user ON motivation_messages(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visual_elements_user ON visual_elements(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievement_definitions_type ON achievement_definitions(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_profiles_user ON user_profiles(user_id)')
        
        # Migrate data from user_profiles to users table if needed
        self._migrate_user_profiles_to_users(cursor)
    
    def _migrate_user_profiles_to_users(self, cursor: sqlite3.Cursor):
        """Migrate data from user_profiles table to users table."""
        try:
            # Check if user_profiles table exists and has data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles'")
            if not cursor.fetchone():
                return  # No user_profiles table to migrate from
            
            # Check if users table already has the new columns
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'bio' not in columns:
                # Add the new columns to users table (simplified - no display_name/username)
                cursor.execute('ALTER TABLE users ADD COLUMN bio TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN reading_goal_pages_per_day INTEGER DEFAULT 20')
                cursor.execute('ALTER TABLE users ADD COLUMN preferred_reading_time TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN favorite_genres TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN reading_level TEXT')
                cursor.execute('ALTER TABLE users ADD COLUMN privacy_level TEXT DEFAULT "public"')
                cursor.execute('ALTER TABLE users ADD COLUMN show_achievements BOOLEAN DEFAULT 1')
                cursor.execute('ALTER TABLE users ADD COLUMN show_reading_stats BOOLEAN DEFAULT 1')
            
            # Migrate data from user_profiles to users (simplified fields)
            cursor.execute('''
                UPDATE users SET
                    nickname = COALESCE((SELECT nickname FROM user_profiles WHERE user_profiles.user_id = users.user_id), users.nickname),
                    bio = (SELECT bio FROM user_profiles WHERE user_profiles.user_id = users.user_id),
                    reading_goal_pages_per_day = COALESCE((SELECT reading_goal_pages_per_day FROM user_profiles WHERE user_profiles.user_id = users.user_id), users.daily_goal),
                    preferred_reading_time = (SELECT preferred_reading_time FROM user_profiles WHERE user_profiles.user_id = users.user_id),
                    favorite_genres = (SELECT favorite_genres FROM user_profiles WHERE user_profiles.user_id = users.user_id),
                    reading_level = (SELECT reading_level FROM user_profiles WHERE user_profiles.user_id = users.user_id),
                    privacy_level = COALESCE((SELECT privacy_level FROM user_profiles WHERE user_profiles.user_id = users.user_id), 'public'),
                    show_achievements = COALESCE((SELECT show_achievements FROM user_profiles WHERE user_profiles.user_id = users.user_id), 1),
                    show_reading_stats = COALESCE((SELECT show_reading_stats FROM user_profiles WHERE user_profiles.user_id = users.user_id), 1)
                WHERE EXISTS (SELECT 1 FROM user_profiles WHERE user_profiles.user_id = users.user_id)
            ''')
            
            self.logger.info("Successfully migrated user_profiles data to users table")
            
        except Exception as e:
            self.logger.error(f"Failed to migrate user_profiles data: {e}")
    
    def _insert_default_data(self, cursor: sqlite3.Cursor):
        """Insert default data into the database."""
        from src.config.constants import DEFAULT_FEATURED_BOOKS
        
        # Insert default featured books
        for book in DEFAULT_FEATURED_BOOKS:
            cursor.execute('''
                INSERT OR IGNORE INTO books (title, author, total_pages, category, description, is_featured)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (book['title'], book['author'], book['total_pages'], book['category'], book['description']))
        
        # Insert default achievement definitions
        default_achievements = [
            # Enhanced Streak achievements with Bronze/Silver/Gold/Diamond levels
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
            cursor.execute('''
                INSERT OR IGNORE INTO achievement_definitions (type, title, description, icon, xp_reward)
                VALUES (?, ?, ?, ?, ?)
            ''', (achievement_type, title, description, icon, xp_reward))
    
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
                tables = ['users', 'books', 'leagues', 'user_books', 'reading_sessions', 'achievements',
                          'user_stats', 'motivation_messages', 'visual_elements', 'achievement_definitions', 'user_profiles']
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

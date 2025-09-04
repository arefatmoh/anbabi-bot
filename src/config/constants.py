"""
Application constants and enums.

This module contains all the constant values used throughout the application.
"""

from enum import Enum

# Bot States
class BotStates(Enum):
    """Conversation states for the bot."""
    REGISTERING = "registering"
    MODE_SELECTION = "mode_selection"
    BOOK_SELECTION = "book_selection"
    CUSTOM_BOOK_INPUT = "custom_book_input"
    PROGRESS_UPDATE = "progress_update"
    LEAGUE_JOIN = "league_join"
    REMINDER_SETUP = "reminder_setup"

# User Modes
class UserModes(Enum):
    """User reading modes."""
    INDIVIDUAL = "individual"
    COMMUNITY = "community"

# Reading Status
class ReadingStatus(Enum):
    """Book reading status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"

# Achievement Types
class AchievementTypes(Enum):
    """Types of achievements."""
    FIRST_BOOK = "first_book"
    BOOK_COMPLETED = "book_completed"
    STREAK_3 = "streak_3"
    STREAK_7 = "streak_7"
    STREAK_14 = "streak_14"
    STREAK_30 = "streak_30"
    STREAK_100 = "streak_100"
    FAST_READER = "fast_reader"
    CONSISTENCY_STAR = "consistency_star"
    HALFWAY = "halfway"
    QUARTER = "quarter"
    THREE_QUARTERS = "three_quarters"

# League Status
class LeagueStatus(Enum):
    """League status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FULL = "full"

# Export Formats
class ExportFormats(Enum):
    """Data export formats."""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"

# Reminder Frequencies
class ReminderFrequency(Enum):
    """Reminder frequency options."""
    DAILY = "daily"
    WEEKDAYS = "weekdays"
    WEEKENDS = "weekends"
    CUSTOM = "custom"

# Progress Thresholds
PROGRESS_THRESHOLDS = {
    25: "quarter",
    50: "halfway",
    75: "three_quarters",
    100: "completed"
}

# Streak Thresholds
STREAK_THRESHOLDS = [3, 7, 14, 30, 100]

# Reading Goals
DEFAULT_DAILY_GOALS = [10, 15, 20, 25, 30, 50]

# Book Categories
BOOK_CATEGORIES = [
    "Fiction",
    "Non-Fiction",
    "Self-Help",
    "Biography",
    "History",
    "Science",
    "Philosophy",
    "Religion",
    "Business",
    "Technology",
    "Health",
    "Education"
]

# Featured Books (Default)
DEFAULT_FEATURED_BOOKS = [
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "total_pages": 208,
        "category": "Fiction",
        "description": "A magical story about following your dreams"
    },
    {
        "title": "The Prophet",
        "author": "Kahlil Gibran",
        "total_pages": 96,
        "category": "Philosophy",
        "description": "Poetic wisdom about life and love"
    },
    {
        "title": "The Forty Rules of Love",
        "author": "Elif Shafak",
        "total_pages": 354,
        "category": "Fiction",
        "description": "A novel about love and spiritual awakening"
    },
    {
        "title": "The Road Less Traveled",
        "author": "M. Scott Peck",
        "total_pages": 320,
        "category": "Self-Help",
        "description": "A guide to spiritual growth"
    },
    {
        "title": "The Power of Now",
        "author": "Eckhart Tolle",
        "total_pages": 229,
        "category": "Self-Help",
        "description": "A guide to spiritual enlightenment"
    }
]

# Emoji Constants
EMOJIS = {
    "book": "📚",
    "reading": "📖",
    "progress": "📊",
    "achievement": "🏆",
    "streak": "🔥",
    "star": "⭐",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "clock": "⏰",
    "calendar": "📅",
    "trophy": "🏆",
    "medal": "🥇",
    "fire": "🔥",
    "rocket": "🚀",
    "heart": "❤️",
    "thumbs_up": "👍",
    "clap": "👏",
    "party": "🎉"
}

# Message Templates
MESSAGE_TEMPLATES = {
    "welcome": "🌟 Welcome to {bot_name}!",
    "progress_bar": "▓" * 10,  # 10 blocks for progress bar
    "empty_progress": "░" * 10,  # 10 empty blocks
    "separator": "─" * 40,
    "bullet_point": "•",
    "arrow": "→",
    "double_arrow": "⇒"
}

# Database Constants
DB_CONSTRAINTS = {
    "max_username_length": 32,
    "max_name_length": 100,
    "max_city_length": 50,
    "max_contact_length": 100,
    "max_book_title_length": 200,
    "max_author_length": 100,
    "max_league_name_length": 100,
    "max_achievement_description": 500
}

# Time Constants
TIME_CONSTANTS = {
    "seconds_per_minute": 60,
    "minutes_per_hour": 60,
    "hours_per_day": 24,
    "days_per_week": 7,
    "days_per_month": 30,
    "days_per_year": 365
}

# Reading Speed Constants (pages per hour)
READING_SPEED_ESTIMATES = {
    "slow": 10,      # 10 pages per hour
    "average": 20,   # 20 pages per hour
    "fast": 40,      # 40 pages per hour
    "very_fast": 60  # 60 pages per hour
}

# Notification Constants
NOTIFICATION_CONSTANTS = {
    "max_retries": 3,
    "retry_delay": 300,  # 5 minutes
    "batch_size": 50,    # Send notifications in batches
    "timeout": 30        # 30 seconds timeout
}

# Cache Constants
CACHE_CONSTANTS = {
    "user_data_ttl": 3600,      # 1 hour
    "book_data_ttl": 7200,      # 2 hours
    "league_data_ttl": 1800,    # 30 minutes
    "stats_ttl": 86400,         # 24 hours
    "max_cache_size": 1000      # Maximum items in cache
}

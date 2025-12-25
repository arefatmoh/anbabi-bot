"""
Application settings and configuration.

This module contains all the configuration settings for the bot.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Admin Configuration
ADMIN_USER_IDS = [
    int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') 
    if id.strip()
]

# Database Configuration
# Database Configuration
# DATABASE_PATH = os.getenv('DATABASE_PATH', BASE_DIR / 'reading_tracker.db')
DB_TYPE = os.getenv('DB_TYPE', 'postgres')  # 'sqlite' or 'postgres'

# Postgres Settings
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# SQLite Fallback (for local testing without PG)
SQLITE_DB_PATH = os.getenv('DATABASE_PATH', BASE_DIR / 'reading_tracker.db')

# Google Sheets Configuration (optional)
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Bot Settings
BOT_NAME = "Read & Revive (አንባቢ)"
BOT_USERNAME = os.getenv('BOT_USERNAME', 'anbabi_bot')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Reading Settings
DEFAULT_DAILY_GOAL = 20  # Default pages per day
MAX_BOOKS_PER_USER = 5   # Maximum books a user can read simultaneously
MIN_PAGES_PER_SESSION = 1
MAX_PAGES_PER_SESSION = 100

# Community Settings
MAX_LEAGUE_MEMBERS = 50
DEFAULT_LEAGUE_DURATION_DAYS = 30

# Reminder Settings
DEFAULT_REMINDER_TIME = "20:00"  # 8:00 PM 20:00
REMINDER_TIMEZONE = "Africa/Addis_Ababa"

# Achievement Settings
STREAK_THRESHOLDS = [3, 7, 14, 30, 100]  # Days for streak achievements
COMPLETION_THRESHOLDS = [25, 50, 75, 100]  # Percentage for completion achievements

# Export Settings
EXPORT_FORMATS = ['csv', 'excel', 'json']
MAX_EXPORT_RECORDS = 10000

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = BASE_DIR / 'logs' / 'bot.log'

# Create logs directory if it doesn't exist
LOG_FILE.parent.mkdir(exist_ok=True)

#!/usr/bin/env python3
"""
Database setup script for Read & Revive Bot.

This script initializes the database with all required tables and default data.
"""

import sys
from pathlib import Path

# Add project root to Python path so 'src' is importable
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.database import db_manager


def main():
    """Main setup function."""
    print("🚀 Setting up Read & Revive Bot Database...")
    print("=" * 50)

    try:
        # Initialize database
        print("📊 Initializing database...")
        db_manager.init_database()
        print("✅ Database initialized successfully!")

        # Get database info
        print("\n📊 Database Information:")
        info = db_manager.get_database_info()
        for key, value in info.items():
            if key == 'table_counts':
                print("  📋 Tables:")
                for table, count in value.items():
                    print(f"    • {table}: {count} records")
            else:
                print(f"  {key}: {value}")

        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Set up your .env file with BOT_TOKEN")
        print("2. Run 'python main.py' to start the bot")

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

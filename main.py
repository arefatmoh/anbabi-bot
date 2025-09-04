#!/usr/bin/env python3
"""
Read & Revive (አንባቢ) Bot - Main Entry Point

A comprehensive Telegram bot for reading tracking and community engagement.
"""

import logging
import sys
from pathlib import Path
import io

# Add project root to Python path so 'src' is importable
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
SRC_DIR = ROOT_DIR / "src"

from src.core.bot import ReadingTrackerBot
from src.config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logging():
    """Set up logging configuration."""
    # Try to make stdout/stderr UTF-8 to avoid Windows cp1252 issues with emojis
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

    # Create logs directory if it doesn't exist
    LOG_FILE.parent.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    """Main application entry point."""
    try:
        # Set up logging
        setup_logging()
        logger = logging.getLogger(__name__)

        logger.info("🚀 Starting Read & Revive Bot...")
        logger.info(f"📁 Working directory: {ROOT_DIR}")
        logger.info(f"📁 Source path: {SRC_DIR}")

        # Create and start the bot
        bot = ReadingTrackerBot()
        bot.start()

    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the bot
    main()

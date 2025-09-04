"""
Test the new project structure and imports.

This test verifies that all modules can be imported correctly.
"""

import sys
from pathlib import Path
import pytest


def test_project_structure():
    """Test that the project structure is correct."""
    # Add src to Python path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Test that we can import main modules
    try:
        from src.config import settings, messages, constants
        from src.core import bot
        from src.database import database
        print("✅ All main modules imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


def test_config_imports():
    """Test configuration module imports."""
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from src.config.settings import BOT_TOKEN, DATABASE_PATH
        from src.config.messages import WELCOME_MESSAGE
        from src.config.constants import BotStates, UserModes
        print("✅ Configuration modules imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import config modules: {e}")


def test_database_imports():
    """Test database module imports."""
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from src.database.database import DatabaseManager
        print("✅ Database modules imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import database modules: {e}")


if __name__ == "__main__":
    print("🧪 Testing project structure...")
    test_project_structure()
    test_config_imports()
    test_database_imports()
    print("🎉 All structure tests passed!")

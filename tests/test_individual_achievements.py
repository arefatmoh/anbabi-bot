from pathlib import Path
import sys

# Ensure project root is on PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.achievement_service import AchievementService
from src.services.book_service import BookService
from tests.test_utils import reset_user, start_book_for_user, print_user_overview


TEST_USER = 700000001


def run():
    reset_user(TEST_USER)
    book_service = BookService()
    ach_service = AchievementService()

    # Create a custom book and start it
    book_id = book_service.add_custom_book_and_start(TEST_USER, 'Indiv Test Book', 'Author', 180)

    # First reading session: 50 pages (Speed Reader + Day 1 streak)
    book_service.update_progress(TEST_USER, book_id, 50)
    ach_service.update_reading_progress(TEST_USER, 50, book_id)

    # Second session: another 50 to cross 100 pages total
    book_service.update_progress(TEST_USER, book_id, 50)
    ach_service.update_reading_progress(TEST_USER, 50, book_id)

    print_user_overview(TEST_USER)


if __name__ == '__main__':
    run()



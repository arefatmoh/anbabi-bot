from pathlib import Path
import sys

# Ensure project root is on PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.achievement_service import AchievementService
from src.services.book_service import BookService
from tests.test_utils import reset_user, ensure_league, join_league, get_league_current_book, print_user_overview


TEST_USER = 700000002


def run():
    reset_user(TEST_USER)
    book_service = BookService()
    ach_service = AchievementService()

    # Ensure a league with a current book
    league_id = ensure_league('League Alpha')
    join_league(TEST_USER, league_id)
    book_id = get_league_current_book(league_id)

    # Start league book for user
    book_service.start_reading(TEST_USER, book_id)

    # Read 120 pages in league context to trigger contributor + league_100_pages
    # Record sessions and achievements
    book_service.update_progress(TEST_USER, book_id, 60)
    ach_service.update_reading_progress(TEST_USER, 60, book_id)
    ach_service.check_league_achievements(TEST_USER, league_id, 60)

    book_service.update_progress(TEST_USER, book_id, 60)
    ach_service.update_reading_progress(TEST_USER, 60, book_id)
    ach_service.check_league_achievements(TEST_USER, league_id, 60)

    print_user_overview(TEST_USER)


if __name__ == '__main__':
    run()



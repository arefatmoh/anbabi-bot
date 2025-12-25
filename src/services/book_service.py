"""
Book service for featured books, user reading, and progress updates.
"""

from typing import List, Dict, Optional
from datetime import date
from src.database.database import db_manager


class BookService:
    """Provides book listing and user reading operations."""

    def get_user_daily_goal(self, user_id: int) -> int:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT daily_goal FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if not row or row['daily_goal'] is None:
                return 20
            try:
                return int(row['daily_goal'])
            except Exception:
                return 20

    def set_user_daily_goal(self, user_id: int, pages_per_day: int) -> None:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users (user_id, daily_goal, full_name, city, contact)
                VALUES (%s, %s, '', '', '')
                ON CONFLICT(user_id) DO UPDATE SET daily_goal = excluded.daily_goal
                """,
                (user_id, pages_per_day),
            )
            conn.commit()

    def get_featured_books(self) -> List[Dict]:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT book_id, title, author, total_pages
                FROM books WHERE is_featured = TRUE
                ORDER BY book_id
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "book_id": r['book_id'],
                    "title": r['title'],
                    "author": r['author'],
                    "total_pages": r['total_pages'],
                }
                for r in rows
            ]

    def add_custom_book_and_start(self, user_id: int, title: str, author: str, total_pages: int) -> int:
        """Create a user-added book and start reading it. Returns book_id."""
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO books (title, author, total_pages, category, description, cover_image, is_featured, created_by)
                VALUES (%s, %s, %s, '', '', '', FALSE, %s)
                RETURNING book_id
                """,
                (title, author, total_pages, user_id),
            )
            book_id = cur.fetchone()['book_id'] # Postgres RETURNING
            # Start reading for user
            cur.execute(
                """
                INSERT INTO user_books (user_id, book_id, start_date, pages_read, status)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 0, 'active')
                """,
                (user_id, book_id),
            )
            conn.commit()
            return book_id

    def start_reading(self, user_id: int, book_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            # if already active, do nothing
            cur.execute(
                """
                SELECT 1 FROM user_books
                WHERE user_id = %s AND book_id = %s AND status = 'active'
                """,
                (user_id, book_id),
            )
            if cur.fetchone():
                return False
            cur.execute(
                """
                INSERT INTO user_books (user_id, book_id, start_date, pages_read, status)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 0, 'active')
                """,
                (user_id, book_id),
            )
            conn.commit()
            return True

    def get_active_books(self, user_id: int) -> List[Dict]:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ub.book_id, b.title, b.author, b.total_pages, ub.pages_read, ub.start_date
                FROM user_books ub
                JOIN books b ON b.book_id = ub.book_id
                WHERE ub.user_id = %s AND ub.status = 'active'
                ORDER BY ub.start_date DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            result: List[Dict] = []
            for r in rows:
                # With RealDictCursor, access by key
                pages_read = r['pages_read']
                total_pages = r['total_pages']
                progress = round((pages_read / total_pages) * 100, 1) if pages_read else 0.0
                result.append(
                    {
                        "book_id": r['book_id'],
                        "title": r['title'],
                        "author": r['author'],
                        "total_pages": total_pages,
                        "pages_read": pages_read,
                        "start_date": r['start_date'],
                        "progress_percent": progress,
                    }
                )
            return result

    def get_user_books_with_status(self, user_id: int) -> List[Dict]:
        """Return all books for a user with status label and counts."""
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT ub.book_id, b.title, b.author, b.total_pages, ub.pages_read, ub.status
                FROM user_books ub
                JOIN books b ON b.book_id = ub.book_id
                WHERE ub.user_id = %s
                ORDER BY CASE ub.status WHEN 'active' THEN 0 WHEN 'completed' THEN 1 ELSE 2 END, ub.start_date DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            result: List[Dict] = []
            for r in rows:
                label = "Completed" if r['status'] == 'completed' else f"{int(r['pages_read'] or 0)}/{int(r['total_pages'] or 0)}"
                result.append(
                    {
                        "book_id": int(r['book_id']),
                        "title": r['title'],
                        "author": r['author'],
                        "total_pages": int(r['total_pages'] or 0),
                        "pages_read": int(r['pages_read'] or 0),
                        "status": r['status'],
                        "display_status": label,
                    }
                )
            return result

    def delete_user_book(self, user_id: int, book_id: int) -> bool:
        """Delete a user's registered book: remove sessions and user_books; delete book row if custom and unused."""
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            # Ensure ownership exists
            cur.execute(
                "SELECT 1 FROM user_books WHERE user_id = %s AND book_id = %s",
                (user_id, book_id),
            )
            if not cur.fetchone():
                return False
            # Delete reading sessions for this user/book
            cur.execute(
                "DELETE FROM reading_sessions WHERE user_id = %s AND book_id = %s",
                (user_id, book_id),
            )
            # Delete mapping
            cur.execute(
                "DELETE FROM user_books WHERE user_id = %s AND book_id = %s",
                (user_id, book_id),
            )
            # If book is custom by this user and no one else uses it, delete it
            cur.execute(
                "SELECT is_featured, created_by FROM books WHERE book_id = %s",
                (book_id,),
            )
            b = cur.fetchone()
            # Postgres booleans
            is_featured = b['is_featured'] if b else False
            created_by = b['created_by'] if b else None
            
            if b and not is_featured and created_by == user_id:
                cur.execute(
                    "SELECT COUNT(*) as count FROM user_books WHERE book_id = %s",
                    (book_id,),
                )
                cnt = int(cur.fetchone()['count'] or 0)
                if cnt == 0:
                    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            conn.commit()
            return True

    def update_progress(self, user_id: int, book_id: int, pages_read: int) -> Dict:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            # get total pages
            cur.execute("SELECT total_pages FROM books WHERE book_id = %s", (book_id,))
            book = cur.fetchone()
            if not book:
                return {"error": "Book not found"}
            total_pages = int(book['total_pages'])

            # update total pages_read for user_books
            cur.execute(
                """
                UPDATE user_books
                SET pages_read = pages_read + %s, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = %s AND book_id = %s AND status = 'active'
                """,
                (pages_read, user_id, book_id),
            )

            # current pages
            cur.execute(
                """
                SELECT pages_read FROM user_books
                WHERE user_id = %s AND book_id = %s
                """,
                (user_id, book_id),
            )
            row = cur.fetchone()
            if not row:
                return {"error": "Reading session not found"}
            current_pages = int(row['pages_read'])

            # mark completed if needed
            is_completed = current_pages >= total_pages
            if is_completed:
                cur.execute(
                    """
                    UPDATE user_books SET status = 'completed' WHERE user_id = %s AND book_id = %s
                    """,
                    (user_id, book_id),
                )

            # insert reading session
            cur.execute(
                """
                INSERT INTO reading_sessions (user_id, book_id, league_id, session_date, pages_read)
                VALUES (%s, %s, NULL, %s, %s)
                """,
                (user_id, book_id, date.today(), pages_read),
            )
            conn.commit()

            progress_percent = round((current_pages / total_pages) * 100, 1) if total_pages else 0.0
            remaining_pages = max(0, total_pages - current_pages)
            return {
                "current_pages": current_pages,
                "total_pages": total_pages,
                "progress_percent": progress_percent,
                "remaining_pages": remaining_pages,
                "is_completed": is_completed,
                "pages_read_today": pages_read,
            }

    def update_progress_with_context(self, user_id: int, book_id: int, pages_read: int, league_id: Optional[int] = None) -> Dict:
        """Update progress and record session with optional league context."""
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            # get total pages
            cur.execute("SELECT total_pages FROM books WHERE book_id = %s", (book_id,))
            book = cur.fetchone()
            if not book:
                return {"error": "Book not found"}
            total_pages = int(book['total_pages'])

            # update total pages_read for user_books
            cur.execute(
                """
                UPDATE user_books
                SET pages_read = pages_read + %s, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = %s AND book_id = %s AND status = 'active'
                """,
                (pages_read, user_id, book_id),
            )

            # current pages
            cur.execute(
                """
                SELECT pages_read FROM user_books
                WHERE user_id = %s AND book_id = %s
                """,
                (user_id, book_id),
            )
            row = cur.fetchone()
            if not row:
                return {"error": "Reading session not found"}
            current_pages = int(row['pages_read'])

            # mark completed if needed
            is_completed = current_pages >= total_pages
            if is_completed:
                cur.execute(
                    """
                    UPDATE user_books SET status = 'completed' WHERE user_id = %s AND book_id = %s
                    """,
                    (user_id, book_id),
                )

            # insert reading session with league context
            cur.execute(
                """
                INSERT INTO reading_sessions (user_id, book_id, league_id, session_date, pages_read)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, book_id, league_id, date.today(), pages_read),
            )
            conn.commit()

            progress_percent = round((current_pages / total_pages) * 100, 1) if total_pages else 0.0
            remaining_pages = max(0, total_pages - current_pages)
            return {
                "current_pages": current_pages,
                "total_pages": total_pages,
                "progress_percent": progress_percent,
                "remaining_pages": remaining_pages,
                "is_completed": is_completed,
                "pages_read_today": pages_read,
            }

    def get_user_stats(self, user_id: int) -> Dict:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as count FROM user_books WHERE user_id = %s", (user_id,))
            total_books = int(cur.fetchone()['count'] or 0)
            cur.execute(
                "SELECT COUNT(*) as count FROM user_books WHERE user_id = %s AND status = 'completed'",
                (user_id,),
            )
            completed_books = int(cur.fetchone()['count'] or 0)
            cur.execute("SELECT SUM(pages_read) as sum FROM user_books WHERE user_id = %s", (user_id,))
            total_pages = int(cur.fetchone()['sum'] or 0)
            return {
                "total_books": total_books,
                "completed_books": completed_books,
                "total_pages": total_pages,
            }

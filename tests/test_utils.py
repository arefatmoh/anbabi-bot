import sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path(__file__).resolve().parents[1] / 'reading_tracker.db'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def reset_user(user_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        # delete child rows first
        cur.execute('DELETE FROM motivation_messages WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM achievements WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM reading_sessions WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM user_books WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM reminders WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM user_stats WHERE user_id = ?', (user_id,))
        cur.execute('DELETE FROM league_members WHERE user_id = ?', (user_id,))
        # keep the user record if exists (or recreate as active)
        cur.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        cur.execute('''
            INSERT OR IGNORE INTO users (user_id, full_name, city, is_active)
            VALUES (?, 'Tester', 'Addis Ababa', 1)
        ''', (user_id,))
        conn.commit()


def ensure_league(name: str, admin_id: int = 900000001, book_title: str = 'Test Book A') -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO users (user_id, full_name, city, is_admin, is_active) VALUES (?, "Test Admin", "Addis Ababa", 1, 1)', (admin_id,))
        cur.execute('INSERT OR IGNORE INTO books (title, author, total_pages, created_by, is_featured) VALUES (?, "Author", 200, ?, 0)', (book_title, admin_id))
        cur.execute('SELECT book_id FROM books WHERE title = ? ORDER BY book_id DESC LIMIT 1', (book_title,))
        book_id = cur.fetchone()[0]
        cur.execute('SELECT league_id FROM leagues WHERE name = ?', (name,))
        row = cur.fetchone()
        if row:
            return int(row[0])
        cur.execute('''
            INSERT INTO leagues (name, description, admin_id, current_book_id, start_date, end_date, daily_goal, max_members, status)
            VALUES (?, 'Test League', ?, ?, DATE('now'), DATE('now','+30 day'), 20, 50, 'active')
        ''', (name, admin_id, book_id))
        conn.commit()
        return cur.lastrowid


def join_league(user_id: int, league_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO league_members (league_id, user_id) VALUES (?, ?)', (league_id, user_id))
        conn.commit()


def start_book_for_user(user_id: int, book_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO user_books (user_id, book_id, start_date, pages_read, status) VALUES (?, ?, DATE("now"), 0, "active")', (user_id, book_id))
        conn.commit()


def get_league_current_book(league_id: int) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute('SELECT current_book_id FROM leagues WHERE league_id = ?', (league_id,))
        return int(cur.fetchone()[0])


def print_user_overview(user_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        print('--- user_stats ---')
        cur.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        print(dict(cur.fetchone() or {}))
        print('--- achievements (recent 10) ---')
        cur.execute('SELECT type, title, earned_at FROM achievements WHERE user_id = ? ORDER BY earned_at DESC LIMIT 10', (user_id,))
        for row in cur.fetchall():
            print(dict(row))
        print('--- motivation_messages (recent 5) ---')
        cur.execute('SELECT message_type, content, sent_at FROM motivation_messages WHERE user_id = ? ORDER BY sent_at DESC LIMIT 5', (user_id,))
        for row in cur.fetchall():
            print(dict(row))



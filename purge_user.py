#!/usr/bin/env python3
"""
Force-delete a user and all related rows to avoid foreign key constraint errors.

Usage:
  python purge_user.py <user_id> [db_path]

Defaults:
  user_id: 1210555623
  db_path: ./reading_tracker.db
"""

import sys
import sqlite3
import time
from pathlib import Path


def main():
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1210555623
    db_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("reading_tracker.db")

    print(f"Connecting to {db_path.resolve()} ...")
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Ensure FK enforcement is on (and respected during DELETE)
    cur.execute("PRAGMA foreign_keys=ON")
    # Increase wait time for locked DB
    cur.execute("PRAGMA busy_timeout=10000")
    # WAL can help with concurrent readers
    try:
        cur.execute("PRAGMA journal_mode=WAL")
    except Exception:
        pass

    # List tables (exclude internal)
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)

    # Get columns per table
    schema = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info('{t}')")
        schema[t] = [row[1] for row in cur.fetchall()]

    # Known user-ref columns
    user_cols = {"user_id", "created_by", "admin_id", "owner_id"}

    # Preferred delete order for common child tables (delete children first)
    preferred_order = [
        'achievements',
        'user_stats',
        'motivation_messages',
        'visual_elements',
        'reading_progress',
        'reading_sessions',
        'user_books',
        'reminders',
        'league_members',
        'league_invitations',
        'notifications',
        'messages',
        'sessions',
    ]

    # Helper
    deletions = []

    def delete_where(table: str, col: str):
        if table not in tables:
            return
        if col not in schema.get(table, []):
            return
        # Retry loop to handle transient locks
        attempts = 0
        while True:
            try:
                cur.execute(f"DELETE FROM {table} WHERE {col}=?", (user_id,))
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempts < 20:
                    attempts += 1
                    time.sleep(0.5)
                    continue
                raise
        deletions.append((table, col, cur.rowcount))

    try:
        con.isolation_level = None
        # Try to acquire write lock immediately with retries
        attempts = 0
        while True:
            try:
                cur.execute("BEGIN IMMEDIATE")
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempts < 20:
                    attempts += 1
                    time.sleep(0.5)
                    continue
                raise

        # 1) Targeted known child tables first
        for t in preferred_order:
            for c in (user_cols & set(schema.get(t, []))):
                delete_where(t, c)

        # 2) Delete leagues created/admined by this user (if present)
        for col in ("created_by", "admin_id", "owner_id"):
            delete_where("leagues", col)

        # 3) Generic sweep over all tables that have a user-like column
        for t in tables:
            for col in (user_cols & set(schema.get(t, []))):
                delete_where(t, col)

        # 4) Finally, delete user row
        delete_where("users", "user_id")

        cur.execute("COMMIT")
        print("Committed.")
    except Exception as e:
        try:
            cur.execute("ROLLBACK")
        except Exception:
            pass
        print("Error:", e)
        raise
    finally:
        con.close()

    # Report
    changed = [f"{t}({c})={n}" for (t, c, n) in deletions if n]
    if changed:
        print("Deleted rows:")
        for line in changed:
            print(" -", line)
    else:
        print("No matching rows found for the specified user.")


if __name__ == "__main__":
    main()



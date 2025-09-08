"""
Seed or upsert expanded achievement definitions safely.

Usage:
  python scripts/seed_achievements.py
"""

import sys
from pathlib import Path

# Ensure src is importable when run directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.database.database import db_manager


EXPANDED_DEFINITIONS = [
    # Expanded overall page milestones
    ("200_pages", "📄 Steady Reader", "Read 200 pages", "📄", 80),
    ("300_pages", "📄 Avid Reader", "Read 300 pages", "📄", 120),
    ("750_pages", "📄 Page Explorer", "Read 750 pages", "📄", 350),
    ("1500_pages", "📄 Page Conqueror", "Read 1500 pages", "📄", 800),
    ("3000_pages", "📄 Page Veteran", "Read 3000 pages", "📄", 1200),
    ("10000_pages", "📄 Page Legend", "Read 10000 pages", "📄", 4000),

    # Expanded league milestones
    ("league_300_pages", "🏆 League 300 Pages", "Read 300 pages in a league", "🏆", 60),
    ("league_750_pages", "🏆 League 750 Pages", "Read 750 pages in a league", "🏆", 160),
    ("league_3000_pages", "🏆 League 3000 Pages", "Read 3000 pages in a league", "🏆", 700),
    ("league_5000_pages", "🏆 League 5000 Pages", "Read 5000 pages in a league", "🏆", 1200),
]


def upsert_definitions():
    with db_manager.get_connection() as conn:
        cur = conn.cursor()
        for typ, title, desc, icon, xp in EXPANDED_DEFINITIONS:
            cur.execute(
                """
                INSERT INTO achievement_definitions (type, title, description, icon, xp_reward, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(type) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    icon=excluded.icon,
                    xp_reward=excluded.xp_reward,
                    is_active=1
                """,
                (typ, title, desc, icon, xp),
            )
        conn.commit()


if __name__ == "__main__":
    upsert_definitions()
    print("Expanded achievement definitions seeded.")



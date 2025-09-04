"""
Reminder service to manage user reading reminders.
"""

from typing import Optional, List, Dict
from datetime import time
import re

from src.database.database import db_manager


class ReminderService:
    """CRUD operations for reminders."""

    TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")

    def parse_time(self, time_str: str) -> Optional[time]:
        m = self.TIME_RE.match(time_str.strip())
        if not m:
            return None
        hh = int(m.group(1))
        mm = int(m.group(2))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return None
        return time(hour=hh, minute=mm)

    def set_reminder(self, user_id: int, t: time, frequency: str = "daily") -> None:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            # upsert by user
            cur.execute(
                """
                INSERT INTO reminders (user_id, reminder_time, frequency, is_active, created_at)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    reminder_time = excluded.reminder_time,
                    frequency = excluded.frequency,
                    is_active = 1
                """,
                (user_id, t.strftime("%H:%M:00"), frequency),
            )
            conn.commit()

    def get_reminder(self, user_id: int) -> Optional[Dict]:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT reminder_time, frequency, is_active, last_sent FROM reminders WHERE user_id = ?",
                (user_id,),
            )
            r = cur.fetchone()
            if not r:
                return None
            return {
                "reminder_time": str(r[0]),
                "frequency": r[1],
                "is_active": bool(r[2]),
                "last_sent": str(r[3]) if r[3] else None,
            }

    def remove_reminder(self, user_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE reminders SET is_active = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            return cur.rowcount > 0

    def list_active_reminders(self) -> List[Dict]:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, reminder_time, frequency FROM reminders WHERE is_active = 1"
            )
            rows = cur.fetchall()
            res: List[Dict] = []
            for r in rows:
                res.append(
                    {
                        "user_id": int(r[0]),
                        "reminder_time": str(r[1]),
                        "frequency": r[2],
                    }
                )
            return res

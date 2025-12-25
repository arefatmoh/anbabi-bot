"""
Reminder service to manage user reading reminders.
"""

from typing import Optional, List, Dict
from datetime import time
import re

from src.database.database import db_manager


class ReminderService:
    """CRUD operations for reminders.

    Notes on time handling:
    - We interpret input/output times as Ethiopia local time (GMT+3).
    - We accept both 24-hour (HH:MM) and 12-hour (h:MM AM/PM) inputs.
    - We store as 24-hour HH:MM:SS string in the database.
    """

    TIME_24H_RE = re.compile(r"^(\d{1,2}):(\d{2})$")
    TIME_12H_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*([AaPp][Mm])$")

    def parse_time(self, time_str: str) -> Optional[time]:
        s = time_str.strip()
        m12 = self.TIME_12H_RE.match(s)
        if m12:
            hh = int(m12.group(1))
            mm = int(m12.group(2))
            ampm = m12.group(3).lower()
            if not (1 <= hh <= 12 and 0 <= mm <= 59):
                return None
            if ampm == 'pm' and hh != 12:
                hh += 12
            if ampm == 'am' and hh == 12:
                hh = 0
            return time(hour=hh, minute=mm)
        m24 = self.TIME_24H_RE.match(s)
        if m24:
            hh = int(m24.group(1))
            mm = int(m24.group(2))
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                return None
            return time(hour=hh, minute=mm)
        return None

    def format_time_12h(self, t: time) -> str:
        hh = t.hour
        mm = t.minute
        ampm = 'AM'
        if hh == 0:
            out_h = 12
            ampm = 'AM'
        elif 1 <= hh < 12:
            out_h = hh
            ampm = 'AM'
        elif hh == 12:
            out_h = 12
            ampm = 'PM'
        else:
            out_h = hh - 12
            ampm = 'PM'
        return f"{out_h}:{mm:02d} {ampm}"

    def set_reminder(self, user_id: int, t: time, frequency: str = "daily") -> None:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            # update-then-insert to avoid ON CONFLICT requirement
            cur.execute(
                """
                UPDATE reminders
                SET reminder_time = %s, frequency = %s, is_active = TRUE
                WHERE user_id = %s
                """,
                (t.strftime("%H:%M:00"), frequency, user_id),
            )
            if cur.rowcount == 0:
                cur.execute(
                    """
                    INSERT INTO reminders (user_id, reminder_time, frequency, is_active, created_at)
                    VALUES (%s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                    """,
                    (user_id, t.strftime("%H:%M:00"), frequency),
                )
            conn.commit()

    def get_reminder(self, user_id: int) -> Optional[Dict]:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT reminder_time, frequency, is_active, last_sent FROM reminders WHERE user_id = %s",
                (user_id,),
            )
            r = cur.fetchone()
            if not r:
                return None
            return {
                "reminder_time": str(r['reminder_time']),
                "frequency": r['frequency'],
                "is_active": bool(r['is_active']),
                "last_sent": str(r['last_sent']) if r['last_sent'] else None,
            }

    def remove_reminder(self, user_id: int) -> bool:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE reminders SET is_active = FALSE WHERE user_id = %s", (user_id,))
            conn.commit()
            return cur.rowcount > 0

    def list_active_reminders(self) -> List[Dict]:
        with db_manager.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, reminder_time, frequency FROM reminders WHERE is_active = TRUE"
            )
            rows = cur.fetchall()
            res: List[Dict] = []
            for r in rows:
                res.append(
                    {
                        "user_id": int(r['user_id']),
                        "reminder_time": str(r['reminder_time']),
                        "frequency": r['frequency'],
                    }
                )
            return res

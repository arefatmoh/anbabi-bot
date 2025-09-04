"""
League repository for database operations.

This module handles all database operations related to leagues and league members.
"""

import logging
from datetime import date, datetime
from typing import List, Optional, Dict, Tuple
from sqlite3 import Connection

from src.database.models.league import League
from src.database.models.league_member import LeagueMember
from src.config.constants import LeagueStatus


class LeagueRepository:
    """Repository for league-related database operations."""
    
    def __init__(self, db_connection: Connection):
        """Initialize league repository."""
        self.conn = db_connection
        self.logger = logging.getLogger(__name__)
    
    def create_league(self, league: League) -> int:
        """Create a new league and return its ID."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO leagues (
                    name, description, admin_id, current_book_id,
                    start_date, end_date, daily_goal, max_members,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                league.name, league.description, league.admin_id,
                league.current_book_id, league.start_date, league.end_date,
                league.daily_goal, league.max_members, league.status.value,
                league.created_at
            ))
            
            league_id = cursor.lastrowid
            self.conn.commit()
            
            self.logger.info(f"Created league '{league.name}' with ID {league_id}")
            return league_id
            
        except Exception as e:
            self.logger.error(f"Failed to create league: {e}")
            self.conn.rollback()
            raise
    
    def get_league_by_id(self, league_id: int) -> Optional[League]:
        """Get league by ID."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT league_id, name, description, admin_id, current_book_id,
                       start_date, end_date, daily_goal, max_members, status, created_at
                FROM leagues WHERE league_id = ?
            """, (league_id,))
            
            row = cursor.fetchone()
            if row:
                return League(
                    league_id=row[0], name=row[1], description=row[2],
                    admin_id=row[3], current_book_id=row[4], start_date=row[5],
                    end_date=row[6], daily_goal=row[7], max_members=row[8],
                    status=LeagueStatus(row[9]), created_at=row[10]
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get league {league_id}: {e}")
            raise
    
    def get_active_leagues(self) -> List[League]:
        """Get all active leagues."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT league_id, name, description, admin_id, current_book_id,
                       start_date, end_date, daily_goal, max_members, status, created_at
                FROM leagues WHERE status = ? ORDER BY created_at DESC
            """, (LeagueStatus.ACTIVE.value,))
            
            leagues = []
            for row in cursor.fetchall():
                league = League(
                    league_id=row[0], name=row[1], description=row[2],
                    admin_id=row[3], current_book_id=row[4], start_date=row[5],
                    end_date=row[6], daily_goal=row[7], max_members=row[8],
                    status=LeagueStatus(row[9]), created_at=row[10]
                )
                leagues.append(league)
            
            return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get active leagues: {e}")
            raise
    
    def get_leagues_by_admin(self, admin_id: int) -> List[League]:
        """Get all leagues created by a specific admin."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT league_id, name, description, admin_id, current_book_id,
                       start_date, end_date, daily_goal, max_members, status, created_at
                FROM leagues WHERE admin_id = ? ORDER BY created_at DESC
            """, (admin_id,))
            
            leagues = []
            for row in cursor.fetchall():
                league = League(
                    league_id=row[0], name=row[1], description=row[2],
                    admin_id=row[3], current_book_id=row[4], start_date=row[5],
                    end_date=row[6], daily_goal=row[7], max_members=row[8],
                    status=LeagueStatus(row[9]), created_at=row[10]
                )
                leagues.append(league)
            
            return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get leagues for admin {admin_id}: {e}")
            raise
    
    def update_league_status(self, league_id: int, status: LeagueStatus) -> bool:
        """Update league status."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                UPDATE leagues SET status = ? WHERE league_id = ?
            """, (status.value, league_id))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                self.logger.info(f"Updated league {league_id} status to {status.value}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update league {league_id} status: {e}")
            self.conn.rollback()
            raise
    
    def add_member_to_league(self, league_id: int, user_id: int) -> bool:
        """Add a user to a league."""
        try:
            cursor = self.conn.cursor()
            
            # Check if user is already a member
            cursor.execute("""
                SELECT 1 FROM league_members 
                WHERE league_id = ? AND user_id = ?
            """, (league_id, user_id))
            
            if cursor.fetchone():
                self.logger.warning(f"User {user_id} is already a member of league {league_id}")
                return False
            
            # Check if league is full
            cursor.execute("""
                SELECT COUNT(*) FROM league_members 
                WHERE league_id = ? AND is_active = 1
            """, (league_id,))
            
            current_members = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT max_members FROM leagues WHERE league_id = ?
            """, (league_id,))
            
            max_members = cursor.fetchone()[0]
            
            if current_members >= max_members:
                self.logger.warning(f"League {league_id} is full")
                return False
            
            # Add member
            cursor.execute("""
                INSERT INTO league_members (league_id, user_id, joined_at, is_active)
                VALUES (?, ?, ?, 1)
            """, (league_id, user_id, datetime.now()))
            
            self.conn.commit()
            self.logger.info(f"Added user {user_id} to league {league_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add member to league: {e}")
            self.conn.rollback()
            raise
    
    def remove_member_from_league(self, league_id: int, user_id: int) -> bool:
        """Remove a user from a league."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                UPDATE league_members 
                SET is_active = 0 
                WHERE league_id = ? AND user_id = ?
            """, (league_id, user_id))
            
            if cursor.rowcount > 0:
                self.conn.commit()
                self.logger.info(f"Removed user {user_id} from league {league_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove member from league: {e}")
            self.conn.rollback()
            raise
    
    def get_league_members(self, league_id: int) -> List[LeagueMember]:
        """Get all active members of a league."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT league_id, user_id, joined_at, is_active
                FROM league_members 
                WHERE league_id = ? AND is_active = 1
                ORDER BY joined_at ASC
            """, (league_id,))
            
            members = []
            for row in cursor.fetchall():
                member = LeagueMember(
                    league_id=row[0], user_id=row[1],
                    joined_at=row[2], is_active=bool(row[3])
                )
                members.append(member)
            
            return members
            
        except Exception as e:
            self.logger.error(f"Failed to get league members: {e}")
            raise
    
    def get_user_leagues(self, user_id: int) -> List[League]:
        """Get all leagues a user is a member of."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT l.league_id, l.name, l.description, l.admin_id, l.current_book_id,
                       l.start_date, l.end_date, l.daily_goal, l.max_members, l.status, l.created_at
                FROM leagues l
                JOIN league_members lm ON l.league_id = lm.league_id
                WHERE lm.user_id = ? AND lm.is_active = 1
                ORDER BY l.created_at DESC
            """, (user_id,))
            
            leagues = []
            for row in cursor.fetchall():
                league = League(
                    league_id=row[0], name=row[1], description=row[2],
                    admin_id=row[3], current_book_id=row[4], start_date=row[5],
                    end_date=row[6], daily_goal=row[7], max_members=row[8],
                    status=LeagueStatus(row[9]), created_at=row[10]
                )
                leagues.append(league)
            
            return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get user leagues: {e}")
            raise
    
    def get_league_member_count(self, league_id: int) -> int:
        """Get the current number of active members in a league."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM league_members 
                WHERE league_id = ? AND is_active = 1
            """, (league_id,))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            self.logger.error(f"Failed to get league member count: {e}")
            raise
    
    def is_user_member(self, league_id: int, user_id: int) -> bool:
        """Check if a user is a member of a league."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM league_members 
                WHERE league_id = ? AND user_id = ? AND is_active = 1
            """, (league_id, user_id))
            
            return cursor.fetchone() is not None
            
        except Exception as e:
            self.logger.error(f"Failed to check user membership: {e}")
            raise

    def update_goal(self, league_id: int, daily_goal: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE leagues SET daily_goal = ? WHERE league_id = ?", (daily_goal, league_id))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update goal: {e}")
            self.conn.rollback()
            raise

    def update_dates(self, league_id: int, start_date: date, end_date: date) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE leagues SET start_date = ?, end_date = ? WHERE league_id = ?",
                (start_date, end_date, league_id),
            )
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update dates: {e}")
            self.conn.rollback()
            raise

    def update_max_members(self, league_id: int, max_members: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE leagues SET max_members = ? WHERE league_id = ?", (max_members, league_id))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update max_members: {e}")
            self.conn.rollback()
            raise

    def update_book(self, league_id: int, book_id: int) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE leagues SET current_book_id = ? WHERE league_id = ?", (book_id, league_id))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update book: {e}")
            self.conn.rollback()
            raise

    def export_league_rows(self, league_id: int) -> List[Dict]:
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT u.full_name, u.username, u.city, b.title, b.author, b.total_pages,
                       ub.pages_read, ub.start_date, ub.last_updated
                FROM league_members lm
                JOIN users u ON u.user_id = lm.user_id
                LEFT JOIN user_books ub ON ub.user_id = lm.user_id
                LEFT JOIN books b ON b.book_id = ub.book_id
                WHERE lm.league_id = ? AND lm.is_active = 1
                ORDER BY u.full_name
                """,
                (league_id,),
            )
            rows = cur.fetchall()
            out: List[Dict] = []
            for r in rows:
                out.append(
                    {
                        "full_name": r[0] or "",
                        "username": r[1] or "",
                        "city": r[2] or "",
                        "book_title": r[3] or "",
                        "book_author": r[4] or "",
                        "total_pages": int(r[5] or 0),
                        "pages_read": int(r[6] or 0),
                        "start_date": str(r[7] or ""),
                        "last_updated": str(r[8] or ""),
                    }
                )
            return out
        except Exception as e:
            self.logger.error(f"Failed to export league rows: {e}")
            return []

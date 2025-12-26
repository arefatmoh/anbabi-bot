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
    
    def __init__(self, db_manager):
        """Initialize league repository with database manager."""
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def create_league(self, league: League) -> int:
        """Create a new league and return its ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO leagues (
                        name, description, admin_id, current_book_id,
                        start_date, end_date, daily_goal, max_members,
                        status, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING league_id
                """, (
                    league.name, league.description, league.admin_id,
                    league.current_book_id, league.start_date, league.end_date,
                    league.daily_goal, league.max_members, league.status.value,
                    league.created_at
                ))
                
                league_id = cursor.fetchone()['league_id']
                conn.commit()
                
                self.logger.info(f"Created league '{league.name}' with ID {league_id}")
                return league_id
            
        except Exception as e:
            self.logger.error(f"Failed to create league: {e}")
            raise
    
    def get_league_by_id(self, league_id: int) -> Optional[League]:
        """Get league by ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT league_id, name, description, admin_id, current_book_id,
                           start_date, end_date, daily_goal, max_members, status, created_at
                    FROM leagues WHERE league_id = %s
                """, (league_id,))
                
                row = cursor.fetchone()
                if row:
                    return League(
                        league_id=row['league_id'],
                        name=row['name'],
                        description=row['description'],
                        admin_id=row['admin_id'],
                        current_book_id=row['current_book_id'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        daily_goal=row['daily_goal'],
                        max_members=row['max_members'],
                        status=LeagueStatus(row['status']),
                        created_at=row['created_at']
                    )
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to get league {league_id}: {e}")
            raise
    
    def get_active_leagues(self) -> List[League]:
        """Get all active leagues."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT league_id, name, description, admin_id, current_book_id,
                           start_date, end_date, daily_goal, max_members, status, created_at
                    FROM leagues WHERE status = %s ORDER BY created_at DESC
                """, (LeagueStatus.ACTIVE.value,))
                
                leagues = []
                for row in cursor.fetchall():
                    league = League(
                        league_id=row['league_id'],
                        name=row['name'],
                        description=row['description'],
                        admin_id=row['admin_id'],
                        current_book_id=row['current_book_id'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        daily_goal=row['daily_goal'],
                        max_members=row['max_members'],
                        status=LeagueStatus(row['status']),
                        created_at=row['created_at']
                    )
                    leagues.append(league)
                
                return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get active leagues: {e}")
            raise
    
    def get_all_leagues(self) -> List[League]:
        """Get all leagues (active and inactive)."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT league_id, name, description, admin_id, current_book_id,
                           start_date, end_date, daily_goal, max_members, status, created_at
                    FROM leagues ORDER BY created_at DESC
                """)
                
                leagues = []
                for row in cursor.fetchall():
                    league = League(
                        league_id=row['league_id'],
                        name=row['name'],
                        description=row['description'],
                        admin_id=row['admin_id'],
                        current_book_id=row['current_book_id'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        daily_goal=row['daily_goal'],
                        max_members=row['max_members'],
                        status=LeagueStatus(row['status']),
                        created_at=row['created_at']
                    )
                    leagues.append(league)
                
                return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get all leagues: {e}")
            raise
    
    def get_leagues_by_admin(self, admin_id: int) -> List[League]:
        """Get all leagues created by a specific admin."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT league_id, name, description, admin_id, current_book_id,
                           start_date, end_date, daily_goal, max_members, status, created_at
                    FROM leagues WHERE admin_id = %s ORDER BY created_at DESC
                """, (admin_id,))
                
                leagues = []
                for row in cursor.fetchall():
                    league = League(
                        league_id=row['league_id'],
                        name=row['name'],
                        description=row['description'],
                        admin_id=row['admin_id'],
                        current_book_id=row['current_book_id'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        daily_goal=row['daily_goal'],
                        max_members=row['max_members'],
                        status=LeagueStatus(row['status']),
                        created_at=row['created_at']
                    )
                    leagues.append(league)
                
                return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get leagues for admin {admin_id}: {e}")
            raise
    
    def update_league_status(self, league_id: int, status: LeagueStatus) -> bool:
        """Update league status."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE leagues SET status = %s WHERE league_id = %s
                """, (status.value, league_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"Updated league {league_id} status to {status.value}")
                    return True
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to update league {league_id} status: {e}")
            raise
    
    def add_member_to_league(self, league_id: int, user_id: int) -> bool:
        """Add a user to a league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user is already a member
                cursor.execute("""
                    SELECT 1 FROM league_members 
                    WHERE league_id = %s AND user_id = %s
                """, (league_id, user_id))
                
                if cursor.fetchone():
                    self.logger.warning(f"User {user_id} is already a member of league {league_id}")
                    return False
                
                # Check if league is full
                cursor.execute("""
                    SELECT COUNT(*) as count FROM league_members 
                    WHERE league_id = %s AND is_active = TRUE
                """, (league_id,))
                
                current_members = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT max_members FROM leagues WHERE league_id = %s
                """, (league_id,))
                
                max_members = cursor.fetchone()['max_members']
                
                if current_members >= max_members:
                    self.logger.warning(f"League {league_id} is full")
                    return False
                
                # Add member
                cursor.execute("""
                    INSERT INTO league_members (league_id, user_id, joined_at, is_active)
                    VALUES (%s, %s, %s, TRUE)
                """, (league_id, user_id, datetime.now()))
                
                conn.commit()
                self.logger.info(f"Added user {user_id} to league {league_id}")
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to add member to league: {e}")
            raise
    
    def remove_member_from_league(self, league_id: int, user_id: int) -> bool:
        """Remove a user from a league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE league_members 
                    SET is_active = FALSE 
                    WHERE league_id = %s AND user_id = %s
                """, (league_id, user_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"Removed user {user_id} from league {league_id}")
                    return True
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove member from league: {e}")
            raise
    
    def get_league_members(self, league_id: int) -> List[LeagueMember]:
        """Get all active members of a league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT league_id, user_id, joined_at, is_active
                    FROM league_members 
                    WHERE league_id = %s AND is_active = TRUE
                    ORDER BY joined_at ASC
                """, (league_id,))
                
                members = []
                for row in cursor.fetchall():
                    member = LeagueMember(
                        league_id=row['league_id'],
                        user_id=row['user_id'],
                        joined_at=row['joined_at'],
                        is_active=bool(row['is_active'])
                    )
                    members.append(member)
                
                return members
            
        except Exception as e:
            self.logger.error(f"Failed to get league members: {e}")
            raise
    
    def get_user_leagues(self, user_id: int) -> List[League]:
        """Get all leagues a user is a member of."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT l.league_id, l.name, l.description, l.admin_id, l.current_book_id,
                           l.start_date, l.end_date, l.daily_goal, l.max_members, l.status, l.created_at
                    FROM leagues l
                    JOIN league_members lm ON l.league_id = lm.league_id
                    WHERE lm.user_id = %s AND lm.is_active = TRUE
                    ORDER BY l.created_at DESC
                """, (user_id,))
                
                leagues = []
                for row in cursor.fetchall():
                    league = League(
                        league_id=row['league_id'],
                        name=row['name'],
                        description=row['description'],
                        admin_id=row['admin_id'],
                        current_book_id=row['current_book_id'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        daily_goal=row['daily_goal'],
                        max_members=row['max_members'],
                        status=LeagueStatus(row['status']),
                        created_at=row['created_at']
                    )
                    leagues.append(league)
                
                return leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get user leagues: {e}")
            raise
    
    def get_league_member_count(self, league_id: int) -> int:
        """Get the current number of active members in a league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT COUNT(*) as count FROM league_members 
                    WHERE league_id = %s AND is_active = TRUE
                """, (league_id,))
                
                return cursor.fetchone()['count']
            
        except Exception as e:
            self.logger.error(f"Failed to get league member count: {e}")
            raise
    
    def is_user_member(self, league_id: int, user_id: int) -> bool:
        """Check if a user is a member of a league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 1 FROM league_members 
                    WHERE league_id = %s AND user_id = %s AND is_active = TRUE
                """, (league_id, user_id))
                
                return cursor.fetchone() is not None
            
        except Exception as e:
            self.logger.error(f"Failed to check user membership: {e}")
            raise

    def update_goal(self, league_id: int, daily_goal: int) -> bool:
        try:
            with self.db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE leagues SET daily_goal = %s WHERE league_id = %s", (daily_goal, league_id))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update goal: {e}")
            raise

    def update_dates(self, league_id: int, start_date: date, end_date: date) -> bool:
        try:
            with self.db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE leagues SET start_date = %s, end_date = %s WHERE league_id = %s",
                    (start_date, end_date, league_id),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update dates: {e}")
            raise

    def update_max_members(self, league_id: int, max_members: int) -> bool:
        try:
            with self.db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE leagues SET max_members = %s WHERE league_id = %s", (max_members, league_id))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update max_members: {e}")
            raise

    def update_book(self, league_id: int, book_id: int) -> bool:
        try:
            with self.db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE leagues SET current_book_id = %s WHERE league_id = %s", (book_id, league_id))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Failed to update book: {e}")
            raise

    def export_league_rows(self, league_id: int) -> List[Dict]:
        try:
            with self.db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT u.full_name, u.city, b.title, b.author, b.total_pages,
                           ub.pages_read, ub.start_date, ub.last_updated
                    FROM league_members lm
                    JOIN users u ON u.user_id = lm.user_id
                    LEFT JOIN user_books ub ON ub.user_id = lm.user_id
                    LEFT JOIN books b ON b.book_id = ub.book_id
                    WHERE lm.league_id = %s AND lm.is_active = TRUE
                    ORDER BY u.full_name
                    """,
                    (league_id,),
                )
                rows = cur.fetchall()
                out: List[Dict] = []
                for r in rows:
                    out.append(
                        {
                            "full_name": r['full_name'] or "",
                            
                            "city": r['city'] or "",
                            "book_title": r['title'] or "",
                            "book_author": r['author'] or "",
                            "total_pages": int(r['total_pages'] or 0),
                            "pages_read": int(r['pages_read'] or 0),
                            "start_date": str(r['start_date'] or ""),
                            "last_updated": str(r['last_updated'] or ""),
                        }
                    )
                return out
        except Exception as e:
            self.logger.error(f"Failed to export league rows: {e}")
            return []

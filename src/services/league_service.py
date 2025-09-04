"""
League service for business logic.

This module handles all business logic related to league management.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional, Dict, Tuple

from src.database.repositories.league_repository import LeagueRepository
from src.database.models.league import League
from src.database.models.league_member import LeagueMember
from src.config.constants import LeagueStatus
from src.config.settings import DEFAULT_LEAGUE_DURATION_DAYS
from src.database.database import db_manager


class LeagueService:
    """Service for league-related business logic."""
    
    def __init__(self, league_repo: LeagueRepository):
        """Initialize league service."""
        self.league_repo = league_repo
        self.logger = logging.getLogger(__name__)
    
    def create_league(
        self,
        name: str,
        admin_id: int,
        book_id: int,
        start_date: Optional[date] = None,
        duration_days: int = DEFAULT_LEAGUE_DURATION_DAYS,
        daily_goal: int = 20,
        max_members: int = 50,
        description: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Create a new reading league.
        
        Returns:
            Tuple of (success, message, league_id)
        """
        try:
            # Set default start date to tomorrow if not provided
            if not start_date:
                start_date = date.today() + timedelta(days=1)
            
            # Calculate end date
            end_date = start_date + timedelta(days=duration_days)
            
            # Validate dates
            if start_date <= date.today():
                return False, "Start date must be in the future", None
            
            # Create league
            league = League.create(
                name=name,
                admin_id=admin_id,
                current_book_id=book_id,
                start_date=start_date,
                end_date=end_date,
                daily_goal=daily_goal,
                max_members=max_members,
                description=description
            )
            
            # Save to database
            league_id = self.league_repo.create_league(league)
            
            # Add admin as first member
            self.league_repo.add_member_to_league(league_id, admin_id)
            
            self.logger.info(f"Created league '{name}' with ID {league_id}")
            return True, f"League '{name}' created successfully!", league_id
            
        except Exception as e:
            self.logger.error(f"Failed to create league: {e}")
            return False, f"Failed to create league: {str(e)}", None
    
    def get_available_leagues(self, user_id: int) -> List[League]:
        """Get leagues available for a user to join."""
        try:
            # Get all active leagues
            active_leagues = self.league_repo.get_active_leagues()
            
            # Filter out leagues the user is already a member of
            available_leagues = []
            for league in active_leagues:
                if not self.league_repo.is_user_member(league.league_id, user_id):
                    # Check if league is full
                    member_count = self.league_repo.get_league_member_count(
                        league.league_id
                    )
                    if member_count < league.max_members:
                        available_leagues.append(league)
            
            return available_leagues
            
        except Exception as e:
            self.logger.error(f"Failed to get available leagues: {e}")
            return []
    
    def join_league(self, league_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Add a user to a league.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if league exists and is active
            league = self.league_repo.get_league_by_id(league_id)
            if not league:
                return False, "League not found"
            
            if not league.is_active:
                return False, "League is not active"
            
            # Check if user is already a member
            if self.league_repo.is_user_member(league_id, user_id):
                return False, "You are already a member of this league"
            
            # Check if league is full
            member_count = self.league_repo.get_league_member_count(league_id)
            if member_count >= league.max_members:
                return False, "League is full"
            
            # Add user to league
            success = self.league_repo.add_member_to_league(league_id, user_id)
            
            if success:
                self.logger.info(f"User {user_id} joined league {league_id}")
                return True, f"Successfully joined '{league.name}'!"
            else:
                return False, "Failed to join league"
                
        except Exception as e:
            self.logger.error(f"Failed to join league: {e}")
            return False, f"Failed to join league: {str(e)}"
    
    def leave_league(self, league_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Remove a user from a league.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if user is a member
            if not self.league_repo.is_user_member(league_id, user_id):
                return False, "You are not a member of this league"
            
            # Remove user from league
            success = self.league_repo.remove_member_from_league(league_id, user_id)
            
            if success:
                self.logger.info(f"User {user_id} left league {league_id}")
                return True, "Successfully left the league"
            else:
                return False, "Failed to leave league"
                
        except Exception as e:
            self.logger.error(f"Failed to leave league: {e}")
            return False, f"Failed to leave league: {str(e)}"
    
    def get_user_leagues(self, user_id: int) -> List[League]:
        """Get all leagues a user is a member of."""
        try:
            return self.league_repo.get_user_leagues(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get user leagues: {e}")
            return []
    
    def get_league_info(self, league_id: int, user_id: int) -> Optional[Dict]:
        """Get detailed information about a league."""
        try:
            league = self.league_repo.get_league_by_id(league_id)
            if not league:
                return None
            
            # Get member count
            member_count = self.league_repo.get_league_member_count(league_id)
            
            # Check if user is a member
            is_member = self.league_repo.is_user_member(league_id, user_id)
            
            # Check if user is admin
            is_admin = league.admin_id == user_id
            
            return {
                'league': league.to_dict(),
                'member_count': member_count,
                'is_member': is_member,
                'is_admin': is_admin,
                'can_join': not is_member and league.is_active and member_count < league.max_members
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get league info: {e}")
            return None
    
    def get_league_leaderboard(self, league_id: int) -> List[Dict]:
        """Compute a simple leaderboard for a league based on user progress."""
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT u.full_name, u.username, ub.user_id, b.title,
                           ub.pages_read, b.total_pages,
                           ROUND(CASE WHEN b.total_pages > 0 THEN (ub.pages_read * 100.0) / b.total_pages ELSE 0 END, 1) AS pct
                    FROM league_members lm
                    JOIN users u ON u.user_id = lm.user_id
                    JOIN user_books ub ON ub.user_id = lm.user_id
                    JOIN books b ON b.book_id = ub.book_id
                    WHERE lm.league_id = ? AND lm.is_active = 1
                    ORDER BY pct DESC, ub.pages_read DESC
                    """,
                    (league_id,),
                )
                rows = cur.fetchall()
                leaderboard: List[Dict] = []
                rank = 1
                for r in rows:
                    leaderboard.append(
                        {
                            "rank": rank,
                            "full_name": r[0] or "",
                            "username": r[1] or "",
                            "user_id": r[2],
                            "book_title": r[3],
                            "pages_read": int(r[4] or 0),
                            "total_pages": int(r[5] or 0),
                            "progress_percent": float(r[6] or 0.0),
                        }
                    )
                    rank += 1
                return leaderboard
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    def update_league_status(self, league_id: int, admin_id: int, status: LeagueStatus) -> Tuple[bool, str]:
        """
        Update league status (admin only).
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if user is admin
            league = self.league_repo.get_league_by_id(league_id)
            if not league:
                return False, "League not found"
            
            if league.admin_id != admin_id:
                return False, "Only league admin can update status"
            
            # Update status
            success = self.league_repo.update_league_status(league_id, status)
            
            if success:
                self.logger.info(f"League {league_id} status updated to {status.value}")
                return True, f"League status updated to {status.value}"
            else:
                return False, "Failed to update league status"
                
        except Exception as e:
            self.logger.error(f"Failed to update league status: {e}")
            return False, f"Failed to update league status: {str(e)}"
    
    def get_all_leagues(self) -> List[Dict]:
        """Get all leagues with member counts."""
        try:
            leagues = self.league_repo.get_all_leagues()
            result = []
            for league in leagues:
                member_count = self.league_repo.get_league_member_count(league.league_id)
                league_dict = {
                    'league_id': league.league_id,
                    'name': league.name,
                    'status': league.status,
                    'member_count': member_count,
                    'max_members': league.max_members,
                    'duration_days': league.duration_days,
                }
                result.append(league_dict)
            return result
        except Exception as e:
            self.logger.error(f"Error getting all leagues: {e}")
            return []

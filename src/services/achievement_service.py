"""
Achievement Service for gamification system.

This service handles achievement tracking, streak management, and XP calculation.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json

from src.database.database import db_manager
from src.database.models.achievement import Achievement, AchievementDefinition, UserStats


class AchievementService:
    """Service for managing achievements and user statistics."""
    
    def __init__(self):
        """Initialize the achievement service."""
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
    
    def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Get user statistics."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_stats WHERE user_id = %s
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return UserStats.from_dict(dict(row))
                else:
                    # Create default stats for new user
                    return self._create_default_user_stats(user_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to get user stats for user {user_id}: {e}")
            return None
    
    def _create_default_user_stats(self, user_id: int) -> UserStats:
        """Create default user statistics."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                cursor.execute('''
                    INSERT INTO user_stats (user_id, created_at, updated_at)
                    VALUES (%s, %s, %s)
                ''', (user_id, now, now))
                
                conn.commit()
                return UserStats(
                    user_id=user_id,
                    created_at=now,
                    updated_at=now
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create default user stats for user {user_id}: {e}")
            return UserStats(user_id=user_id)
    
    def update_user_stats(self, user_id: int, **kwargs) -> bool:
        """Update user statistics."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current stats
                current_stats = self.get_user_stats(user_id)
                if not current_stats:
                    return False
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(current_stats, key):
                        setattr(current_stats, key, value)
                
                # Update database
                cursor.execute('''
                    UPDATE user_stats SET
                        current_streak = %s, longest_streak = %s, total_achievements = %s,
                        level = %s, xp = %s, books_completed = %s, total_pages_read = %s,
                        last_reading_date = %s, streak_start_date = %s, updated_at = %s
                    WHERE user_id = %s
                ''', (
                    current_stats.current_streak,
                    current_stats.longest_streak,
                    current_stats.total_achievements,
                    current_stats.level,
                    current_stats.xp,
                    current_stats.books_completed,
                    current_stats.total_pages_read,
                    current_stats.last_reading_date.isoformat() if current_stats.last_reading_date else None,
                    current_stats.streak_start_date.isoformat() if current_stats.streak_start_date else None,
                    datetime.now().isoformat(),
                    user_id
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update user stats for user {user_id}: {e}")
            return False
    
    def update_reading_progress(self, user_id: int, pages_read: int, book_id: int) -> List[Achievement]:
        """Update reading progress and check for achievements."""
        try:
            new_achievements = []
            today = date.today()
            
            # Get current stats
            stats = self.get_user_stats(user_id)
            if not stats:
                return new_achievements
            
            # Update total pages read
            stats.total_pages_read += pages_read
            
            # Update streak
            if stats.last_reading_date:
                last_date = stats.last_reading_date.date() if isinstance(stats.last_reading_date, datetime) else stats.last_reading_date
                if last_date == today:
                    # Already read today, no streak change
                    pass
                elif last_date == today - timedelta(days=1):
                    # Consecutive day, increment streak
                    stats.current_streak += 1
                    if not stats.streak_start_date:
                        stats.streak_start_date = datetime.combine(last_date, datetime.min.time())
                else:
                    # Streak broken, reset
                    stats.current_streak = 1
                    stats.streak_start_date = datetime.combine(today, datetime.min.time())
            else:
                # First reading
                stats.current_streak = 1
                stats.streak_start_date = datetime.combine(today, datetime.min.time())
            
            stats.last_reading_date = datetime.combine(today, datetime.min.time())
            
            # Update longest streak
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
            
            # Check for streak achievements
            streak_achievements = self._check_streak_achievements(user_id, stats.current_streak)
            new_achievements.extend(streak_achievements)
            
            # Check for page reading achievements
            page_achievements = self._check_page_achievements(user_id, stats.total_pages_read)
            new_achievements.extend(page_achievements)
            
            # Award base XP for reading activity (1 XP per page)
            # This ensures users always get some progress even without hitting milestones
            base_xp = pages_read
            stats.xp += base_xp
            
            # Calculate total pages read TODAY across all books/sessions
            # This ensures daily achievements work cumulatively
            total_daily_pages = self._get_daily_pages_read(user_id)
            
            # Check for daily reading achievements using cumulative total
            daily_achievements = self._check_daily_achievements(user_id, total_daily_pages)
            new_achievements.extend(daily_achievements)
            
            # Check for book completion achievements
            book_achievements = self._check_book_completion_achievements(user_id, book_id)
            new_achievements.extend(book_achievements)
            
            # Update stats with new achievements
            if new_achievements:
                stats.total_achievements += len(new_achievements)
                # Calculate XP from new achievements
                total_xp = sum(achievement.metadata.get('xp_reward', 0) for achievement in new_achievements if achievement.metadata)
                stats.xp += total_xp
                
                # Check for level up
                new_level = self._calculate_level(stats.xp)
                if new_level > stats.level:
                    stats.level = new_level
                    # Create level up achievement
                    level_achievement = self._create_achievement(
                        user_id, 'level_up', f'Level {new_level}', 
                        f'Reached level {new_level}!', {'level': new_level, 'xp_reward': 100}
                    )
                    if level_achievement:
                        new_achievements.append(level_achievement)
                        stats.total_achievements += 1
                        stats.xp += 100
            
            # Update books completed count
            stats.books_completed = self._get_completed_books_count(user_id)
            
            # Save updated stats
            self.update_user_stats(
                user_id,
                current_streak=stats.current_streak,
                longest_streak=stats.longest_streak,
                total_achievements=stats.total_achievements,
                level=stats.level,
                xp=stats.xp,
                books_completed=stats.books_completed,
                total_pages_read=stats.total_pages_read,
                last_reading_date=stats.last_reading_date,
                streak_start_date=stats.streak_start_date
            )
            
            return new_achievements
            
        except Exception as e:
            self.logger.error(f"Failed to update reading progress for user {user_id}: {e}")
            return []
    
    def _check_streak_achievements(self, user_id: int, current_streak: int) -> List[Achievement]:
        """Check for enhanced streak-based achievements with Bronze/Silver/Gold/Diamond levels."""
        achievements = []
        
        # Enhanced streak milestones with Bronze/Silver/Gold/Diamond levels
        streak_milestones = [1, 3, 7, 14, 21, 30, 50, 75, 100, 150, 200, 250, 300, 365]
        
        for milestone in streak_milestones:
            if current_streak == milestone:
                achievement_type = f"{milestone}_day_streak"
                if not self._has_achievement(user_id, achievement_type):
                    # Get achievement definition for proper title/description, else fallback
                    achievement_def = self._get_achievement_definition(achievement_type)
                    if achievement_def is not None:
                        title = achievement_def.title
                        description = achievement_def.description
                        xp_reward = achievement_def.xp_reward
                    else:
                        # Fallback values if definitions were not seeded
                        title = f"{milestone}-Day Streak"
                        description = f"Maintained a reading streak for {milestone} day(s)"
                        # Reasonable XP defaults aligned with tiers
                        xp_map = {1: 10, 3: 25, 7: 50, 14: 100, 21: 150, 30: 200,
                                  50: 400, 75: 600, 100: 1000, 150: 1500, 200: 2000,
                                  250: 2500, 300: 3000, 365: 5000}
                        xp_reward = xp_map.get(milestone, 50)
                    achievement = self._create_achievement(
                        user_id,
                        achievement_type,
                        title,
                        description,
                        {'streak': milestone, 'xp_reward': xp_reward, 'level': self._get_streak_level(milestone)}
                    )
                    if achievement:
                        achievements.append(achievement)
        
        return achievements
    
    def _get_achievement_definition(self, achievement_type: str) -> Optional['AchievementDefinition']:
        """Get achievement definition by type."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM achievement_definitions WHERE type = %s
                ''', (achievement_type,))
                
                result = cursor.fetchone()
                if result:
                    return AchievementDefinition.from_dict(dict(result))
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get achievement definition for {achievement_type}: {e}")
            return None
    
    def _get_streak_level(self, streak_days: int) -> str:
        """Get streak level (Bronze/Silver/Gold/Diamond) based on days."""
        if streak_days <= 30:
            return "Bronze"
        elif streak_days <= 100:
            return "Silver"
        elif streak_days <= 250:
            return "Gold"
        else:
            return "Diamond"
    
    def _check_page_achievements(self, user_id: int, total_pages: int) -> List[Achievement]:
        """Check for page-based achievements."""
        achievements = []
        # Expanded overall page milestones
        page_milestones = [100, 200, 300, 500, 750, 1000, 1500, 3000, 5000, 10000]
        
        for milestone in page_milestones:
            if total_pages >= milestone:
                achievement_type = f"{milestone}_pages"
                if not self._has_achievement(user_id, achievement_type):
                    # Prefer definition data if present
                    definition = self._get_achievement_definition(achievement_type)
                    title = definition.title if definition else '📄 Pages Milestone'
                    description = definition.description if definition else f'Read {milestone} pages'
                    xp_reward = definition.xp_reward if definition else max(50, milestone // 10)
                    achievement = self._create_achievement(
                        user_id,
                        achievement_type,
                        title,
                        description,
                        {'pages': milestone, 'xp_reward': xp_reward}
                    )
                    if achievement:
                        achievements.append(achievement)
        
        return achievements
    
    def _check_daily_achievements(self, user_id: int, pages_read: int) -> List[Achievement]:
        """Check for daily reading achievements."""
        achievements = []
        
        # Speed reader (50+ pages in a day)
        if pages_read >= 50:
            if not self._has_achievement(user_id, 'speed_reader'):
                achievement = self._create_achievement(
                    user_id, 'speed_reader', '⚡ Speed Reader',
                    'Read 50+ pages in a single day',
                    {'pages': pages_read, 'xp_reward': 100}
                )
                if achievement:
                    achievements.append(achievement)
        
        # Marathon reader (100+ pages in a day)
        if pages_read >= 100:
            if not self._has_achievement(user_id, 'marathon_reader'):
                achievement = self._create_achievement(
                    user_id, 'marathon_reader', '🏃 Marathon Reader',
                    'Read 100+ pages in a single day',
                    {'pages': pages_read, 'xp_reward': 200}
                )
                if achievement:
                    achievements.append(achievement)
        
        return achievements
    
    def _check_book_completion_achievements(self, user_id: int, book_id: int) -> List[Achievement]:
        """Check for book completion achievements."""
        achievements = []
        
        try:
            # Check if the book was just completed
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ub.pages_read, b.total_pages, ub.status
                    FROM user_books ub
                    JOIN books b ON b.book_id = ub.book_id
                    WHERE ub.user_id = %s AND ub.book_id = %s
                ''', (user_id, book_id))
                
                row = cursor.fetchone()
                if not row:
                    return achievements
                
                pages_read = row['pages_read']
                total_pages = row['total_pages']
                status = row['status']
                
                # Check if book is completed
                if status == 'completed' and pages_read >= total_pages:
                    # Get total completed books count
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM user_books 
                        WHERE user_id = %s AND status = 'completed'
                    ''', (user_id,))
                    
                    completed_count = cursor.fetchone()['count']
                    
                    # Check for first book achievement
                    if completed_count == 1 and not self._has_achievement(user_id, 'first_book'):
                        achievement = self._create_achievement(
                            user_id, 'first_book', '📚 First Book',
                            'Completed your first book! Welcome to the reading journey!',
                            {'book_id': book_id, 'xp_reward': 100}
                        )
                        if achievement:
                            achievements.append(achievement)
                    
                    # Check for book collector (5 books)
                    elif completed_count == 5 and not self._has_achievement(user_id, 'book_collector'):
                        achievement = self._create_achievement(
                            user_id, 'book_collector', '📚 Book Collector',
                            'Completed 5 books! You\'re building a great collection!',
                            {'book_id': book_id, 'completed_count': completed_count, 'xp_reward': 300}
                        )
                        if achievement:
                            achievements.append(achievement)
                    
                    # Check for book lover (10 books)
                    elif completed_count == 10 and not self._has_achievement(user_id, 'book_lover'):
                        achievement = self._create_achievement(
                            user_id, 'book_lover', '📚 Book Lover',
                            'Completed 10 books! You\'re truly passionate about reading!',
                            {'book_id': book_id, 'completed_count': completed_count, 'xp_reward': 600}
                        )
                        if achievement:
                            achievements.append(achievement)
                    
                    # Check for book enthusiast (25 books)
                    elif completed_count == 25 and not self._has_achievement(user_id, 'book_enthusiast'):
                        achievement = self._create_achievement(
                            user_id, 'book_enthusiast', '📚 Book Enthusiast',
                            'Completed 25 books! You\'re a true reading enthusiast!',
                            {'book_id': book_id, 'completed_count': completed_count, 'xp_reward': 1500}
                        )
                        if achievement:
                            achievements.append(achievement)
                    
                    # Check for book master (50 books)
                    elif completed_count == 50 and not self._has_achievement(user_id, 'book_master'):
                        achievement = self._create_achievement(
                            user_id, 'book_master', '📚 Book Master',
                            'Completed 50 books! You are a true book master!',
                            {'book_id': book_id, 'completed_count': completed_count, 'xp_reward': 3000}
                        )
                        if achievement:
                            achievements.append(achievement)
                            
        except Exception as e:
            self.logger.error(f"Failed to check book completion achievements for user {user_id}: {e}")
        
        return achievements
    
    def _get_completed_books_count(self, user_id: int) -> int:
        """Get the count of completed books for a user."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as count FROM user_books 
                    WHERE user_id = %s AND status = 'completed'
                ''', (user_id,))
                
                return cursor.fetchone()['count']
                
        except Exception as e:
            self.logger.error(f"Failed to get completed books count for user {user_id}: {e}")
            return 0
            
    def _get_daily_pages_read(self, user_id: int) -> int:
        """Get total pages read by user today across all books."""
        try:
            today = date.today()
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT SUM(pages_read) as sum FROM reading_sessions 
                    WHERE user_id = %s AND session_date = %s
                ''', (user_id, today))
                
                result = cursor.fetchone()
                return result['sum'] if result and result['sum'] else 0
                
        except Exception as e:
            self.logger.error(f"Failed to get daily pages read for user {user_id}: {e}")
            return 0
    
    def _has_achievement(self, user_id: int, achievement_type: str) -> bool:
        """Check if user already has a specific achievement."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as count FROM achievements 
                    WHERE user_id = %s AND type = %s
                ''', (user_id, achievement_type))
                
                return cursor.fetchone()['count'] > 0
                
        except Exception as e:
            self.logger.error(f"Failed to check achievement for user {user_id}: {e}")
            return False
    
    def _create_achievement(self, user_id: int, achievement_type: str, title: str, 
                          description: str, metadata: Dict[str, Any]) -> Optional[Achievement]:
        """Create a new achievement for a user."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get achievement definition for XP reward
                cursor.execute('''
                    SELECT xp_reward FROM achievement_definitions WHERE type = %s
                ''', (achievement_type,))
                
                definition = cursor.fetchone()
                if definition:
                    metadata['xp_reward'] = definition['xp_reward']
                
                cursor.execute('''
                    INSERT INTO achievements (user_id, type, title, description, metadata, earned_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (user_id, achievement_type, title, description, json.dumps(metadata), datetime.now()))
                
                conn.commit()
                
                return Achievement(
                    id=cursor.fetchone()['id'],
                    user_id=user_id,
                    type=achievement_type,
                    title=title,
                    description=description,
                    earned_at=datetime.now(),
                    metadata=metadata
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create achievement for user {user_id}: {e}")
            return None
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate user level based on XP."""
        # Simple level calculation: every 1000 XP = 1 level
        return max(1, (xp // 1000) + 1)
    
    def get_user_achievements(self, user_id: int, limit: int = 10) -> List[Achievement]:
        """Get user's recent achievements."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM achievements 
                    WHERE user_id = %s 
                    ORDER BY earned_at DESC 
                    LIMIT %s
                ''', (user_id, limit))
                
                achievements = []
                for row in cursor.fetchall():
                    achievements.append(Achievement.from_dict(dict(row)))
                
                return achievements
                
        except Exception as e:
            self.logger.error(f"Failed to get achievements for user {user_id}: {e}")
            return []
    
    def get_user_achievement_count(self, user_id: int) -> int:
        """Get total count of user's achievements."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as count FROM achievements 
                    WHERE user_id = %s
                ''', (user_id,))
                
                result = cursor.fetchone()
                return result['count'] if result else 0
                
        except Exception as e:
            self.logger.error(f"Failed to get achievement count for user {user_id}: {e}")
            return 0
    
    def get_achievement_definitions(self) -> List[AchievementDefinition]:
        """Get all achievement definitions."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM achievement_definitions 
                    WHERE is_active = 1 
                    ORDER BY xp_reward ASC
                ''')
                
                definitions = []
                for row in cursor.fetchall():
                    definitions.append(AchievementDefinition.from_dict(dict(row)))
                
                return definitions
                
        except Exception as e:
            self.logger.error(f"Failed to get achievement definitions: {e}")
            return []
    
    def get_league_user_stats(self, user_id: int, league_id: int) -> Optional[Dict[str, Any]]:
        """Get user's statistics within a specific league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get league's current book
                cursor.execute('''
                    SELECT current_book_id FROM leagues WHERE league_id = %s
                ''', (league_id,))
                
                league_result = cursor.fetchone()
                if not league_result:
                    return None
                
                current_book_id = league_result['current_book_id']
                if not current_book_id:
                    return None
                
                # Get user's progress on the league's current book
                cursor.execute('''
                    SELECT 
                        CASE WHEN ub.pages_read >= b.total_pages THEN 1 ELSE 0 END as books_completed,
                        COALESCE(ub.pages_read, 0) as pages_read
                    FROM books b
                    LEFT JOIN user_books ub ON ub.book_id = b.book_id AND ub.user_id = %s
                    WHERE b.book_id = %s
                ''', (user_id, current_book_id))
                
                book_result = cursor.fetchone()
                books_completed = book_result['books_completed'] if book_result else 0
                pages_read = book_result['pages_read'] if book_result else 0
                
                # Get league-specific achievements
                # Note: Postgres LIKE ||
                cursor.execute('''
                    SELECT COUNT(*) as achievements
                    FROM achievements 
                    WHERE user_id = %s 
                    AND (metadata LIKE '%%"league_id":' || %s || '%%' OR type IN ('community_contributor', 'league_champion'))
                ''', (user_id, league_id))
                
                achievements_result = cursor.fetchone()
                achievements = achievements_result['achievements'] if achievements_result else 0
                
                # Get user's position in league (based on pages read on current book)
                cursor.execute('''
                    SELECT COUNT(*) + 1 as position
                    FROM (
                        SELECT ub.user_id, COALESCE(ub.pages_read, 0) as total_pages
                        FROM user_books ub
                        WHERE ub.book_id = %s
                        GROUP BY ub.user_id
                        HAVING total_pages > %s
                    ) as subquery
                ''', (current_book_id, pages_read))
                
                position_result = cursor.fetchone()
                position = position_result['position'] if position_result else 1
                
                return {
                    'books_completed': books_completed,
                    'pages_read': pages_read,
                    'achievements': achievements,
                    'position': position
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get league user stats for user {user_id}, league {league_id}: {e}")
            return None
    
    def get_league_achievements(self, user_id: int, league_id: int, limit: int = 10) -> List[Achievement]:
        """Get user's achievements within a specific league."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM achievements 
                    WHERE user_id = %s 
                    AND (metadata LIKE '%%"league_id":' || %s || '%%' OR type IN ('community_contributor', 'league_champion'))
                    ORDER BY earned_at DESC 
                    LIMIT %s
                ''', (user_id, league_id, limit))
                
                achievements = []
                for row in cursor.fetchall():
                    achievements.append(Achievement.from_dict(dict(row)))
                
                return achievements
                
        except Exception as e:
            self.logger.error(f"Failed to get league achievements for user {user_id}, league {league_id}: {e}")
            return []
    
    def get_league_name(self, league_id: int) -> str:
        """Get league name by ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM leagues WHERE league_id = %s', (league_id,))
                
                result = cursor.fetchone()
                return result['name'] if result else "Unknown League"
                
        except Exception as e:
            self.logger.error(f"Failed to get league name for league {league_id}: {e}")
            return "Unknown League"
    
    def check_league_achievements(self, user_id: int, league_id: int, pages_read: int) -> List[Achievement]:
        """Check for league-specific achievements."""
        achievements = []
        
        # League participation achievement
        if not self._has_achievement(user_id, 'community_contributor'):
            achievement = self._create_achievement(
                user_id, 'community_contributor', '🌟 Community Star',
                'Participate in a reading league',
                {'league_id': league_id, 'xp_reward': 100}
            )
            if achievement:
                achievements.append(achievement)
        
        # League-specific page milestones
        league_stats = self.get_league_user_stats(user_id, league_id)
        if league_stats:
            league_pages = league_stats.get('pages_read', 0)
            
            # Expanded league page milestones
            league_milestones = [100, 300, 500, 750, 1000, 2000, 3000, 5000]
            for milestone in league_milestones:
                if league_pages >= milestone:
                    achievement_type = f"league_{milestone}_pages"
                    if not self._has_achievement(user_id, achievement_type):
                        definition = self._get_achievement_definition(achievement_type)
                        title = definition.title if definition else f'🏆 League {milestone} Pages'
                        description = definition.description if definition else f'Read {milestone} pages in this league'
                        xp_reward = definition.xp_reward if definition else max(20, milestone // 5)
                        achievement = self._create_achievement(
                            user_id,
                            achievement_type,
                            title,
                            description,
                            {'league_id': league_id, 'pages': milestone, 'xp_reward': xp_reward}
                        )
                        if achievement:
                            achievements.append(achievement)
        
        return achievements

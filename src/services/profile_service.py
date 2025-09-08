"""
Profile service for managing user profiles and comprehensive statistics.

This service handles user profile information, preferences, and detailed reading analytics.
Now uses the unified users table instead of separate user_profiles table.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from collections import defaultdict

from src.database.database import DatabaseManager
from src.database.models.profile import UserProfile, ProfileStatistics
from src.services.achievement_service import AchievementService


class ProfileService:
    """Service for managing user profiles and comprehensive statistics."""
    
    def __init__(self, db_manager: DatabaseManager, achievement_service: AchievementService):
        self.db_manager = db_manager
        self.achievement_service = achievement_service
        self.logger = logging.getLogger(__name__)
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile information from users table."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, full_name, nickname, bio, reading_goal_pages_per_day,
                           preferred_reading_time, favorite_genres, reading_level, privacy_level,
                           show_achievements, show_reading_stats, registration_date
                    FROM users WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    # Convert row to dictionary
                    columns = [desc[0] for desc in cursor.description]
                    data = dict(zip(columns, row))
                    
                    # Handle None values and defaults - simplified fields
                    data['display_name'] = data.get('full_name', '')  # Use full_name as display_name
                    data['nickname'] = data.get('nickname', '')  # Keep nickname as is
                    data['reading_goal_pages_per_day'] = data['reading_goal_pages_per_day'] or 20
                    data['privacy_level'] = data['privacy_level'] or 'public'
                    data['show_achievements'] = bool(data['show_achievements'])
                    data['show_reading_stats'] = bool(data['show_reading_stats'])
                    
                    # Use registration_date for both created_at and updated_at
                    data['created_at'] = data.get('registration_date')
                    data['updated_at'] = data.get('registration_date')
                    
                    profile = UserProfile.from_dict(data)
                    return profile
                else:
                    # Create default profile
                    return self._create_default_profile(user_id)
        except Exception as e:
            self.logger.error(f"Failed to get user profile for {user_id}: {e}")
            return None
    
    def update_user_profile(self, profile: UserProfile) -> bool:
        """Update user profile in users table."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET
                        full_name = ?, nickname = ?, bio = ?, reading_goal_pages_per_day = ?,
                        preferred_reading_time = ?, favorite_genres = ?, reading_level = ?,
                        privacy_level = ?, show_achievements = ?, show_reading_stats = ?,
                        last_activity = ?
                    WHERE user_id = ?
                ''', (
                    profile.display_name, profile.nickname, profile.bio, 
                    profile.reading_goal_pages_per_day, profile.preferred_reading_time,
                    profile.favorite_genres, profile.reading_level, profile.privacy_level,
                    profile.show_achievements, profile.show_reading_stats,
                    datetime.now(), profile.user_id
                ))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to update user profile for {profile.user_id}: {e}")
            return False
    
    def update_profile_field(self, user_id: int, field: str, value: Any) -> bool:
        """Update a specific profile field."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Map field names to database columns (simplified)
                field_mapping = {
                    'display_name': 'full_name',  # display_name maps to full_name
                    'nickname': 'nickname', 
                    'bio': 'bio',
                    'daily_goal': 'reading_goal_pages_per_day',
                    'reading_time': 'preferred_reading_time',
                    'favorite_genres': 'favorite_genres',
                    'reading_level': 'reading_level',
                    'privacy_level': 'privacy_level',
                    'show_achievements': 'show_achievements',
                    'show_reading_stats': 'show_reading_stats'
                }
                
                if field not in field_mapping:
                    self.logger.error(f"Unknown profile field: {field}")
                    return False
                
                db_field = field_mapping[field]
                cursor.execute(f'''
                    UPDATE users SET {db_field} = ?, last_activity = ?
                    WHERE user_id = ?
                ''', (value, datetime.now(), user_id))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Failed to update profile field {field} for user {user_id}: {e}")
            return False
    
    def get_comprehensive_statistics(self, user_id: int) -> Optional[ProfileStatistics]:
        """Get comprehensive reading statistics for a user."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic user stats
                cursor.execute('''
                    SELECT current_streak, longest_streak, total_achievements, level, xp,
                           books_completed, total_pages_read, last_reading_date, streak_start_date
                    FROM user_stats WHERE user_id = ?
                ''', (user_id,))
                
                stats_row = cursor.fetchone()
                if not stats_row:
                    return None
                
                current_streak, longest_streak, total_achievements, level, xp, books_completed, total_pages_read, last_reading_date, streak_start_date = stats_row
                
                # Get user join date
                cursor.execute('SELECT registration_date FROM users WHERE user_id = ?', (user_id,))
                join_row = cursor.fetchone()
                join_date = datetime.fromisoformat(join_row[0]) if join_row and join_row[0] else datetime.now()
                
                # Calculate days since join
                days_since_join = max(1, (datetime.now() - join_date).days)
                
                # Get reading sessions for detailed analytics
                cursor.execute('''
                    SELECT session_date, pages_read, reading_time_minutes
                    FROM reading_sessions 
                    WHERE user_id = ? AND session_date IS NOT NULL
                    ORDER BY session_date
                ''', (user_id,))
                
                sessions = cursor.fetchall()
                
                # Calculate detailed statistics
                total_reading_days = len(sessions)
                average_pages_per_day = total_pages_read / days_since_join if days_since_join > 0 else 0
                average_pages_per_book = total_pages_read / books_completed if books_completed > 0 else 0
                
                # Calculate reading speed (pages per hour)
                total_reading_time = sum(session[2] for session in sessions if session[2])
                reading_speed_pages_per_hour = (total_pages_read / (total_reading_time / 60)) if total_reading_time > 0 else 0
                
                # Find favorite reading day and time
                day_counts = defaultdict(int)
                time_counts = defaultdict(int)
                
                for session in sessions:
                    if session[0]:  # session_date
                        try:
                            session_date = datetime.fromisoformat(session[0]).date()
                            day_name = session_date.strftime('%A')
                            day_counts[day_name] += 1
                        except (ValueError, TypeError):
                            pass
                
                favorite_reading_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else "Monday"
                favorite_reading_time = "Evening"  # Default, could be calculated from actual data
                
                # Find most productive month
                month_counts = defaultdict(int)
                for session in sessions:
                    if session[0]:
                        try:
                            session_date = datetime.fromisoformat(session[0])
                            month_name = session_date.strftime('%B')
                            month_counts[month_name] += session[1] if session[1] else 0
                        except (ValueError, TypeError):
                            pass
                
                most_productive_month = max(month_counts.items(), key=lambda x: x[1])[0] if month_counts else "January"
                
                # Calculate consistency score
                if days_since_join > 0:
                    consistency_score = min(100, (total_reading_days / days_since_join) * 100)
                else:
                    consistency_score = 0
                
                # Parse dates
                last_reading_date_parsed = None
                if last_reading_date:
                    try:
                        last_reading_date_parsed = datetime.fromisoformat(last_reading_date).date()
                    except (ValueError, TypeError):
                        pass
                
                streak_start_date_parsed = None
                if streak_start_date:
                    try:
                        streak_start_date_parsed = datetime.fromisoformat(streak_start_date).date()
                    except (ValueError, TypeError):
                        pass
                
                return ProfileStatistics(
                    user_id=user_id,
                    total_books_read=books_completed,
                    total_pages_read=total_pages_read,
                    current_streak=current_streak,
                    longest_streak=longest_streak,
                    total_reading_days=total_reading_days,
                    average_pages_per_day=average_pages_per_day,
                    average_pages_per_book=average_pages_per_book,
                    reading_speed_pages_per_hour=reading_speed_pages_per_hour,
                    favorite_reading_day=favorite_reading_day,
                    favorite_reading_time=favorite_reading_time,
                    most_productive_month=most_productive_month,
                    reading_consistency_score=consistency_score,
                    level=level,
                    xp=xp,
                    total_achievements=total_achievements,
                    join_date=join_date.date(),
                    last_reading_date=last_reading_date_parsed,
                    streak_start_date=streak_start_date_parsed
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive statistics for user {user_id}: {e}")
            return None
    
    def get_reading_insights(self, user_id: int) -> List[str]:
        """Get personalized reading insights for a user."""
        try:
            stats = self.get_comprehensive_statistics(user_id)
            if not stats:
                return []
            
            insights = []
            
            # Streak insights
            if stats.current_streak >= 7:
                insights.append(f"🔥 Amazing! You've been reading for {stats.current_streak} days straight!")
            elif stats.current_streak >= 3:
                insights.append(f"📚 Great momentum! {stats.current_streak} days in a row!")
            
            # Reading speed insights
            if stats.reading_speed_pages_per_hour > 50:
                insights.append("⚡ You're a speed reader! Over 50 pages per hour!")
            elif stats.reading_speed_pages_per_hour > 30:
                insights.append("📖 Good reading pace! You're making steady progress.")
            
            # Consistency insights
            if stats.reading_consistency_score > 80:
                insights.append("🎯 Excellent reading consistency! You're building a great habit.")
            elif stats.reading_consistency_score > 50:
                insights.append("📈 Good reading consistency! Keep it up!")
            
            # Achievement insights
            if stats.total_achievements > 10:
                insights.append(f"🏆 Achievement master! You've earned {stats.total_achievements} achievements!")
            elif stats.total_achievements > 5:
                insights.append(f"⭐ Great progress! {stats.total_achievements} achievements unlocked!")
            
            # Genre insights (if available)
            if stats.favorite_reading_day:
                insights.append(f"📅 You're most active on {stats.favorite_reading_day}s!")
            
            return insights[:5]  # Return top 5 insights
            
        except Exception as e:
            self.logger.error(f"Failed to get reading insights for user {user_id}: {e}")
            return []
    
    def _create_default_profile(self, user_id: int) -> UserProfile:
        """Create a default profile for a new user."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic user info from users table
                cursor.execute('SELECT full_name, nickname, daily_goal FROM users WHERE user_id = ?', (user_id,))
                user_row = cursor.fetchone()
                
                if user_row:
                    full_name, nickname, daily_goal = user_row
                    
                    # Create profile with data from users table
                    profile = UserProfile(
                        user_id=user_id,
                        display_name=full_name or "Reader",
                        nickname=nickname or "",
                        bio="",
                        reading_goal_pages_per_day=daily_goal or 20,
                        preferred_reading_time=None,
                        favorite_genres=None,
                        reading_level=self._auto_assign_reading_level(user_id),
                        privacy_level="public",
                        show_achievements=True,
                        show_reading_stats=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    # Save the profile to users table (simplified fields)
                    cursor.execute('''
                        UPDATE users SET
                            full_name = ?, nickname = ?, bio = ?, reading_goal_pages_per_day = ?,
                            preferred_reading_time = ?, favorite_genres = ?, reading_level = ?,
                            privacy_level = ?, show_achievements = ?, show_reading_stats = ?,
                            last_activity = ?
                        WHERE user_id = ?
                    ''', (
                        profile.display_name, profile.nickname, profile.bio,
                        profile.reading_goal_pages_per_day, profile.preferred_reading_time,
                        profile.favorite_genres, profile.reading_level, profile.privacy_level,
                        profile.show_achievements, profile.show_reading_stats,
                        datetime.now(), user_id
                    ))
                    conn.commit()
                    
                    return profile
                else:
                    # Fallback if user doesn't exist in users table
                    return UserProfile(
                        user_id=user_id,
                        display_name="Reader",
                        nickname="",
                        bio="",
                        reading_goal_pages_per_day=20,
                        reading_level="Beginner",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to create default profile for user {user_id}: {e}")
            return UserProfile(
                user_id=user_id,
                display_name="Reader",
                nickname="",
                bio="",
                reading_goal_pages_per_day=20,
                reading_level="Beginner",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
    
    def _auto_assign_reading_level(self, user_id: int) -> str:
        """Auto-assign reading level based on user's reading history."""
        try:
            # Get user stats
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                return "Beginner"
            
            # Get additional metrics
            books_completed = stats.books_completed
            total_pages = stats.total_pages_read
            achievements = self.achievement_service.get_user_achievement_count(user_id)
            streak = stats.current_streak
            
            # Calculate consistency (simplified)
            consistency = min(100, (streak * 10)) if streak > 0 else 0
            
            # Assign level based on multiple factors
            if books_completed >= 50 or total_pages >= 10000 or achievements >= 20:
                return "Master"
            elif books_completed >= 25 or total_pages >= 5000 or achievements >= 15:
                return "Advanced"
            elif books_completed >= 10 or total_pages >= 2000 or achievements >= 10:
                return "Intermediate"
            elif books_completed >= 3 or total_pages >= 500 or achievements >= 5:
                return "Novice"
            else:
                return "Beginner"
                
        except Exception as e:
            self.logger.error(f"Failed to auto-assign reading level for user {user_id}: {e}")
            return "Beginner"
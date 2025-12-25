"""
Visual Service for gamification system.

This service handles progress bars, achievement badges, and shareable certificates.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from src.database.database import db_manager
from src.database.models.motivation import VisualElement, VisualElementType
from src.services.achievement_service import AchievementService


class VisualService:
    """Service for creating visual elements and progress displays."""
    
    def __init__(self):
        """Initialize the visual service."""
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.achievement_service = AchievementService()
    
    def create_progress_bar(self, current: int, total: int, width: int = 10, 
                          show_percentage: bool = True) -> str:
        """Create a visual progress bar."""
        try:
            if total <= 0:
                return "▱" * width + " 0%"
            
            percentage = min(100, (current / total) * 100)
            filled_bars = int((percentage / 100) * width)
            empty_bars = width - filled_bars
            
            progress_bar = "▰" * filled_bars + "▱" * empty_bars
            
            if show_percentage:
                return f"{progress_bar} {percentage:.0f}%"
            else:
                return progress_bar
                
        except Exception as e:
            self.logger.error(f"Failed to create progress bar: {e}")
            return "▱" * width + " Error"
    
    def create_streak_display(self, current_streak: int, longest_streak: int) -> str:
        """Create a visual streak display."""
        try:
            if current_streak == 0:
                return "🔥 No active streak"
            
            # Create fire emojis based on streak length
            if current_streak < 7:
                fire_emoji = "🔥"
            elif current_streak < 30:
                fire_emoji = "🔥🔥"
            else:
                fire_emoji = "🔥🔥🔥"
            
            display = f"{fire_emoji} {current_streak} day streak"
            if longest_streak > current_streak:
                display += f" (Best: {longest_streak})"
            
            return display
            
        except Exception as e:
            self.logger.error(f"Failed to create streak display: {e}")
            return "🔥 Streak error"
    
    def create_level_display(self, level: int, xp: int, next_level_xp: int = None) -> str:
        """Create a visual level display."""
        try:
            if next_level_xp is None:
                next_level_xp = level * 1000
            
            current_level_xp = (level - 1) * 1000
            progress_xp = xp - current_level_xp
            needed_xp = next_level_xp - current_level_xp
            
            progress_bar = self.create_progress_bar(progress_xp, needed_xp, 8, False)
            
            return f"⭐ Level {level} {progress_bar} ({xp} XP)"
            
        except Exception as e:
            self.logger.error(f"Failed to create level display: {e}")
            return f"⭐ Level {level}"
    
    def create_achievement_badge(self, achievement: 'Achievement') -> str:
        """Create a visual achievement badge."""
        try:
            # Get achievement definition for icon
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT icon FROM achievement_definitions WHERE type = %s
                ''', (achievement.type,))
                
                result = cursor.fetchone()
                icon = result['icon'] if result else "🏆"
            
            badge = f"{icon} {achievement.title}"
            if achievement.metadata and 'xp_reward' in achievement.metadata:
                badge += f" (+{achievement.metadata['xp_reward']} XP)"
            
            return badge
            
        except Exception as e:
            self.logger.error(f"Failed to create achievement badge: {e}")
            return f"🏆 {achievement.title}"
    
    def create_reading_stats_display(self, user_id: int) -> str:
        """Create a comprehensive reading stats display."""
        try:
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                return "📊 No stats available"
            
            display = "📊 Your Reading Stats:\n\n"
            
            # Streak display
            display += f"{self.create_streak_display(stats.current_streak, stats.longest_streak)}\n"
            
            # Level display
            next_level_xp = stats.level * 1000
            display += f"{self.create_level_display(stats.level, stats.xp, next_level_xp)}\n"
            
            # Books and pages
            display += f"📚 Books Completed: {stats.books_completed}\n"
            display += f"📄 Total Pages: {stats.total_pages_read:,}\n"
            display += f"🏆 Achievements: {stats.total_achievements}\n"
            
            return display
            
        except Exception as e:
            self.logger.error(f"Failed to create reading stats display for user {user_id}: {e}")
            return "📊 Stats unavailable"
    
    def create_book_progress_display(self, current_pages: int, total_pages: int, 
                                   book_title: str = None) -> str:
        """Create a book progress display."""
        try:
            if total_pages <= 0:
                return "📖 No progress data"
            
            progress_bar = self.create_progress_bar(current_pages, total_pages, 12)
            percentage = (current_pages / total_pages) * 100
            remaining = total_pages - current_pages
            
            display = f"📖 {book_title or 'Current Book'}\n"
            display += f"{progress_bar}\n"
            display += f"📄 {current_pages:,}/{total_pages:,} pages ({percentage:.1f}%)\n"
            display += f"📚 {remaining:,} pages remaining"
            
            return display
            
        except Exception as e:
            self.logger.error(f"Failed to create book progress display: {e}")
            return "📖 Progress unavailable"
    
    def create_achievement_celebration_display(self, achievement: 'Achievement') -> str:
        """Create a celebration display for new achievements."""
        try:
            # Get achievement definition for icon
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT icon FROM achievement_definitions WHERE type = %s
                ''', (achievement.type,))
                
                result = cursor.fetchone()
                icon = result['icon'] if result else "🏆"
            
            display = f"🎉 ACHIEVEMENT UNLOCKED! 🎉\n\n"
            display += f"{icon} {achievement.title}\n"
            display += f"📝 {achievement.description}\n"
            
            if achievement.metadata and 'xp_reward' in achievement.metadata:
                display += f"\n✨ +{achievement.metadata['xp_reward']} XP earned!"
            
            display += f"\n🎊 Congratulations on your progress!"
            
            return display
            
        except Exception as e:
            self.logger.error(f"Failed to create achievement celebration display: {e}")
            return f"🎉 Achievement: {achievement.title}"
    
    def create_league_leaderboard_display(self, leaderboard_data: List[Dict[str, Any]], 
                                        user_position: int = None) -> str:
        """Create a visual league leaderboard display."""
        try:
            if not leaderboard_data:
                return "🏆 No leaderboard data available"
            
            display = "🏆 League Leaderboard:\n\n"
            
            # Medal emojis for top positions
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            
            for i, entry in enumerate(leaderboard_data[:10], 1):
                position = entry.get('position', i)
                username = entry.get('full_name') or f"User {entry.get('user_id', '')}"
                pages = entry.get('pages_read', 0)
                
                if position in medals:
                    display += f"{medals[position]} {position}. {username}: {pages:,} pages\n"
                else:
                    display += f"{position:2d}. {username}: {pages:,} pages\n"
                
                # Highlight user's position
                if user_position and position == user_position:
                    display = display.rstrip('\n') + " 👈 You!\n"
            
            return display
            
        except Exception as e:
            self.logger.error(f"Failed to create league leaderboard display: {e}")
            return "🏆 Leaderboard unavailable"
    
    def create_weekly_progress_summary(self, user_id: int) -> str:
        """Create a weekly progress summary display."""
        try:
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                return "📊 No weekly data available"
            
            # Get recent achievements
            recent_achievements = self.achievement_service.get_user_achievements(user_id, 3)
            
            display = "📊 Weekly Progress Summary:\n\n"
            
            # Main stats
            display += f"🔥 Current Streak: {stats.current_streak} days\n"
            display += f"📚 Total Pages: {stats.total_pages_read:,}\n"
            display += f"⭐ Level: {stats.level} ({stats.xp:,} XP)\n"
            display += f"🏆 Total Achievements: {stats.total_achievements}\n"
            
            # Recent achievements
            if recent_achievements:
                display += f"\n🎉 Recent Achievements:\n"
                for achievement in recent_achievements:
                    display += f"• {self.create_achievement_badge(achievement)}\n"
            
            # Progress bar for current level
            current_level_xp = (stats.level - 1) * 1000
            next_level_xp = stats.level * 1000
            level_progress = stats.xp - current_level_xp
            level_needed = next_level_xp - current_level_xp
            
            if level_needed > 0:
                level_bar = self.create_progress_bar(level_progress, level_needed, 8)
                display += f"\n⭐ Level Progress: {level_bar}"
            
            return display
            
        except Exception as e:
            self.logger.error(f"Failed to create weekly progress summary for user {user_id}: {e}")
            return "📊 Weekly summary unavailable"
    
    def save_visual_element(self, user_id: int, element_type: str, data: str, 
                          expires_at: datetime = None) -> bool:
        """Save a visual element to the database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO visual_elements (user_id, element_type, data, created_at, expires_at)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, element_type, data, datetime.now(), expires_at))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save visual element for user {user_id}: {e}")
            return False
    
    def get_user_visual_elements(self, user_id: int, element_type: str = None, 
                               limit: int = 10) -> List[VisualElement]:
        """Get user's visual elements."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM visual_elements 
                    WHERE user_id = %s AND is_active = TRUE
                '''
                params = [user_id]
                
                if element_type:
                    query += ' AND element_type = %s'
                    params.append(element_type)
                
                query += ' ORDER BY created_at DESC LIMIT %s'
                params.append(limit)
                
                cursor.execute(query, params)
                
                elements = []
                for row in cursor.fetchall():
                    elements.append(VisualElement.from_dict(dict(row)))
                
                return elements
                
        except Exception as e:
            self.logger.error(f"Failed to get visual elements for user {user_id}: {e}")
            return []

"""
Motivation Service for gamification system.

This service handles personalized messages, progress celebrations, and social encouragement.
"""

import logging
import random
import json
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any

from src.database.database import db_manager
from src.database.models.motivation import MotivationMessage, MessageType
from src.services.achievement_service import AchievementService


class MotivationService:
    """Service for managing motivation messages and celebrations."""
    
    def __init__(self):
        """Initialize the motivation service."""
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.achievement_service = AchievementService()
    
    def send_achievement_celebration(self, user_id: int, achievement: 'Achievement') -> Optional[str]:
        """Send enhanced celebration message for a new achievement."""
        try:
            # Get achievement level for enhanced messaging
            achievement_level = achievement.metadata.get('level', 'Bronze') if achievement.metadata else 'Bronze'
            
            # Enhanced celebration messages based on achievement level
            if achievement_level == "Bronze":
                celebration_messages = [
                    f"🥉 Bronze Achievement! You earned: {achievement.title}",
                    f"🌟 Great start! You unlocked: {achievement.title}",
                    f"💪 Building momentum! You achieved: {achievement.title}",
                    f"🎯 On the right track! You earned: {achievement.title}",
                    f"⭐ First steps! You unlocked: {achievement.title}"
                ]
            elif achievement_level == "Silver":
                celebration_messages = [
                    f"🥈 Silver Achievement! You earned: {achievement.title}",
                    f"🌟 Impressive progress! You unlocked: {achievement.title}",
                    f"💎 Shining bright! You achieved: {achievement.title}",
                    f"🎊 Excellent work! You earned: {achievement.title}",
                    f"⭐ Rising star! You unlocked: {achievement.title}"
                ]
            elif achievement_level == "Gold":
                celebration_messages = [
                    f"🥇 Gold Achievement! You earned: {achievement.title}",
                    f"🏆 Outstanding! You unlocked: {achievement.title}",
                    f"💎 Golden performance! You achieved: {achievement.title}",
                    f"🎉 Exceptional! You earned: {achievement.title}",
                    f"⭐ Elite level! You unlocked: {achievement.title}"
                ]
            elif achievement_level == "Diamond":
                celebration_messages = [
                    f"💎 Diamond Achievement! You earned: {achievement.title}",
                    f"👑 Legendary! You unlocked: {achievement.title}",
                    f"💎 Master level! You achieved: {achievement.title}",
                    f"🎊 Phenomenal! You earned: {achievement.title}",
                    f"⭐ Ultimate achievement! You unlocked: {achievement.title}"
                ]
            else:
                celebration_messages = [
                    f"🎉 Congratulations! You earned: {achievement.title}",
                    f"🏆 Amazing work! You just unlocked: {achievement.title}",
                    f"⭐ Fantastic! You achieved: {achievement.title}",
                    f"🎊 Well done! You earned: {achievement.title}",
                    f"🌟 Incredible! You unlocked: {achievement.title}"
                ]
            
            message_content = random.choice(celebration_messages)
            
            # Add XP reward information
            if achievement.metadata and 'xp_reward' in achievement.metadata:
                xp_reward = achievement.metadata['xp_reward']
                message_content += f"\n\n✨ +{xp_reward} XP earned!"
                
                # Add level progression hint
                if xp_reward >= 500:
                    message_content += f"\n🚀 That's a major XP boost! You're leveling up fast!"
                elif xp_reward >= 200:
                    message_content += f"\n📈 Great XP gain! Keep up the excellent work!"
            
            # Add streak information for streak achievements
            if 'streak' in achievement.type:
                streak_days = achievement.metadata.get('streak', 0) if achievement.metadata else 0
                if streak_days >= 100:
                    message_content += f"\n🔥 {streak_days} days of dedication! You're unstoppable!"
                elif streak_days >= 30:
                    message_content += f"\n💪 {streak_days} days strong! Amazing consistency!"
                elif streak_days >= 7:
                    message_content += f"\n🌟 {streak_days} days in a row! Building great habits!"
            
            # Store the message in database
            self._create_motivation_message(
                user_id, MessageType.ACHIEVEMENT_EARNED, message_content,
                {'achievement_id': achievement.id, 'achievement_type': achievement.type, 'level': achievement_level}
            )
            
            return message_content
            
        except Exception as e:
            self.logger.error(f"Failed to send achievement celebration for user {user_id}: {e}")
            return None
    
    def send_daily_motivation(self, user_id: int) -> Optional[str]:
        """Send daily motivation message."""
        try:
            # Get user stats for personalized message
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                return False
            
            # Generate personalized message based on user's progress
            if stats.current_streak > 0:
                if stats.current_streak == 1:
                    message = "🌅 Good morning! Ready to start your reading journey today?"
                elif stats.current_streak < 7:
                    message = f"🔥 Day {stats.current_streak} of your streak! Keep the momentum going!"
                elif stats.current_streak < 30:
                    message = f"🌟 Amazing! {stats.current_streak} days strong! You're building an incredible habit!"
                else:
                    message = f"🏆 {stats.current_streak} days! You're a reading legend! What will you conquer today?"
            else:
                motivational_quotes = [
                    "📚 Every page you read is a step toward your goals!",
                    "🌟 Today is a perfect day to start reading!",
                    "💫 Your next great adventure awaits in the pages of a book!",
                    "🚀 Ready to explore new worlds through reading?",
                    "✨ Every book is a new opportunity to grow!"
                ]
                message = random.choice(motivational_quotes)
            
            # Store the message in database
            self._create_motivation_message(
                user_id, MessageType.DAILY_MOTIVATION, message,
                {'streak': stats.current_streak, 'level': stats.level}
            )
            
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to send daily motivation for user {user_id}: {e}")
            return None
    
    def send_progress_celebration(self, user_id: int, pages_read: int, book_title: str = None) -> Optional[str]:
        """Send celebration for reading progress."""
        try:
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                return False
            
            # Generate celebration message based on pages read
            if pages_read >= 100:
                message = f"🏃 Marathon reading session! {pages_read} pages in one day! You're unstoppable!"
            elif pages_read >= 50:
                message = f"⚡ Speed reading mode! {pages_read} pages today! Amazing pace!"
            elif pages_read >= 20:
                message = f"📖 Great progress! {pages_read} pages read today! Keep it up!"
            else:
                message = f"📚 Nice reading! {pages_read} pages today! Every page counts!"
            
            if book_title:
                message += f"\n\n📖 Currently reading: {book_title}"
            
            # Store the message in database
            self._create_motivation_message(
                user_id, MessageType.DAILY_GOAL_REACHED, message,
                {'pages_read': pages_read, 'book_title': book_title}
            )
            
            return message
            
        except Exception as e:
            self.logger.error(f"Failed to send progress celebration for user {user_id}: {e}")
            return None
    
    def send_streak_reminder(self, user_id: int) -> bool:
        """Send reminder to maintain reading streak."""
        try:
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats or stats.current_streak == 0:
                return False
            
            reminder_messages = [
                f"🔥 Don't break your {stats.current_streak}-day streak! Read a few pages today!",
                f"🌟 Your {stats.current_streak}-day reading streak is impressive! Keep it going!",
                f"💪 {stats.current_streak} days strong! Just a few pages to maintain your streak!",
                f"🏆 Amazing {stats.current_streak}-day streak! Don't let it slip away!"
            ]
            
            message = random.choice(reminder_messages)
            
            return self._create_motivation_message(
                user_id, MessageType.STREAK_REMINDER, message,
                {'streak': stats.current_streak}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send streak reminder for user {user_id}: {e}")
            return False
    
    def send_comeback_message(self, user_id: int, days_away: int) -> bool:
        """Send welcome back message for returning users."""
        try:
            comeback_messages = [
                f"👋 Welcome back! We missed you! Ready to continue your reading journey?",
                f"🌟 Great to see you again! Your books are waiting for you!",
                f"📚 You're back! Let's pick up where you left off!",
                f"🎉 Welcome back, reader! Time to dive into some great stories!"
            ]
            
            message = random.choice(comeback_messages)
            if days_away > 7:
                message += f"\n\n💪 It's been {days_away} days - let's start a new streak!"
            
            return self._create_motivation_message(
                user_id, MessageType.COMEBACK_MESSAGE, message,
                {'days_away': days_away}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send comeback message for user {user_id}: {e}")
            return False
    
    def send_weekly_progress_summary(self, user_id: int) -> bool:
        """Send weekly progress summary."""
        try:
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                return False
            
            # Get recent achievements
            recent_achievements = self.achievement_service.get_user_achievements(user_id, 5)
            
            message = f"📊 Weekly Summary:\n"
            message += f"🔥 Current Streak: {stats.current_streak} days\n"
            message += f"📚 Total Pages: {stats.total_pages_read}\n"
            message += f"🏆 Level: {stats.level} ({stats.xp} XP)\n"
            
            if recent_achievements:
                message += f"\n🎉 Recent Achievements:\n"
                for achievement in recent_achievements[:3]:
                    message += f"• {achievement.title}\n"
            
            message += f"\n💪 Keep up the amazing work!"
            
            return self._create_motivation_message(
                user_id, MessageType.WEEKLY_PROGRESS, message,
                {'streak': stats.current_streak, 'pages': stats.total_pages_read, 'level': stats.level}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send weekly summary for user {user_id}: {e}")
            return False
    
    def send_league_encouragement(self, user_id: int, league_name: str, position: int, total_members: int) -> bool:
        """Send encouragement message for league participation."""
        try:
            if position == 1:
                message = f"🏆 You're leading the {league_name} league! Amazing work!"
            elif position <= 3:
                message = f"🥇 Top 3 in {league_name}! You're on fire!"
            elif position <= total_members // 2:
                message = f"💪 Great progress in {league_name}! Keep pushing forward!"
            else:
                message = f"🚀 Every page counts in {league_name}! You've got this!"
            
            return self._create_motivation_message(
                user_id, MessageType.LEAGUE_UPDATE, message,
                {'league_name': league_name, 'position': position, 'total_members': total_members}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send league encouragement for user {user_id}: {e}")
            return False
    
    def _create_motivation_message(self, user_id: int, message_type: str, content: str, 
                                 metadata: Dict[str, Any] = None) -> bool:
        """Create a motivation message in the database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO motivation_messages (user_id, message_type, content, metadata, sent_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, message_type, content, 
                      json.dumps(metadata) if metadata else None, datetime.now()))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create motivation message for user {user_id}: {e}")
            return False
    
    def get_user_messages(self, user_id: int, limit: int = 10, unread_only: bool = False) -> List[MotivationMessage]:
        """Get user's motivation messages."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM motivation_messages 
                    WHERE user_id = ?
                '''
                params = [user_id]
                
                if unread_only:
                    query += ' AND is_read = 0'
                
                query += ' ORDER BY sent_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                
                messages = []
                for row in cursor.fetchall():
                    messages.append(MotivationMessage.from_dict(dict(row)))
                
                return messages
                
        except Exception as e:
            self.logger.error(f"Failed to get messages for user {user_id}: {e}")
            return []
    
    def mark_message_as_read(self, message_id: int) -> bool:
        """Mark a motivation message as read."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE motivation_messages SET is_read = 1 WHERE id = ?
                ''', (message_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to mark message {message_id} as read: {e}")
            return False
    
    def get_unread_message_count(self, user_id: int) -> int:
        """Get count of unread messages for a user."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*) FROM motivation_messages 
                    WHERE user_id = ? AND is_read = 0
                ''', (user_id,))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            self.logger.error(f"Failed to get unread message count for user {user_id}: {e}")
            return 0
    
    def get_community_messages(self, user_id: int, league_id: int, limit: int = 10) -> List[MotivationMessage]:
        """Get community-specific motivation messages."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM motivation_messages 
                    WHERE user_id = ? 
                    AND (metadata LIKE '%"league_id":' || ? || '%' OR message_type IN ('league_update', 'community_challenge'))
                    ORDER BY sent_at DESC 
                    LIMIT ?
                ''', (user_id, league_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append(MotivationMessage.from_dict(dict(row)))
                
                return messages
                
        except Exception as e:
            self.logger.error(f"Failed to get community messages for user {user_id}, league {league_id}: {e}")
            return []
    
    def get_unread_community_message_count(self, user_id: int, league_id: int) -> int:
        """Get count of unread community messages for a user."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*) FROM motivation_messages 
                    WHERE user_id = ? AND is_read = 0
                    AND (metadata LIKE '%"league_id":' || ? || '%' OR message_type IN ('league_update', 'community_challenge'))
                ''', (user_id, league_id))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            self.logger.error(f"Failed to get unread community message count for user {user_id}, league {league_id}: {e}")
            return 0
    
    def send_league_achievement_celebration(self, user_id: int, achievement: 'Achievement', league_id: int) -> bool:
        """Send celebration message for a new league achievement."""
        try:
            league_name = self.achievement_service.get_league_name(league_id)
            
            celebration_messages = [
                f"🎉 League Achievement! You earned: {achievement.title} in {league_name}!",
                f"🏆 Amazing work in {league_name}! You just unlocked: {achievement.title}",
                f"⭐ Fantastic league progress! You achieved: {achievement.title}",
                f"🎊 Well done in {league_name}! You earned: {achievement.title}",
                f"🌟 Incredible league performance! You unlocked: {achievement.title}"
            ]
            
            message_content = random.choice(celebration_messages)
            if achievement.metadata and 'xp_reward' in achievement.metadata:
                message_content += f"\n\n✨ +{achievement.metadata['xp_reward']} XP earned!"
            
            return self._create_motivation_message(
                user_id, MessageType.ACHIEVEMENT_EARNED, message_content,
                {'achievement_id': achievement.id, 'achievement_type': achievement.type, 'league_id': league_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send league achievement celebration for user {user_id}: {e}")
            return False
    
    def send_level_up_notification(self, user_id: int, new_level: int, total_xp: int) -> bool:
        """Send level up notification to user."""
        try:
            level_messages = [
                f"🎉 LEVEL UP! You've reached Level {new_level}!",
                f"⭐ Congratulations! You're now Level {new_level}!",
                f"🏆 Amazing progress! Welcome to Level {new_level}!",
                f"🌟 Outstanding! You've advanced to Level {new_level}!",
                f"💎 Incredible! You're now Level {new_level}!"
            ]
            
            message_content = random.choice(level_messages)
            message_content += f"\n\n📊 Total XP: {total_xp:,}"
            
            # Add level-specific encouragement
            if new_level <= 5:
                message_content += f"\n🎯 You're building a solid foundation! Keep reading!"
            elif new_level <= 10:
                message_content += f"\n💪 Great progress! You're becoming a dedicated reader!"
            elif new_level <= 20:
                message_content += f"\n🌟 Impressive! You're a true reading enthusiast!"
            else:
                message_content += f"\n👑 Legendary! You're a reading master!"
            
            return self._create_motivation_message(
                user_id, MessageType.ACHIEVEMENT_EARNED, message_content,
                {'type': 'level_up', 'level': new_level, 'total_xp': total_xp}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send level up notification for user {user_id}: {e}")
            return False
    
    def send_streak_milestone_notification(self, user_id: int, streak_days: int) -> Optional[str]:
        """Send streak milestone notification to user."""
        try:
            if streak_days == 1:
                message_content = "🎉 Congratulations! You've started your reading streak!\n\n🔥 Day 1 complete! Every journey begins with a single step."
            elif streak_days == 3:
                message_content = "🥉 First Spark! You've built your first streak!\n\n🔥 3 days strong! Keep the momentum going!"
            elif streak_days == 7:
                message_content = "🥉 One Week Reader! 1 full week of reading!\n\n🌱 Consistency pays off! You're building great habits!"
            elif streak_days == 14:
                message_content = "🥉 Two-Week Challenger! Two weeks strong!\n\n💪 Building momentum! You're on fire!"
            elif streak_days == 21:
                message_content = "🥉 Habit Builder! 21 days = new habit formed!\n\n💪 You've officially built a reading habit!"
            elif streak_days == 30:
                message_content = "🥉 One Month Champion! One month of consistent reading!\n\n🏆 Amazing dedication! You're a reading champion!"
            elif streak_days == 50:
                message_content = "🥈 Golden Streak! 50 days of dedication!\n\n✨ Shining bright! Your dedication is inspiring!"
            elif streak_days == 75:
                message_content = "🥈 Dedicated Reader! 75 days strong!\n\n🌟 Your dedication is truly inspiring!"
            elif streak_days == 100:
                message_content = "🥈 Century Club! 100 days!\n\n🎉 Welcome to the Century Club! You're unstoppable!"
            elif streak_days == 150:
                message_content = "🥇 Unstoppable! 150 days!\n\n💎 You are truly unstoppable!"
            elif streak_days == 200:
                message_content = "🥇 Marathon Mind! 200 days!\n\n🏃 Your mind is a reading marathon!"
            elif streak_days == 250:
                message_content = "🥇 Knowledge Seeker! 250 days!\n\n📚 A true seeker of knowledge!"
            elif streak_days == 300:
                message_content = "💎 Book Sage! 300 days!\n\n👑 You are a true book sage!"
            elif streak_days == 365:
                message_content = "💎 One-Year Legend! 365 days!\n\n👑 You are a reading legend!"
            else:
                message_content = f"🔥 Amazing streak! {streak_days} days strong!\n\n💪 Keep up the incredible work!"
            
            # Store the message in database
            self._create_motivation_message(
                user_id, MessageType.STREAK_MILESTONE, message_content,
                {'type': 'streak_milestone', 'streak_days': streak_days}
            )
            
            return message_content
            
        except Exception as e:
            self.logger.error(f"Failed to send streak milestone notification for user {user_id}: {e}")
            return None

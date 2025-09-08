"""
Scheduled Message Service for daily motivational quotes and reading hints.

This service handles sending scheduled messages to users at specific times.
"""

import logging
import asyncio
from datetime import datetime, time, timedelta
from typing import List, Optional
import random

from src.database.database import db_manager
from src.services.motivation_service import MotivationService
import re
from src.config.motivational_quotes import get_random_quote, get_quote_by_category
from src.config.reading_hints import get_random_hint, get_hint_by_category


class ScheduledMessageService:
    """Service for sending scheduled motivational messages and reading hints."""
    
    def __init__(self):
        """Initialize the scheduled message service."""
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.motivation_service = MotivationService()
        
        # Default times for messages (UTC timezone)
        self.morning_quote_time = time(5, 0)  # 5:00 AM UTC = 8:00 AM local time 
        self.afternoon_hint_time = time(12, 0)  # 12:00 PM UTC = 3:00 PM local time
    
    async def send_morning_quotes(self, context=None):
        """Send motivational quotes to all active users in the morning."""
        try:
            self.logger.info("Starting morning motivational quotes delivery...")
            
            # Get all active users
            active_users = self._get_active_users()
            
            if not active_users:
                self.logger.info("No active users found for morning quotes")
                return
            
            # Get a motivational quote
            quote = get_random_quote()
            
            # Send to all active users
            sent_count = 0
            for user_id in active_users:
                try:
                    # Create personalized message (HTML formatting)
                    message = f"🌅 <b>Good Morning!</b>\n\n⭐️ {quote}\n\n💪 Have a great reading day! 📚✨"
                    
                    # Store motivation message in database
                    self.motivation_service._create_motivation_message(
                        user_id, "daily_motivation", message,
                        {'type': 'morning_quote', 'quote': quote}
                    )
                    
                    # Send message via bot if context is available
                    if context and hasattr(context, 'bot'):
                        try:
                            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
                            sent_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to send morning quote to user {user_id}: {e}")
                    else:
                        # If no bot context, just store in database
                        sent_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to send morning quote to user {user_id}: {e}")
            
            self.logger.info(f"Morning quotes sent to {sent_count}/{len(active_users)} users")
            
        except Exception as e:
            self.logger.error(f"Failed to send morning quotes: {e}")
    
    async def send_afternoon_hints(self, context=None):
        """Send reading hints to all active users in the afternoon."""
        try:
            self.logger.info("Starting afternoon reading hints delivery...")
            
            # Get all active users
            active_users = self._get_active_users()
            
            if not active_users:
                self.logger.info("No active users found for afternoon hints")
                return
            
            # Get a reading hint and ensure it's HTML-safe (convert Markdown **bold** to <b>bold</b>)
            raw_hint = get_random_hint()
            hint = re.sub(r"\*\*(.+?)\*\*", r"<b>\\1</b>", raw_hint)
            
            # Send to all active users
            sent_count = 0
            for user_id in active_users:
                try:
                    # Create personalized message (HTML formatting)
                    message = f"📖 <b>Reading Tip of the Day</b>\n\n💡 {hint}\n\nHappy reading! 📚✨"
                    
                    # Store motivation message in database
                    self.motivation_service._create_motivation_message(
                        user_id, "reading_hint", message,
                        {'type': 'afternoon_hint', 'hint': hint}
                    )
                    
                    # Send message via bot if context is available
                    if context and hasattr(context, 'bot'):
                        try:
                            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
                            sent_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to send afternoon hint to user {user_id}: {e}")
                    else:
                        # If no bot context, just store in database
                        sent_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to send afternoon hint to user {user_id}: {e}")
            
            self.logger.info(f"Afternoon hints sent to {sent_count}/{len(active_users)} users")
            
        except Exception as e:
            self.logger.error(f"Failed to send afternoon hints: {e}")
    
    def _get_active_users(self) -> List[int]:
        """Get list of active user IDs."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get users who have been active in the last 30 days
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                
                cursor.execute('''
                    SELECT user_id FROM users 
                    WHERE is_active = 1 
                    AND last_activity > ?
                    ORDER BY user_id
                ''', (thirty_days_ago,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Failed to get active users: {e}")
            return []
    
    async def send_personalized_morning_message(self, user_id: int):
        """Send a personalized morning message to a specific user."""
        try:
            # Get user's current streak and stats
            from src.services.achievement_service import AchievementService
            achievement_service = AchievementService()
            stats = achievement_service.get_user_stats(user_id)
            
            if not stats:
                return False
            
            # Choose quote based on user's streak
            if stats.current_streak == 0:
                quote = get_quote_by_category("motivation")
                message = f"🌅 Good Morning!\n\n{quote}\n\n📖 Ready to start your reading journey today?"
            elif stats.current_streak < 7:
                quote = get_quote_by_category("persistence")
                message = f"🌅 Good Morning!\n\n{quote}\n\n🔥 Day {stats.current_streak} of your streak! Keep going!"
            elif stats.current_streak < 30:
                quote = get_quote_by_category("reading")
                message = f"🌅 Good Morning!\n\n{quote}\n\n🌟 {stats.current_streak} days strong! You're building an amazing habit!"
            else:
                quote = get_quote_by_category("achievement")
                message = f"🌅 Good Morning!\n\n{quote}\n\n🏆 {stats.current_streak} days! You're a reading legend!"
            
            # Send motivation message
            return self.motivation_service._create_motivation_message(
                user_id, "daily_motivation", message,
                {'type': 'personalized_morning', 'streak': stats.current_streak, 'quote': quote}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send personalized morning message to user {user_id}: {e}")
            return False
    
    async def send_personalized_afternoon_hint(self, user_id: int):
        """Send a personalized afternoon reading hint to a specific user."""
        try:
            # Get user's reading stats
            from src.services.achievement_service import AchievementService
            achievement_service = AchievementService()
            stats = achievement_service.get_user_stats(user_id)
            
            if not stats:
                return False
            
            # Choose hint based on user's level
            if stats.level <= 2:
                hint = get_hint_by_category("techniques")
                message = f"📚 Afternoon Reading Tip!\n\n{hint}\n\n🎯 Perfect for building your reading foundation!"
            elif stats.level <= 5:
                hint = get_hint_by_category("habits")
                message = f"📚 Afternoon Reading Tip!\n\n{hint}\n\n🌟 Great for maintaining your reading momentum!"
            else:
                hint = get_hint_by_category("motivation")
                message = f"📚 Afternoon Reading Tip!\n\n{hint}\n\n🏆 Advanced tips for a reading master like you!"
            
            # Send motivation message
            return self.motivation_service._create_motivation_message(
                user_id, "daily_motivation", message,
                {'type': 'personalized_afternoon', 'level': stats.level, 'hint': hint}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send personalized afternoon hint to user {user_id}: {e}")
            return False
    
    def schedule_daily_messages(self, application):
        """Schedule daily morning quotes and afternoon hints."""
        try:
            if application.job_queue is None:
                self.logger.warning("Job queue not available for scheduling messages")
                return
            
            # Schedule morning quotes at 8:00 AM
            application.job_queue.run_daily(
                self._morning_quotes_job,
                time=self.morning_quote_time,
                name="morning_quotes"
            )
            
            # Schedule afternoon hints at 3:00 PM
            application.job_queue.run_daily(
                self._afternoon_hints_job,
                time=self.afternoon_hint_time,
                name="afternoon_hints"
            )
            
            self.logger.info(f"Scheduled daily messages: Morning quotes at {self.morning_quote_time}, Afternoon hints at {self.afternoon_hint_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule daily messages: {e}")
    
    async def _morning_quotes_job(self, context):
        """Job function for morning quotes."""
        await self.send_morning_quotes(context)
    
    async def _afternoon_hints_job(self, context):
        """Job function for afternoon hints."""
        await self.send_afternoon_hints(context)
    
    def get_next_message_times(self) -> dict:
        """Get the next scheduled message times."""
        now = datetime.now()
        
        # Calculate next morning quote time
        next_morning = datetime.combine(now.date(), self.morning_quote_time)
        if next_morning <= now:
            next_morning += timedelta(days=1)
        
        # Calculate next afternoon hint time
        next_afternoon = datetime.combine(now.date(), self.afternoon_hint_time)
        if next_afternoon <= now:
            next_afternoon += timedelta(days=1)
        
        return {
            'morning_quotes': next_morning,
            'afternoon_hints': next_afternoon
        }

"""
Profile handlers for user profile management and viewing.

This module handles all profile-related bot interactions including viewing and editing profiles.
"""

import logging
from datetime import datetime, date
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.services.profile_service import ProfileService
from src.database.models.profile import UserProfile, ProfileStatistics


class ProfileHandlers:
    """Handlers for profile-related bot interactions."""
    
    def __init__(self, profile_service: ProfileService):
        self.profile_service = profile_service
        self.logger = logging.getLogger(__name__)
    
    async def handle_profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command to show user profile."""
        try:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id if update.effective_chat else None
            query = update.callback_query
            if query:
                await query.answer()
            
            # Get user profile and statistics
            profile = self.profile_service.get_user_profile(user_id)
            stats = self.profile_service.get_comprehensive_statistics(user_id)
            insights = self.profile_service.get_reading_insights(user_id)
            
            if not profile or not stats:
                if query:
                    await query.edit_message_text("❌ Unable to load your profile. Please try again later.")
                elif chat_id is not None:
                    await context.bot.send_message(chat_id=chat_id, text="❌ Unable to load your profile. Please try again later.")
                return

            # Values should come from database; do not auto-populate from Telegram here
            
            # Create comprehensive profile display
            display = self._create_profile_display(profile, stats, insights)
            
            # Create keyboard for profile actions with nice arrangement
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile"), InlineKeyboardButton("📊 Detailed Stats", callback_data="detailed_stats")],
                [InlineKeyboardButton("🎯 Reading Goals", callback_data="reading_goals")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="mode_individual")]
            ])
            
            if query and query.message:
                await query.edit_message_text(display, reply_markup=keyboard, parse_mode='HTML')
            elif chat_id is not None:
                await context.bot.send_message(chat_id=chat_id, text=display, reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Failed to handle profile command: {e}")
            if update.callback_query and update.callback_query.message:
                await update.callback_query.edit_message_text("❌ Error loading profile. Please try again later.")
            elif update.effective_chat:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Error loading profile. Please try again later.")
    
    async def handle_edit_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle edit profile callback."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            profile = self.profile_service.get_user_profile(user_id)
            
            if not profile:
                await query.edit_message_text("❌ Unable to load profile for editing.")
                return
            
            # Create edit profile display
            display = "✏️ <b>Edit Your Profile</b>\n"
            display += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            display += f"👤 <b>Display Name:</b> {profile.display_name or 'Not set'}\n"
            display += f"🏷️ <b>Nickname:</b> {profile.nickname or 'Not set'}\n"
            display += f"📝 <b>Bio:</b> {profile.bio or 'Not set'}\n"
            display += f"🎯 <b>Daily Goal:</b> {profile.reading_goal_pages_per_day} pages\n"
            display += f"⏰ <b>Preferred Time:</b> {profile.preferred_reading_time or 'Not set'}\n"
            display += f"📚 <b>Reading Level:</b> {profile.reading_level or 'Beginner'}\n"
            display += "Choose what you'd like to edit:"
            
            # Create edit options keyboard with nice arrangement
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Display Name", callback_data="edit_display_name"), InlineKeyboardButton("🏷️ Nickname", callback_data="edit_nickname")],
                [InlineKeyboardButton("📝 Bio", callback_data="edit_bio")],
                [InlineKeyboardButton("🎯 Daily Goal", callback_data="edit_daily_goal"), InlineKeyboardButton("⏰ Reading Time", callback_data="edit_reading_time")],
                [InlineKeyboardButton("🏠 Back to Profile", callback_data="view_profile")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit profile: {e}")
            await query.edit_message_text("❌ Error loading edit profile.")
    
    async def handle_edit_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing specific profile fields."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            field = query.data.replace("edit_", "")
            
            # Set the field being edited in context
            context.user_data['editing_field'] = field
            
            # Create field-specific prompts
            prompts = {
                'display_name': "👤 Enter your display name:",
                'nickname': "🏷️ Enter your nickname (or type '-' to remove):",
                'bio': "📝 Enter your bio (or type '-' to remove):",
                'daily_goal': "🎯 Enter your daily reading goal (pages):",
                'reading_time': "⏰ Enter your preferred reading time (e.g., '9:00 PM' or 'Morning'):"
            }
            
            if field not in prompts:
                await query.edit_message_text("❌ Invalid field to edit.")
                return
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="edit_profile")]
            ])
            
            await query.edit_message_text(prompts[field], reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit field: {e}")
            await query.edit_message_text("❌ Error starting edit.")
    
    async def handle_edit_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input for profile editing."""
        try:
            user_id = update.effective_user.id
            field = context.user_data.get('editing_field')
            
            self.logger.info(f"Profile edit text input - User: {user_id}, Field: {field}, Text: {update.message.text}")
            
            if not field:
                self.logger.info("No editing field set, not in edit mode")
                return  # Not in edit mode
            
            text = update.message.text.strip()
            
            # Handle special cases
            if text == '-' and field in ['nickname', 'bio']:
                text = None
            
            # Validate daily goal input
            if field == 'daily_goal':
                try:
                    goal_value = int(text)
                    if goal_value <= 0:
                        await update.message.reply_text("❌ Daily goal must be a positive number. Please try again.")
                        return
                    text = str(goal_value)
                except ValueError:
                    await update.message.reply_text("❌ Please enter a valid number for daily goal. Please try again.")
                    return
            
            # Update the profile
            success = self.profile_service.update_profile_field(user_id, field, text)
            
            if success:
                # Clear editing state
                context.user_data.pop('editing_field', None)
                
                # Show success message and return to edit profile
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Continue Editing", callback_data="edit_profile")],
                    [InlineKeyboardButton("🏠 Back to Profile", callback_data="view_profile")]
                ])
                
                await update.message.reply_text(f"✅ {field.replace('_', ' ').title()} updated successfully!", reply_markup=keyboard)
            else:
                await update.message.reply_text("❌ Failed to update profile. Please try again.")
                
        except Exception as e:
            self.logger.error(f"Failed to handle edit text input: {e}")
            await update.message.reply_text("❌ Error updating profile.")
    
    async def handle_detailed_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle detailed statistics display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            stats = self.profile_service.get_comprehensive_statistics(user_id)
            
            if not stats:
                await query.edit_message_text("❌ Unable to load detailed statistics.")
                return
            
            # Create detailed statistics display
            display = "📊 <b>Detailed Reading Statistics</b>\n"
            display += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Reading Overview
            display += "📚 <b>Reading Overview</b>\n"
            display += f"📖 Books Completed: {stats.total_books_read}\n"
            display += f"📄 Total Pages: {stats.total_pages_read:,}\n"
            display += f"📅 Reading Days: {stats.total_reading_days}\n"
            display += f"📊 Avg Pages/Day: {stats.average_pages_per_day:.1f}\n"
            display += f"📖 Avg Pages/Book: {stats.average_pages_per_book:.1f}\n\n"
            
            # Streak Information
            display += "🔥 <b>Streak Information</b>\n"
            display += f"⚡ Current Streak: {stats.current_streak} days\n"
            display += f"🏆 Longest Streak: {stats.longest_streak} days\n"
            if stats.streak_start_date:
                display += f"📅 Streak Started: {stats.streak_start_date}\n"
            display += f"📈 Consistency Score: {stats.reading_consistency_score:.1f}%\n\n"
            
            # Reading Patterns
            display += "📈 <b>Reading Patterns</b>\n"
            display += f"📅 Favorite Day: {stats.favorite_reading_day}\n"
            display += f"⏰ Favorite Time: {stats.favorite_reading_time}\n"
            display += f"📆 Most Productive Month: {stats.most_productive_month}\n"
            display += f"⚡ Reading Speed: {stats.reading_speed_pages_per_hour:.1f} pages/hour\n\n"
            
            # Gamification Stats
            display += "🎮 <b>Gamification</b>\n"
            display += f"⭐ Level: {stats.level}\n"
            display += f"🎯 XP: {stats.xp:,}\n"
            display += f"🏆 Achievements: {stats.total_achievements}\n\n"
            
            # Account Information
            display += "👤 <b>Account Information</b>\n"
            display += f"📅 Joined: {stats.join_date}\n"
            if stats.last_reading_date:
                display += f"📖 Last Reading: {stats.last_reading_date}\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Back to Profile", callback_data="view_profile")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Failed to handle detailed stats: {e}")
            await query.edit_message_text("❌ Error loading detailed statistics.")
    
    async def handle_reading_goals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle reading goals management."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            profile = self.profile_service.get_user_profile(user_id)
            stats = self.profile_service.get_comprehensive_statistics(user_id)
            
            if not profile or not stats:
                await query.edit_message_text("❌ Unable to load reading goals.")
                return
            
            # Create reading goals display
            display = "🎯 <b>Reading Goals & Progress</b>\n"
            display += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Current Goal
            display += f"📊 <b>Daily Goal:</b> {profile.reading_goal_pages_per_day} pages\n"
            display += f"📈 <b>Current Average:</b> {stats.average_pages_per_day:.1f} pages/day\n"
            
            # Goal Progress
            goal_progress = (stats.average_pages_per_day / profile.reading_goal_pages_per_day) * 100
            if goal_progress >= 100:
                display += f"🎉 <b>Goal Status:</b> Exceeding goal by {goal_progress - 100:.1f}%!\n"
            elif goal_progress >= 80:
                display += f"📈 <b>Goal Status:</b> Close to goal ({goal_progress:.1f}%)\n"
            else:
                display += f"📊 <b>Goal Status:</b> {goal_progress:.1f}% of daily goal\n"
            
            display += "\n"
            
            # Goal Recommendations
            if goal_progress < 50:
                display += "💡 <b>Recommendation:</b> Try setting a smaller daily goal to build consistency.\n"
            elif goal_progress > 150:
                display += "💡 <b>Recommendation:</b> Consider increasing your daily goal to challenge yourself!\n"
            else:
                display += "💡 <b>Recommendation:</b> Great job maintaining your reading goal!\n"
            
            display += "\n"
            
            # Weekly/Monthly Goals
            weekly_goal = profile.reading_goal_pages_per_day * 7
            monthly_goal = profile.reading_goal_pages_per_day * 30
            
            display += f"📅 <b>Weekly Goal:</b> {weekly_goal} pages\n"
            display += f"📆 <b>Monthly Goal:</b> {monthly_goal} pages\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 Set New Daily Goal", callback_data="edit_daily_goal")],
                [InlineKeyboardButton("📊 View Progress", callback_data="goal_progress")],
                [InlineKeyboardButton("🏠 Back to Profile", callback_data="view_profile")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Failed to handle reading goals: {e}")
            await query.edit_message_text("❌ Error loading reading goals.")
    
    async def handle_goal_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle goal progress view."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            profile = self.profile_service.get_user_profile(user_id)
            stats = self.profile_service.get_comprehensive_statistics(user_id)
            
            if not profile or not stats:
                await query.edit_message_text("❌ Unable to load goal progress.")
                return
            
            # Create detailed progress display
            display = "📊 <b>Detailed Goal Progress</b>\n"
            display += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Current vs Goal
            daily_goal = profile.reading_goal_pages_per_day
            current_avg = stats.average_pages_per_day
            
            display += f"🎯 <b>Daily Goal:</b> {daily_goal} pages\n"
            display += f"📈 <b>Current Average:</b> {current_avg:.1f} pages/day\n\n"
            
            # Progress visualization
            progress_percent = (current_avg / daily_goal) * 100
            progress_bar = self._create_progress_bar(progress_percent)
            display += f"📊 <b>Progress:</b> {progress_bar} {progress_percent:.1f}%\n\n"
            
            # Weekly/Monthly progress
            weekly_actual = current_avg * 7
            monthly_actual = current_avg * 30
            weekly_goal = daily_goal * 7
            monthly_goal = daily_goal * 30
            
            display += f"📅 <b>Weekly:</b> {weekly_actual:.0f}/{weekly_goal} pages\n"
            display += f"📆 <b>Monthly:</b> {monthly_actual:.0f}/{monthly_goal} pages\n\n"
            
            # Insights
            if progress_percent >= 100:
                display += "🎉 <b>Excellent!</b> You're exceeding your daily goal!\n"
            elif progress_percent >= 80:
                display += "📈 <b>Great job!</b> You're close to your goal.\n"
            elif progress_percent >= 50:
                display += "📊 <b>Good progress!</b> Keep building consistency.\n"
            else:
                display += "💪 <b>Keep going!</b> Every page counts toward your goal.\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 Reading Goals", callback_data="reading_goals")],
                [InlineKeyboardButton("🏠 Back to Profile", callback_data="view_profile")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            self.logger.error(f"Failed to handle goal progress: {e}")
            await query.edit_message_text("❌ Error loading goal progress.")
    
    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a visual progress bar."""
        filled = int((percentage / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    def _create_profile_display(self, profile: UserProfile, stats: ProfileStatistics, insights: list) -> str:
        """Create comprehensive profile display."""
        display = "👤 <b>Your Reading Profile</b>\n"
        display += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Personal Information
        display_name = profile.display_name or "Reader"
        display += f"👤 <b>Name:</b> {display_name}\n"
        if profile.nickname:
            display += f"🏷️ <b>Nickname:</b> {profile.nickname}\n"
        else:
            display += f"🏷️ <b>Nickname:</b> Not set\n"
        
        # Get phone number from users table
        phone = self._get_user_phone(profile.user_id)
        if phone:
            display += f"📞 <b>Phone:</b> {phone}\n"
        else:
            display += f"📞 <b>Phone:</b> Not provided\n"
        
        if profile.bio:
            display += f"📝 <b>Bio:</b> {profile.bio}\n"
        
        display += f"📚 <b>Reading Level:</b> {profile.reading_level or 'Beginner'}\n"
        display += "\n"
        
        # Key Statistics
        display += "📊 <b>Key Statistics</b>\n"
        display += f"📖 Books Read: {stats.total_books_read}\n"
        display += f"📄 Total Pages: {stats.total_pages_read:,}\n"
        display += f"🔥 Current Streak: {stats.current_streak} days\n"
        display += f"⭐ Level: {stats.level} ({stats.xp:,} XP)\n"
        display += f"🏆 Achievements: {stats.total_achievements}\n\n"
        
        # Reading Insights
        if insights:
            display += "💡 <b>Reading Insights</b>\n"
            for insight in insights[:3]:  # Show top 3 insights
                display += f"• {insight}\n"
            display += "\n"
        
        # Reading Goals
        display += "🎯 <b>Reading Goals</b>\n"
        display += f"📊 Daily Goal: {profile.reading_goal_pages_per_day} pages\n"
        display += f"📈 Current Average: {stats.average_pages_per_day:.1f} pages/day\n"
        
        # Goal progress indicator
        goal_progress = (stats.average_pages_per_day / profile.reading_goal_pages_per_day) * 100
        if goal_progress >= 100:
            display += f"🎉 Exceeding goal by {goal_progress - 100:.1f}%!\n"
        else:
            display += f"📊 {goal_progress:.1f}% of daily goal\n"
        
        return display
    
    def _get_user_phone(self, user_id: int) -> str:
        """Get user's phone number from the users table."""
        try:
            with self.profile_service.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT contact FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                return result[0] if result and result[0] else ""
        except Exception as e:
            self.logger.error(f"Failed to get user phone for {user_id}: {e}")
            return ""

"""
Achievement handlers for gamification system.

This module handles achievement-related bot interactions and displays.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.services.achievement_service import AchievementService
from src.services.motivation_service import MotivationService
from src.services.visual_service import VisualService


class AchievementHandlers:
    """Handlers for achievement-related bot interactions."""
    
    def __init__(self):
        """Initialize achievement handlers."""
        self.logger = logging.getLogger(__name__)
        self.achievement_service = AchievementService()
        self.motivation_service = MotivationService()
        self.visual_service = VisualService()
    
    async def handle_achievements_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle achievements menu display - context-aware (individual vs community)."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Determine context (individual vs community mode)
            league_id = context.user_data.get('current_league_id')
            is_community_mode = context.user_data.get('community_mode', False)
            
            # Only show community mode if user is actively in community mode
            # or has a specific league context
            if is_community_mode and league_id is None:
                # User is in community mode but no specific league selected, show league selection
                await self._show_community_achievements_league_selection(query, context)
            elif league_id is not None:
                # User has league context, show league-specific achievements
                await self._handle_community_achievements_menu(query, context, league_id)
            else:
                # User is in individual mode, show individual achievements
                await self._handle_individual_achievements_menu(query, context)
            
        except Exception as e:
            self.logger.error(f"Failed to handle achievements menu: {e}")
            await query.edit_message_text("❌ Error loading achievements.")
    
    async def _handle_individual_achievements_menu(self, query, context):
        """Handle individual mode achievements menu."""
        user_id = query.from_user.id
        
        # Get user stats and recent achievements (all achievements)
        stats = self.achievement_service.get_user_stats(user_id)
        recent_achievements = self.achievement_service.get_user_achievements(user_id, 5)
        
        if not stats:
            await query.edit_message_text("❌ Unable to load your achievements.")
            return
        
        # Create individual achievements display
        display = "🏆 Individual Achievements\n"
        display += "📚 All your reading accomplishments\n\n"
        
        # Stats overview
        display += self.visual_service.create_streak_display(stats.current_streak, stats.longest_streak)
        display += f"\n{self.visual_service.create_level_display(stats.level, stats.xp)}"
        display += f"\n📚 Books: {stats.books_completed} | 📄 Pages: {stats.total_pages_read:,}"
        display += f"\n🏆 Total Achievements: {stats.total_achievements}\n"
        
        # Recent achievements
        if recent_achievements:
            display += "\n🎉 Recent Achievements:\n"
            for achievement in recent_achievements:
                display += f"• {self.visual_service.create_achievement_badge(achievement)}\n"
        else:
            display += "\n📖 Start reading to earn your first achievement!"
        
        # Create keyboard for individual mode
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Detailed Stats", callback_data="achievement_stats")],
            [InlineKeyboardButton("🎯 All Achievements", callback_data="achievement_list")],
            [InlineKeyboardButton("💬 Motivation Messages", callback_data="motivation_messages")],
            [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")]
        ])
        
        await query.edit_message_text(display, reply_markup=keyboard)
    
    async def _handle_community_achievements_menu(self, query, context, league_id=None):
        """Handle community mode achievements menu."""
        user_id = query.from_user.id
        
        # If no league_id provided, show league selection
        if league_id is None:
            await self._show_community_achievements_league_selection(query, context)
            return
        
        # Get league-specific and general community achievements
        league_stats = self.achievement_service.get_league_user_stats(user_id, league_id)
        general_stats = self.achievement_service.get_user_stats(user_id)
        league_achievements = self.achievement_service.get_league_achievements(user_id, league_id, 5)
        
        # Get league name
        league_name = self.achievement_service.get_league_name(league_id)
        
        # Create community achievements display
        display = f"🏆 Community Achievements\n"
        display += f"👥 {league_name} League\n\n"
        
        # League-specific stats
        if league_stats:
            display += f"📊 League Progress:\n"
            display += f"📚 Books in League: {league_stats.get('books_completed', 0)}\n"
            display += f"📄 Pages in League: {league_stats.get('pages_read', 0):,}\n"
            display += f"🏆 League Achievements: {league_stats.get('achievements', 0)}\n"
            display += f"🥇 League Position: #{league_stats.get('position', 'N/A')}\n\n"
        
        # General stats
        if general_stats:
            display += f"📈 Overall Progress:\n"
            display += self.visual_service.create_streak_display(general_stats.current_streak, general_stats.longest_streak)
            display += f"\n{self.visual_service.create_level_display(general_stats.level, general_stats.xp)}\n"
        
        # Recent league achievements
        if league_achievements:
            display += "\n🎉 Recent League Achievements:\n"
            for achievement in league_achievements:
                display += f"• {self.visual_service.create_achievement_badge(achievement)}\n"
        else:
            display += "\n👥 Start participating in the league to earn achievements!"
        
        # Create keyboard for community mode
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 League Stats", callback_data="league_achievement_stats")],
            [InlineKeyboardButton("🎯 League Achievements", callback_data="league_achievement_list")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="com_leaderboard")],
            [InlineKeyboardButton("💬 Community Messages", callback_data="community_motivation_messages")],
            [InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")]
        ])
        
        await query.edit_message_text(display, reply_markup=keyboard)
    
    async def _show_community_achievements_league_selection(self, query, context):
        """Show league selection for community achievements."""
        user_id = query.from_user.id
        
        # Get user's leagues
        from src.services.factory import get_league_service
        league_service = get_league_service()
        user_leagues = league_service.get_user_leagues(user_id)
        
        if not user_leagues:
            await query.edit_message_text(
                "🏆 <b>Community Achievements</b>\n\n"
                "You're not in any leagues yet. Join a league to start earning community achievements!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔎 Browse Leagues", callback_data="com_browse")],
                    [InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")]
                ])
            )
            return
        
        # Show leagues for achievements
        keyboard = []
        for league in user_leagues:
            keyboard.append([
                InlineKeyboardButton(
                    f"🏆 {league.name}",
                    callback_data=f"com_achievements_league_{league.league_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")])
        
        await query.edit_message_text(
            "🏆 <b>Community Achievements</b>\n\n"
            "Choose a league to view achievements:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_achievement_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle detailed achievement stats display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Get comprehensive stats
            stats = self.achievement_service.get_user_stats(user_id)
            if not stats:
                await query.edit_message_text("❌ Unable to load your stats.")
                return
            
            # Create detailed stats display
            display = self.visual_service.create_reading_stats_display(user_id)
            
            # Add additional details
            display += f"\n\n📈 Detailed Statistics:\n"
            display += f"📅 Last Reading: {stats.last_reading_date.strftime('%Y-%m-%d') if stats.last_reading_date else 'Never'}\n"
            display += f"🎯 Current Streak Started: {stats.streak_start_date.strftime('%Y-%m-%d') if stats.streak_start_date else 'N/A'}\n"
            
            # Calculate averages
            if stats.books_completed > 0:
                avg_pages_per_book = stats.total_pages_read / stats.books_completed
                display += f"📊 Average Pages per Book: {avg_pages_per_book:.1f}\n"
            
            if stats.total_achievements > 0:
                avg_xp_per_achievement = stats.xp / stats.total_achievements
                display += f"⭐ Average XP per Achievement: {avg_xp_per_achievement:.1f}\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Weekly Summary", callback_data="weekly_summary")],
                [InlineKeyboardButton("🏆 Back to Achievements", callback_data="achievement_menu")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle achievement stats: {e}")
            await query.edit_message_text("❌ Error loading detailed stats.")
    
    async def handle_achievement_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all achievements list display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Get all user achievements
            all_achievements = self.achievement_service.get_user_achievements(user_id, 20)
            
            if not all_achievements:
                display = "🏆 No achievements yet!\n\n"
                display += "📖 Start reading to earn your first achievement!\n"
                display += "🎯 Complete books, maintain streaks, and reach milestones to unlock achievements."
            else:
                display = f"🏆 All Achievements ({len(all_achievements)})\n\n"
                
                for i, achievement in enumerate(all_achievements, 1):
                    display += f"{i:2d}. {self.visual_service.create_achievement_badge(achievement)}\n"
                    display += f"    📅 {achievement.earned_at.strftime('%Y-%m-%d')}\n\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏆 Back to Achievements", callback_data="achievement_menu")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle achievement list: {e}")
            await query.edit_message_text("❌ Error loading achievements list.")
    
    async def handle_motivation_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle motivation messages display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Get motivation messages
            messages = self.motivation_service.get_user_messages(user_id, 10)
            unread_count = self.motivation_service.get_unread_message_count(user_id)
            
            if not messages:
                display = "💬 No motivation messages yet!\n\n"
                display += "📖 Start reading to receive personalized motivation messages!"
            else:
                display = f"💬 Motivation Messages ({unread_count} unread)\n\n"
                
                for i, message in enumerate(messages, 1):
                    status = "🔴" if not message.is_read else "✅"
                    display += f"{status} {message.content}\n"
                    display += f"   📅 {message.sent_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📬 Mark All as Read", callback_data="mark_messages_read")],
                [InlineKeyboardButton("🏆 Back to Achievements", callback_data="achievement_menu")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle motivation messages: {e}")
            await query.edit_message_text("❌ Error loading motivation messages.")
    
    async def handle_weekly_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle weekly progress summary display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Create weekly summary
            display = self.visual_service.create_weekly_progress_summary(user_id)
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Back to Stats", callback_data="achievement_stats")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle weekly summary: {e}")
            await query.edit_message_text("❌ Error loading weekly summary.")
    
    async def handle_mark_messages_read(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle marking all messages as read."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Mark all messages as read
            with self.achievement_service.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE motivation_messages SET is_read = 1 WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
            
            await query.edit_message_text("✅ All messages marked as read!")
            
            # Return to motivation messages
            await self.handle_motivation_messages(update, context)
            
        except Exception as e:
            self.logger.error(f"Failed to mark messages as read: {e}")
            await query.edit_message_text("❌ Error marking messages as read.")
    
    async def handle_achievement_celebration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                           achievement: 'Achievement'):
        """Handle achievement celebration display."""
        try:
            query = update.callback_query
            await query.answer()
            
            # Create celebration display
            display = self.visual_service.create_achievement_celebration_display(achievement)
            
            # Send celebration message
            self.motivation_service.send_achievement_celebration(query.from_user.id, achievement)
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏆 View All Achievements", callback_data="achievement_menu")],
                [InlineKeyboardButton("📊 View Stats", callback_data="achievement_stats")],
                [InlineKeyboardButton("📖 Continue Reading", callback_data="mode_individual")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle achievement celebration: {e}")
            await query.edit_message_text("🎉 Achievement unlocked!")
    
    async def handle_league_achievement_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle league-specific achievement stats display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            league_id = context.user_data.get('current_league_id')
            
            if not league_id:
                await query.edit_message_text("❌ No league context found.")
                return
            
            # Get league-specific stats
            league_stats = self.achievement_service.get_league_user_stats(user_id, league_id)
            league_name = self.achievement_service.get_league_name(league_id)
            
            if not league_stats:
                await query.edit_message_text("❌ Unable to load league stats.")
                return
            
            # Create detailed league stats display
            display = f"📊 League Statistics\n"
            display += f"👥 {league_name} League\n\n"
            
            display += f"📈 Your League Performance:\n"
            display += f"📚 Books Completed: {league_stats.get('books_completed', 0)}\n"
            display += f"📄 Pages Read: {league_stats.get('pages_read', 0):,}\n"
            display += f"🏆 League Achievements: {league_stats.get('achievements', 0)}\n"
            display += f"🥇 Current Position: #{league_stats.get('position', 'N/A')}\n"
            
            # Add league-specific achievements progress
            display += f"\n🎯 League Achievement Progress:\n"
            league_achievements = self.achievement_service.get_league_achievements(user_id, league_id, 10)
            
            if league_achievements:
                for achievement in league_achievements:
                    display += f"• {self.visual_service.create_achievement_badge(achievement)}\n"
            else:
                display += "📖 No league achievements yet. Keep reading to unlock them!"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 All League Achievements", callback_data="league_achievement_list")],
                [InlineKeyboardButton("🏆 Back to League Achievements", callback_data="achievement_menu")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle league achievement stats: {e}")
            await query.edit_message_text("❌ Error loading league stats.")
    
    async def handle_league_achievement_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle league-specific achievements list display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            league_id = context.user_data.get('current_league_id')
            
            if not league_id:
                await query.edit_message_text("❌ No league context found.")
                return
            
            # Get all league achievements
            league_achievements = self.achievement_service.get_league_achievements(user_id, league_id, 20)
            league_name = self.achievement_service.get_league_name(league_id)
            
            if not league_achievements:
                display = f"🏆 No League Achievements Yet!\n\n"
                display += f"👥 {league_name} League\n\n"
                display += "📖 Start participating in the league to earn achievements!\n"
                display += "🎯 Complete books, read pages, and climb the leaderboard!"
            else:
                display = f"🏆 All League Achievements ({len(league_achievements)})\n"
                display += f"👥 {league_name} League\n\n"
                
                for i, achievement in enumerate(league_achievements, 1):
                    display += f"{i:2d}. {self.visual_service.create_achievement_badge(achievement)}\n"
                    display += f"    📅 {achievement.earned_at.strftime('%Y-%m-%d')}\n\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 League Stats", callback_data="league_achievement_stats")],
                [InlineKeyboardButton("🏆 Back to League Achievements", callback_data="achievement_menu")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle league achievement list: {e}")
            await query.edit_message_text("❌ Error loading league achievements.")
    
    async def handle_community_motivation_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle community-specific motivation messages display."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            league_id = context.user_data.get('current_league_id')
            
            if not league_id:
                await query.edit_message_text("❌ No league context found.")
                return
            
            # Get community-specific motivation messages
            messages = self.motivation_service.get_community_messages(user_id, league_id, 10)
            unread_count = self.motivation_service.get_unread_community_message_count(user_id, league_id)
            league_name = self.achievement_service.get_league_name(league_id)
            
            if not messages:
                display = f"💬 No Community Messages Yet!\n\n"
                display += f"👥 {league_name} League\n\n"
                display += "📖 Start participating in the league to receive community messages!"
            else:
                display = f"💬 Community Messages ({unread_count} unread)\n"
                display += f"👥 {league_name} League\n\n"
                
                for i, message in enumerate(messages, 1):
                    status = "🔴" if not message.is_read else "✅"
                    display += f"{status} {message.content}\n"
                    display += f"   📅 {message.sent_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            # Create keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📬 Mark All as Read", callback_data="mark_community_messages_read")],
                [InlineKeyboardButton("🏆 Back to League Achievements", callback_data="achievement_menu")]
            ])
            
            await query.edit_message_text(display, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to handle community motivation messages: {e}")
            await query.edit_message_text("❌ Error loading community messages.")

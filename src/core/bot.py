"""
Main bot class for Read & Revive Bot.

This module contains the main bot class that orchestrates all functionality.
"""

import logging
import re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.ext import Defaults

from src.config.settings import BOT_TOKEN
from src.core.handlers.user_handlers import UserHandlers
from src.core.handlers.admin_handlers import AdminHandlers
from src.core.handlers.admin_league_handlers import AdminLeagueHandlers
from src.core.handlers.conversation import ConversationHandlers
from src.core.handlers.achievement_handlers import AchievementHandlers
from src.services.book_service import BookService
from src.services.reminder_service import ReminderService
from src.services.achievement_service import AchievementService
from src.services.motivation_service import MotivationService
from src.services.visual_service import VisualService
from src.services.scheduled_message_service import ScheduledMessageService
from src.services.factory import get_league_service


class ReadingTrackerBot:
    """Main bot class for Read & Revive Bot."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.application = None
        self.user_handlers = None
        self.admin_handlers = None
        self.admin_league_handlers = None
        self.conversation_handlers = None
        self.achievement_handlers = None
        self.book_service = BookService()
        self.reminder_service = ReminderService()
        self.achievement_service = AchievementService()
        self.motivation_service = MotivationService()
        self.visual_service = VisualService()
        self.scheduled_message_service = ScheduledMessageService()
        self._init_handlers()
        self._init_application()
    
    def _init_handlers(self):
        try:
            self.user_handlers = UserHandlers()
            self.admin_handlers = AdminHandlers()
            self.admin_league_handlers = AdminLeagueHandlers(get_league_service())
            self.conversation_handlers = ConversationHandlers()
            self.achievement_handlers = AchievementHandlers()
            self.logger.info("✅ All handlers initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize handlers: {e}")
            raise
    
    async def _handle_create_league_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle create_league command."""
        from src.core.handlers.admin_league_handlers import AdminLeagueHandlers
        from src.services.factory import get_league_service
        
        league_service = get_league_service()
        league_handlers = AdminLeagueHandlers(league_service)
        
        # Set conversation state
        context.user_data['creating_league'] = True
        context.user_data['league_data'] = {}
        
        await league_handlers.handle_create_league(update, context)
    
    async def _handle_add_book_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add_book command."""
        from src.core.handlers.admin_handlers import AdminHandlers
        
        admin_handlers = AdminHandlers()
        
        # Set conversation state
        context.user_data['adding_book'] = True
        context.user_data['book_data'] = {}
        context.user_data['book_step'] = 'title'
        
        await admin_handlers.handle_book_addition(update, context)
    
    def _init_application(self):
        try:
            defaults = Defaults(parse_mode=ParseMode.HTML)
            self.application = Application.builder().token(BOT_TOKEN).defaults(defaults).build()
            self.logger.info("✅ Telegram application initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize application: {e}")
            raise
    
    def _setup_handlers(self):
        try:
            # /start and registration first
            self.application.add_handler(CommandHandler('start', self.user_handlers.start))
            
            # Progress numeric input - MUST come before general text handler
            self.application.add_handler(MessageHandler(filters.Regex(re.compile(r"^\d+$")), self._handle_progress_number))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.user_handlers.handle_registration_text))

            # User commands
            self.application.add_handler(CommandHandler('help', self.user_handlers.help_command))
            self.application.add_handler(CommandHandler('progress', self.user_handlers.progress_command))
            self.application.add_handler(CommandHandler('books', self.user_handlers.books_command))
            self.application.add_handler(CommandHandler('stats', self.user_handlers.stats_command))
            self.application.add_handler(CommandHandler('league', self.user_handlers.league_command))
            self.application.add_handler(CommandHandler('leaderboard', self.user_handlers.league_handlers.handle_leaderboard_command))
            self.application.add_handler(CommandHandler('reminder', self.user_handlers.reminder_command))
            self.application.add_handler(CommandHandler('reminder_set', self.user_handlers.reminder_set))
            self.application.add_handler(CommandHandler('reminder_view', self.user_handlers.reminder_view))
            self.application.add_handler(CommandHandler('reminder_remove', self.user_handlers.reminder_remove))
            self.application.add_handler(CommandHandler('profile', self.user_handlers.profile_command))
            
            # Admin commands
            self.application.add_handler(CommandHandler('admin', self.admin_handlers.admin_command))
            self.application.add_handler(CommandHandler('create_league', self._handle_create_league_command))
            self.application.add_handler(CommandHandler('add_book', self._handle_add_book_command))
            
            # Admin message handlers
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_book_addition))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_user_search))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_user_ban))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_user_unban))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_user_message))

            # Mode selection and submenus
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_mode_callback, pattern="^mode_(individual|community)$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_individual_action, pattern="^ind_(my_books|add_book|progress|stats|reminder|set_goal)$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_community_action, pattern="^com_(browse|my|progress|leaderboard|reminder|stats)$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_community_progress_league, pattern="^com_progress_league_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_community_reminder_league, pattern="^com_reminder_league_\\d+$"))

            # Goal inline callbacks
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_goal_inline, pattern=r"^goal_(\d+|custom)$"))
            # Reminder inline callbacks
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_reminder_inline, pattern=r"^rem_(menu|time_\d{4}|disable|custom)$"))
            # Community reminder callbacks
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_community_reminder_time, pattern=r"^com_reminder_time_\d+_\d{4}$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_community_reminder_custom, pattern=r"^com_reminder_custom_\d+$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_community_reminder_disable, pattern=r"^com_reminder_disable_\d+$"))

            # My Books pagination, open and delete callbacks
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_my_books_page, pattern=r"^ind_my_books_page_\d+$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_my_book_open, pattern=r"^ind_book_\d+$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_delete_book_inline, pattern=r"^ind_del_\d+$"))
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_delete_book_inline, pattern=r"^ind_del_confirm_\d+$"))
            
            # Admin callbacks
            self.application.add_handler(CallbackQueryHandler(self.admin_handlers.handle_admin_callback, pattern=r"^admin_.*$"))
            
            # League book selection callbacks
            self.application.add_handler(CallbackQueryHandler(self.admin_league_handlers.handle_league_book_selection, pattern=r"^league_book_\d+$"))
            self.application.add_handler(CallbackQueryHandler(self.admin_league_handlers.handle_league_book_selection, pattern="^league_cancel$"))
            self.application.add_handler(CallbackQueryHandler(self.admin_league_handlers.handle_league_book_selection, pattern=r"^league_books_page_\d+$"))
            
            # League confirmation callbacks
            self.application.add_handler(CallbackQueryHandler(self.admin_league_handlers.handle_league_confirmation, pattern="^league_confirm$"))
            self.application.add_handler(CallbackQueryHandler(self.admin_league_handlers.handle_league_confirmation, pattern="^league_cancel_confirm$"))

            # Admin: league creation + edits
            self.application.add_handler(CommandHandler('setbook', self.admin_league_handlers.handle_create_league))
            self.application.add_handler(CommandHandler('league_edit_goal', self.admin_league_handlers.edit_goal))
            self.application.add_handler(CommandHandler('league_edit_dates', self.admin_league_handlers.edit_dates))
            self.application.add_handler(CommandHandler('league_edit_max', self.admin_league_handlers.edit_max))
            self.application.add_handler(CommandHandler('league_export', self.admin_league_handlers.export_league))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_league_name_input))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_league_description_input))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_league_book_input))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_league_duration_input))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_league_daily_goal_input))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_league_max_members_input))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_league_handlers.handle_confirm_or_cancel))

            # League callbacks
            lh = self.user_handlers.league_handlers
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_menu, pattern="^league_main_menu$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_browse, pattern="^league_browse$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_my_leagues, pattern="^league_my_leagues$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_view, pattern="^league_view_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_join, pattern="^league_join_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_join_confirm, pattern="^league_join_confirm_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_leave, pattern="^league_leave_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_leave_confirm, pattern="^league_leave_confirm_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_leaderboard_view, pattern="^league_lb_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_stats_callback, pattern="^league_stats$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_leaderboard_callback, pattern="^league_leaderboard$"))
            self.application.add_handler(CallbackQueryHandler(lh.handle_league_menu, pattern="^main_menu$"))

            # Book callbacks
            self.application.add_handler(CallbackQueryHandler(self._handle_book_start, pattern="^book_start_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(self._handle_progress_select_book, pattern="^progress_select_\\d+$"))
            self.application.add_handler(CallbackQueryHandler(self._handle_progress_quick_add, pattern=r"^progress_add_-?\d+$"))
            self.application.add_handler(CallbackQueryHandler(self._handle_progress_submit, pattern=r"^progress_submit$"))
            self.application.add_handler(CallbackQueryHandler(self._handle_noop, pattern=r"^noop$"))
            
            # Achievement callbacks
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_achievements_menu, pattern="^achievement_menu$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_achievement_stats, pattern="^achievement_stats$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_achievement_list, pattern="^achievement_list$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_motivation_messages, pattern="^motivation_messages$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_weekly_summary, pattern="^weekly_summary$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_mark_messages_read, pattern="^mark_messages_read$"))
            
            # League-specific achievement callbacks
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_league_achievement_stats, pattern="^league_achievement_stats$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_league_achievement_list, pattern="^league_achievement_list$"))
            self.application.add_handler(CallbackQueryHandler(self.achievement_handlers.handle_community_motivation_messages, pattern="^community_motivation_messages$"))
            self.application.add_handler(CallbackQueryHandler(self._handle_community_achievements_league, pattern=r"^com_achievements_league_\d+$"))

            # Reminder tick job
            if self.application.job_queue is not None:
                self.application.job_queue.run_repeating(self._reminder_tick, interval=60, first=5)
                
                # Schedule daily motivational messages
                self.scheduled_message_service.schedule_daily_messages(self.application)
            else:
                self.logger.warning("JobQueue not available. Install PTB with job-queue extra to enable reminders.")

            self.logger.info("✅ All handlers set up successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to set up handlers: {e}")
            raise

    async def _handle_noop(self, update, context):
        try:
            await update.callback_query.answer()
        except Exception:
            pass

    async def _handle_book_start(self, update, context):
        query = update.callback_query
        await query.answer()
        book_id = int(query.data.split('_')[-1])
        user_id = query.from_user.id
        started = self.book_service.start_reading(user_id, book_id)
        
        # Context-aware navigation buttons
        league_id = context.user_data.get('current_league_id')
        is_community_mode = context.user_data.get('community_mode', False)
        
        if league_id or is_community_mode:
            # User is in community mode
            back_button = InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
            more_books_button = InlineKeyboardButton("📚 More Books", callback_data="com_browse")
            # Ensure community mode flag is preserved
            context.user_data['community_mode'] = True
        else:
            # User is in individual mode
            back_button = InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")
            more_books_button = InlineKeyboardButton("📚 More Books", callback_data="ind_books")
        
        if started:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{book_id}"), more_books_button],
                [back_button],
            ])
            await query.edit_message_text("✅ Started reading. What next?", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{book_id}")],
                [back_button],
            ])
            await query.edit_message_text("ℹ️ You're already reading this book.", reply_markup=keyboard)

    async def _handle_progress_select_book(self, update, context):
        query = update.callback_query
        await query.answer()
        book_id = int(query.data.split('_')[-1])
        context.user_data['current_book_id'] = book_id
        goal = self.book_service.get_user_daily_goal(query.from_user.id)
        
        # Context-aware navigation button
        league_id = context.user_data.get('current_league_id')
        is_community_mode = context.user_data.get('community_mode', False)
        
        if league_id or is_community_mode:
            # User is in community mode
            back_button = InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
            # Ensure community mode flag is preserved
            context.user_data['community_mode'] = True
        else:
            # User is in individual mode
            back_button = InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"➕ +{goal}", callback_data=f"progress_add_{goal}"), InlineKeyboardButton("➕ +5", callback_data="progress_add_5"), InlineKeyboardButton("➕ +10", callback_data="progress_add_10")],
            [InlineKeyboardButton("➖", callback_data="progress_add_-1"), InlineKeyboardButton(f"{goal}", callback_data="noop"), InlineKeyboardButton("➕", callback_data="progress_add_1")],
            [InlineKeyboardButton("Submit", callback_data="progress_submit"), back_button],
        ])
        context.user_data['adjust_amount'] = goal
        await query.edit_message_text("Choose quick add, adjust counter, or enter pages (number):", reply_markup=keyboard)

    async def _handle_progress_quick_add(self, update, context):
        query = update.callback_query
        await query.answer()
        amt_str = query.data.split('_')[-1]
        self.logger.debug(f"progress quick add pressed: {amt_str}")
        if amt_str == '1' or amt_str == '-1':
            # adjust counter
            delta = 1 if amt_str == '1' else -1
            current = int(context.user_data.get('adjust_amount', self.book_service.get_user_daily_goal(query.from_user.id)))
            new_val = max(0, current + delta)
            context.user_data['adjust_amount'] = new_val
            # rebuild keyboard with updated center - context-aware navigation
            league_id = context.user_data.get('current_league_id')
            is_community_mode = context.user_data.get('community_mode', False)
            
            if league_id or is_community_mode:
                # User is in community mode
                back_button = InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
                # Ensure community mode flag is preserved
                context.user_data['community_mode'] = True
            else:
                # User is in individual mode
                back_button = InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"➕ +{self.book_service.get_user_daily_goal(query.from_user.id)}", callback_data=f"progress_add_{self.book_service.get_user_daily_goal(query.from_user.id)}"), InlineKeyboardButton("➕ +5", callback_data="progress_add_5"), InlineKeyboardButton("➕ +10", callback_data="progress_add_10")],
                [InlineKeyboardButton("➖", callback_data="progress_add_-1"), InlineKeyboardButton(f"{new_val}", callback_data="noop"), InlineKeyboardButton("➕", callback_data="progress_add_1")],
                [InlineKeyboardButton("Submit", callback_data="progress_submit"), back_button],
            ])
            await query.edit_message_reply_markup(reply_markup=kb)
            return
        try:
            amt = int(amt_str)
        except Exception:
            await query.edit_message_text("Invalid amount.")
            return
        book_id = context.user_data.get('current_book_id')
        if not book_id:
            await query.edit_message_text("No book selected. Use /progress.")
            return
        user_id = query.from_user.id
        result = self.book_service.update_progress(user_id, book_id, amt)
        if 'error' in result:
            await query.edit_message_text(f"❌ {result['error']}")
            return
        bar = self._progress_bar(result['progress_percent'])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats"), InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
        ])
        msg = (
            "📖 Progress Updated!\n\n"
            f"➕ Added: {amt} pages\n"
            f"📊 Total: {result['current_pages']}/{result['total_pages']} pages\n"
            f"{bar} {result['progress_percent']}%\n"
            f"📖 Remaining: {result['remaining_pages']} pages\n"
        )
        if result['is_completed']:
            msg += "\n🎉 Congratulations! You've completed this book! Share your achievement with friends!"
        await query.edit_message_text(msg, reply_markup=keyboard)

    async def _handle_progress_submit(self, update, context):
        query = update.callback_query
        await query.answer()
        amt = int(context.user_data.get('adjust_amount', 0))
        self.logger.debug(f"progress submit pressed: {amt}")
        if amt <= 0:
            await query.edit_message_text("Please increase the amount above 0, then press Submit.")
            return
        book_id = context.user_data.get('current_book_id')
        if not book_id:
            await query.edit_message_text("No book selected. Use /progress.")
            return
        user_id = query.from_user.id
        result = self.book_service.update_progress(user_id, book_id, amt)
        if 'error' in result:
            await query.edit_message_text(f"❌ {result['error']}")
            return
        
        # 🎮 GAMIFICATION INTEGRATION: Update achievements and send motivation
        new_achievements = self.achievement_service.update_reading_progress(user_id, amt, book_id)
        
        # Check for league-specific achievements if in community mode
        league_id = context.user_data.get('current_league_id')
        if league_id:
            league_achievements = self.achievement_service.check_league_achievements(user_id, league_id, amt)
            new_achievements.extend(league_achievements)
            
            # Send league-specific motivation messages
            for achievement in league_achievements:
                self.motivation_service.send_league_achievement_celebration(user_id, achievement, league_id)
        
        # Send achievement celebration notifications
        achievement_messages = []
        for achievement in new_achievements:
            if 'streak' in achievement.type:
                # Send streak milestone notification
                streak_days = achievement.metadata.get('streak', 0) if achievement.metadata else 0
                message = self.motivation_service.send_streak_milestone_notification(user_id, streak_days)
                if message:
                    achievement_messages.append(message)
            else:
                # Send regular achievement celebration
                message = self.motivation_service.send_achievement_celebration(user_id, achievement)
                if message:
                    achievement_messages.append(message)
        
        # Check for level up and send notification
        stats = self.achievement_service.get_user_stats(user_id)
        if stats and stats.level > 1:
            # Check if user leveled up (this would need to be tracked in the achievement service)
            # For now, we'll send a general progress celebration
            pass
        
        # Send progress celebration
        book_title = result.get('book_title', 'Current Book')
        progress_message = self.motivation_service.send_progress_celebration(user_id, amt, book_title)
        
        # Send achievement messages to user
        for message in achievement_messages:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                self.logger.error(f"Failed to send achievement message to user {user_id}: {e}")
        
        # Send progress celebration message if available
        if progress_message:
            try:
                await context.bot.send_message(chat_id=user_id, text=progress_message)
            except Exception as e:
                self.logger.error(f"Failed to send progress message to user {user_id}: {e}")
        
        # Create enhanced progress bar with gamification
        bar = self.visual_service.create_progress_bar(result['current_pages'], result['total_pages'], 12)
        
        # Get user stats for enhanced display
        stats = self.achievement_service.get_user_stats(user_id)
        streak_display = self.visual_service.create_streak_display(stats.current_streak, stats.longest_streak) if stats else ""
        level_display = self.visual_service.create_level_display(stats.level, stats.xp) if stats else ""
        
        # Determine navigation buttons based on context
        # Check if user came from community mode (has league context OR community mode flag)
        league_id = context.user_data.get('current_league_id')
        is_community_mode = context.user_data.get('community_mode', False)
        
        # Only show community mode navigation if user is actively in community mode
        # or has a specific league context
        if league_id is not None or is_community_mode:
            # User is in community mode
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 My Stats", callback_data="com_stats"), InlineKeyboardButton("🏆 Leaderboard", callback_data="com_leaderboard")],
                [InlineKeyboardButton("🏆 Achievements", callback_data="achievement_menu"), InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")],
            ])
        else:
            # User is in individual mode
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats"), InlineKeyboardButton("🏆 Achievements", callback_data="achievement_menu")],
                [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
            ])
        
        # Enhanced progress message with gamification
        msg = (
            "📖 Progress Updated!\n\n"
            f"➕ Added: {amt} pages\n"
            f"📊 Total: {result['current_pages']}/{result['total_pages']} pages\n"
            f"{bar} {result['progress_percent']}%\n"
            f"📖 Remaining: {result['remaining_pages']} pages\n"
        )
        
        # Add gamification elements
        if stats:
            msg += f"\n{streak_display}\n{level_display}\n"
        
        # Handle new achievements
        if new_achievements:
            msg += f"\n🎉 {len(new_achievements)} new achievement(s) unlocked!\n"
            for achievement in new_achievements:
                msg += f"🏆 {achievement.title}\n"
        
        if result['is_completed']:
            msg += "\n🎉 Congratulations! You've completed this book! Share your achievement with friends!"
        
        await query.edit_message_text(msg, reply_markup=keyboard)

    async def _handle_progress_number(self, update, context):
        try:
            pages = int(update.message.text)
        except Exception:
            return
        
        # Check if we're in league creation flow
        if context.user_data.get('creating_league'):
            # Route to league creation handlers
            await self.user_handlers._handle_league_creation_text(update, context)
            return
        
        # Check if we're in add book flow
        if context.user_data.get('add_book_step') == 'pages':
            # Route to add book handler
            await self.user_handlers.handle_registration_text(update, context)
            return
        
        book_id = context.user_data.get('current_book_id')
        if not book_id:
            return
        user_id = update.effective_user.id
        result = self.book_service.update_progress(user_id, book_id, pages)
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return

        # Gamification: mirror submit flow for typed numbers
        new_achievements = self.achievement_service.update_reading_progress(user_id, pages, book_id)

        # League-specific achievements if in community context
        league_id = context.user_data.get('current_league_id')
        if league_id:
            league_achievements = self.achievement_service.check_league_achievements(user_id, league_id, pages)
            new_achievements.extend(league_achievements)
            for achievement in league_achievements:
                self.motivation_service.send_league_achievement_celebration(user_id, achievement, league_id)

        # Build and send achievement notifications
        achievement_messages = []
        for achievement in new_achievements:
            if 'streak' in achievement.type:
                streak_days = achievement.metadata.get('streak', 0) if achievement.metadata else 0
                message = self.motivation_service.send_streak_milestone_notification(user_id, streak_days)
                if message:
                    achievement_messages.append(message)
            else:
                message = self.motivation_service.send_achievement_celebration(user_id, achievement)
                if message:
                    achievement_messages.append(message)

        # Progress celebration
        book_title = result.get('book_title', 'Current Book')
        progress_message = self.motivation_service.send_progress_celebration(user_id, pages, book_title)
        for message in achievement_messages:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
            except Exception:
                pass
        if progress_message:
            try:
                await context.bot.send_message(chat_id=user_id, text=progress_message)
            except Exception:
                pass

        # Context-aware navigation
        is_community_mode = context.user_data.get('community_mode', False)
        if league_id is not None or is_community_mode:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 My Stats", callback_data="com_stats"), InlineKeyboardButton("🏆 Leaderboard", callback_data="com_leaderboard")],
                [InlineKeyboardButton("🏆 Achievements", callback_data="achievement_menu"), InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")],
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats"), InlineKeyboardButton("🏆 Achievements", callback_data="achievement_menu")],
                [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
            ])

        bar = self._progress_bar(result['progress_percent'])
        stats = self.achievement_service.get_user_stats(user_id)
        streak_display = self.visual_service.create_streak_display(stats.current_streak, stats.longest_streak) if stats else ""
        level_display = self.visual_service.create_level_display(stats.level, stats.xp) if stats else ""

        msg = (
            "📖 Progress Updated!\n\n"
            f"📚 Pages read today: {pages}\n"
            f"📊 Total: {result['current_pages']}/{result['total_pages']} pages\n"
            f"{bar} {result['progress_percent']}%\n"
            f"📖 Remaining: {result['remaining_pages']} pages\n"
        )
        if stats:
            msg += f"\n{streak_display}\n{level_display}\n"
        if new_achievements:
            msg += f"\n🎉 {len(new_achievements)} new achievement(s) unlocked!\n"
            for achievement in new_achievements:
                msg += f"🏆 {achievement.title}\n"
        if result['is_completed']:
            msg += "\n🎉 Congratulations! You've completed this book! Share your achievement with friends!"
        await update.message.reply_text(msg, reply_markup=keyboard)

    def _progress_bar(self, percent: float, width: int = 10) -> str:
        filled = int(round((percent / 100.0) * width))
        return "▓" * filled + "░" * (width - filled)

    async def _handle_community_achievements_league(self, update, context):
        """Handle community achievements for a specific league."""
        query = update.callback_query
        await query.answer()
        
        # Extract league ID from callback data
        league_id = int(query.data.split('_')[-1])
        
        # Set league and community mode context
        context.user_data['current_league_id'] = league_id
        context.user_data['community_mode'] = True
        
        # Show league-specific achievements
        await self.achievement_handlers._handle_community_achievements_menu(query, context, league_id)

    async def _reminder_tick(self, context):
        try:
            active = self.reminder_service.list_active_reminders()
            if not active:
                return
            # naive local time check (HH:MM)
            from datetime import datetime
            now_hhmm = datetime.now().strftime("%H:%M")
            for r in active:
                rt = str(r['reminder_time'])[:5]
                if rt == now_hhmm:
                    chat_id = r['user_id']
                    try:
                        await context.bot.send_message(chat_id=chat_id, text="⏰ Have you read your pages today? Use /progress to update.")
                    except Exception:
                        pass
        except Exception as e:
            self.logger.error(f"Reminder tick error: {e}")

    def start(self):
        try:
            self.logger.info("🚀 Starting Read & Revive Bot...")
            self._setup_handlers()
            self.logger.info("📡 Starting bot polling...")
            self.application.run_polling()
        except Exception as e:
            self.logger.error(f"❌ Failed to start bot: {e}")
            raise

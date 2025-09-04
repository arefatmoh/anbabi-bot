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
from src.services.book_service import BookService
from src.services.reminder_service import ReminderService
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
        self.book_service = BookService()
        self.reminder_service = ReminderService()
        self._init_handlers()
        self._init_application()
    
    def _init_handlers(self):
        try:
            self.user_handlers = UserHandlers()
            self.admin_handlers = AdminHandlers()
            self.admin_league_handlers = AdminLeagueHandlers(get_league_service())
            self.conversation_handlers = ConversationHandlers()
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

            # Goal inline callbacks
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_goal_inline, pattern=r"^goal_(\d+|custom)$"))
            # Reminder inline callbacks
            self.application.add_handler(CallbackQueryHandler(self.user_handlers.handle_reminder_inline, pattern=r"^rem_(menu|time_\d{4}|disable|custom)$"))

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

            # Reminder tick job
            if self.application.job_queue is not None:
                self.application.job_queue.run_repeating(self._reminder_tick, interval=60, first=5)
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
        if started:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{book_id}"), InlineKeyboardButton("📚 More Books", callback_data="ind_books")],
                [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
            ])
            await query.edit_message_text("✅ Started reading. What next?", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{book_id}")],
                [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
            ])
            await query.edit_message_text("ℹ️ You're already reading this book.", reply_markup=keyboard)

    async def _handle_progress_select_book(self, update, context):
        query = update.callback_query
        await query.answer()
        book_id = int(query.data.split('_')[-1])
        context.user_data['current_book_id'] = book_id
        goal = self.book_service.get_user_daily_goal(query.from_user.id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"➕ +{goal}", callback_data=f"progress_add_{goal}"), InlineKeyboardButton("➕ +5", callback_data="progress_add_5"), InlineKeyboardButton("➕ +10", callback_data="progress_add_10")],
            [InlineKeyboardButton("➖", callback_data="progress_add_-1"), InlineKeyboardButton(f"{goal}", callback_data="noop"), InlineKeyboardButton("➕", callback_data="progress_add_1")],
            [InlineKeyboardButton("Submit", callback_data="progress_submit"), InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
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
            # rebuild keyboard with updated center
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"➕ +{self.book_service.get_user_daily_goal(query.from_user.id)}", callback_data=f"progress_add_{self.book_service.get_user_daily_goal(query.from_user.id)}"), InlineKeyboardButton("➕ +5", callback_data="progress_add_5"), InlineKeyboardButton("➕ +10", callback_data="progress_add_10")],
                [InlineKeyboardButton("➖", callback_data="progress_add_-1"), InlineKeyboardButton(f"{new_val}", callback_data="noop"), InlineKeyboardButton("➕", callback_data="progress_add_1")],
                [InlineKeyboardButton("Submit", callback_data="progress_submit"), InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
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
        
        book_id = context.user_data.get('current_book_id')
        if not book_id:
            return
        user_id = update.effective_user.id
        result = self.book_service.update_progress(user_id, book_id, pages)
        if 'error' in result:
            await update.message.reply_text(f"❌ {result['error']}")
            return
        bar = self._progress_bar(result['progress_percent'])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats"), InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
        ])
        msg = (
            "📖 Progress Updated!\n\n"
            f"📚 Pages read today: {result['pages_read_today']}\n"
            f"📊 Total: {result['current_pages']}/{result['total_pages']} pages\n"
            f"{bar} {result['progress_percent']}%\n"
            f"📖 Remaining: {result['remaining_pages']} pages\n"
        )
        if result['is_completed']:
            msg += "\n🎉 Congratulations! You've completed this book! Share your achievement with friends!"
        await update.message.reply_text(msg, reply_markup=keyboard)

    def _progress_bar(self, percent: float, width: int = 10) -> str:
        filled = int(round((percent / 100.0) * width))
        return "▓" * filled + "░" * (width - filled)

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

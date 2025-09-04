"""
User command handlers.

This module contains all the user command handlers for the bot.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from src.config.messages import HELP_MESSAGE, WELCOME_MESSAGE, MODE_SELECTION_MESSAGE, REGISTRATION_MESSAGE, PROGRESS_UPDATE_MESSAGE
from src.services.factory import get_league_service
from src.core.handlers.league_handlers import LeagueHandlers
from src.services.book_service import BookService
from src.services.reminder_service import ReminderService
from src.database.database import db_manager


class UserHandlers:
    """Handles all user commands and interactions."""
    
    def __init__(self):
        """Initialize user handlers."""
        self.logger = logging.getLogger(__name__)
        self._league_handlers = None
        self.book_service = BookService()
        self.reminder_service = ReminderService()
    
    @property
    def league_handlers(self) -> LeagueHandlers:
        if self._league_handlers is None:
            self._league_handlers = LeagueHandlers(get_league_service())
        return self._league_handlers
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start: greet and start registration if new; else welcome back with mode buttons."""
        user_id = update.effective_user.id
        full_name_db = None
        nickname_db = None
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT full_name, username FROM users WHERE user_id = ?", (user_id,))
                row = cur.fetchone()
                if row:
                    full_name_db = row[0]
                    nickname_db = row[1]
        except Exception as e:
            self.logger.error(f"DB read error: {e}")
        if full_name_db:
            display_name = nickname_db or full_name_db
            greet = f"Welcome back, {display_name}!"
            await update.message.reply_text(greet)
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🆕 Individual Mode", callback_data="mode_individual"),
                    InlineKeyboardButton("👥 Community Mode", callback_data="mode_community"),
                ]
            ])
            await update.message.reply_text(MODE_SELECTION_MESSAGE, reply_markup=keyboard)
            return
        # New user: begin minimal registration
        await update.message.reply_text(WELCOME_MESSAGE)
        await update.message.reply_text("👋 What's your full name?")
        context.user_data['reg_step'] = 'name'
    
    async def handle_registration_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unified registration handler for name and nickname steps."""
        step = context.user_data.get('reg_step')
        if step == 'name':
            name = update.message.text.strip()
            if len(name) < 2:
                await update.message.reply_text("Please provide a valid name.")
                return
            context.user_data['reg_name'] = name
            context.user_data['reg_step'] = 'nickname'
            await update.message.reply_text("Great! Do you have a nickname? If not, type '-' ")
            return
        if step == 'nickname':
            nickname = update.message.text.strip()
            if nickname == '-':
                nickname = ''
            try:
                with db_manager.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT OR REPLACE INTO users (user_id, username, full_name, city, contact)
                        VALUES (?, ?, ?, COALESCE(city,''), COALESCE(contact,''))
                        """,
                        (
                            update.effective_user.id,
                            nickname or (update.effective_user.username or ''),
                            context.user_data.get('reg_name', ''),
                        ),
                    )
                    conn.commit()
            except Exception as e:
                self.logger.error(f"User save error: {e}")
            await self._show_mode_menu(update)
            context.user_data.pop('reg_step', None)
            context.user_data.pop('reg_name', None)
            return
        # If no registration step, ignore
        return
    
    async def handle_mode_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        mode = query.data.split('_')[-1]
        if mode == 'individual':
            await self._show_individual_menu(query)
        else:
            await self._show_community_menu(query)
    
    async def _show_mode_menu(self, update: Update):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🆕 Individual Mode", callback_data="mode_individual"),
                InlineKeyboardButton("👥 Community Mode", callback_data="mode_community"),
            ]
        ])
        if update.message:
            await update.message.reply_text(MODE_SELECTION_MESSAGE, reply_markup=keyboard)
        else:
            await update.edit_message_text(MODE_SELECTION_MESSAGE, reply_markup=keyboard)  # type: ignore
    
    async def _show_individual_menu(self, query):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Start Reading", callback_data="ind_books"), InlineKeyboardButton("📖 Update Progress", callback_data="ind_progress")],
            [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats"), InlineKeyboardButton("⏰ Reminders", callback_data="ind_reminder")],
        ])
        await query.edit_message_text("Individual Mode — choose an option:", reply_markup=keyboard)
    
    async def _show_community_menu(self, query):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Browse Leagues", callback_data="com_browse"), InlineKeyboardButton("👥 My Leagues", callback_data="com_my")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="com_leaderboard")],
        ])
        await query.edit_message_text("Community Mode — choose an option:", reply_markup=keyboard)
    
    async def handle_individual_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        action = q.data
        if action == 'ind_books':
            # reuse books flow
            await q.edit_message_text("📚 Featured Books:")
            class Dummy: pass
            d = Dummy(); d.message = q.message  # type: ignore
            await self.books_command(d, context)  # reuse sending
        elif action == 'ind_progress':
            await q.edit_message_text("📖 Update your reading progress:")
            class Dummy: pass
            d = Dummy(); d.message = q.message  # type: ignore
            d.effective_user = q.from_user  # type: ignore
            await self.progress_command(d, context)
        elif action == 'ind_stats':
            class Dummy: pass
            d = Dummy(); d.message = q.message  # type: ignore
            d.effective_user = q.from_user  # type: ignore
            await self.stats_command(d, context)
        elif action == 'ind_reminder':
            class Dummy: pass
            d = Dummy(); d.message = q.message  # type: ignore
            await self.reminder_command(d, context)
    
    async def handle_community_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        action = q.data
        if action == 'com_browse':
            await self.league_handlers.handle_league_browse(update, context)
        elif action == 'com_my':
            await self.league_handlers.handle_league_my_leagues(update, context)
        elif action == 'com_leaderboard':
            await self.league_handlers.handle_leaderboard_command(q, context)  # type: ignore
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(HELP_MESSAGE)
    
    async def books_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        books = self.book_service.get_featured_books()
        if not books:
            await update.message.reply_text("No featured books available right now.")
            return
        keyboard = []
        for b in books:
            keyboard.append([
                InlineKeyboardButton(
                    f"{b['title']} - {b['author']} ({b['total_pages']}p)",
                    callback_data=f"book_start_{b['book_id']}"
                )
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📚 Featured Books (tap to start):", reply_markup=reply_markup)
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        active = self.book_service.get_active_books(user_id)
        if not active:
            await update.message.reply_text("You have no active books. Use /books to start one.")
            return
        if len(active) == 1:
            context.user_data['current_book_id'] = active[0]['book_id']
            await update.message.reply_text(PROGRESS_UPDATE_MESSAGE)
            return
        keyboard = []
        for book in active:
            keyboard.append([
                InlineKeyboardButton(
                    f"{book['title']} ({book['pages_read']}/{book['total_pages']})",
                    callback_data=f"progress_select_{book['book_id']}"
                )
            ])
        await update.message.reply_text("Select a book to update progress:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        stats = self.book_service.get_user_stats(user_id)
        msg = (
            "📊 Your Stats\n\n"
            f"📚 Books Started: {stats['total_books']}\n"
            f"🏁 Books Completed: {stats['completed_books']}\n"
            f"📖 Total Pages Read: {stats['total_pages']}\n"
        )
        await update.message.reply_text(msg)
    
    async def league_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.league_handlers.handle_league_menu(update, context)
    
    async def reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Reminders:\n/reminder_set HH:MM — set daily reminder\n/reminder_view — show reminder\n/reminder_remove — disable reminder"
        )
    
    async def reminder_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /reminder_set HH:MM (24h)")
            return
        t = self.reminder_service.parse_time(args[0])
        if not t:
            await update.message.reply_text("Invalid time format. Use HH:MM (24h)")
            return
        self.reminder_service.set_reminder(update.effective_user.id, t, "daily")
        await update.message.reply_text(f"✅ Reminder set for {args[0]} daily.")
    
    async def reminder_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        r = self.reminder_service.get_reminder(update.effective_user.id)
        if not r or not r["is_active"]:
            await update.message.reply_text("No active reminder.")
            return
        await update.message.reply_text(
            f"Reminder: {str(r['reminder_time'])[:5]} ({r['frequency']})"
        )
    
    async def reminder_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ok = self.reminder_service.remove_reminder(update.effective_user.id)
        if ok:
            await update.message.reply_text("✅ Reminder disabled.")
        else:
            await update.message.reply_text("No reminder to disable.")
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command."""
        await update.message.reply_text("Profile feature is coming next.")

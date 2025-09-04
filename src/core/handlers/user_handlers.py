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
        # Handle custom reminder time entry (12-hour with AM/PM also accepted)
        if context.user_data.get('awaiting_reminder_time'):
            t = self.reminder_service.parse_time(update.message.text.strip())
            if not t:
                await update.message.reply_text("Invalid time. Use h:MM AM/PM (e.g., 9:00 PM) or 24h HH:MM")
                return
            self.reminder_service.set_reminder(update.effective_user.id, t, "daily")
            context.user_data.pop('awaiting_reminder_time', None)
            pretty = self.reminder_service.format_time_12h(t)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="mode_individual")]])
            await update.message.reply_text(f"✅ Reminder set for {pretty} (Ethiopia time).", reply_markup=kb)
            return
        
        # Handle step-by-step custom book flow
        add_step = context.user_data.get('add_book_step')
        if add_step:
            if add_step == 'title':
                title = update.message.text.strip()
                if len(title) < 2:
                    await update.message.reply_text("Please provide a valid title.")
                    return
                context.user_data['add_book']['title'] = title
                context.user_data['add_book_step'] = 'author'
                await update.message.reply_text("✍️ Who is the author?")
                return
            if add_step == 'author':
                author = update.message.text.strip()
                if len(author) < 2:
                    await update.message.reply_text("Please provide a valid author name.")
                    return
                context.user_data['add_book']['author'] = author
                context.user_data['add_book_step'] = 'pages'
                await update.message.reply_text("📄 How many total pages does it have? (number)")
                return
            if add_step == 'pages':
                try:
                    pages = int(update.message.text.strip())
                    if pages <= 0:
                        raise ValueError()
                except Exception:
                    await update.message.reply_text("Total pages must be a positive number.")
                    return
                data = context.user_data.get('add_book', {})
                book_id = self.book_service.add_custom_book_and_start(
                    update.effective_user.id,
                    data.get('title', ''),
                    data.get('author', ''),
                    pages,
                )
                # Clear state
                context.user_data.pop('add_book_step', None)
                context.user_data.pop('add_book', None)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{book_id}")],
                    [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")],
                ])
                await update.message.reply_text("✅ Your book has been added and started. What next?", reply_markup=keyboard)
                return
        
        # Custom goal input
        if context.user_data.get('awaiting_goal_custom'):
            try:
                val = int(update.message.text.strip())
                if val <= 0:
                    raise ValueError()
            except Exception:
                await update.message.reply_text("Please enter a positive number.")
                return
            self.book_service.set_user_daily_goal(update.effective_user.id, val)
            context.user_data.pop('awaiting_goal_custom', None)
            await update.message.reply_text(f"✅ Daily goal set to {val} pages/day.")
            return
        
        # Registration flow
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
                        INSERT INTO users (user_id, username, full_name, city, contact)
                        VALUES (?, ?, ?, '', '')
                        ON CONFLICT(user_id) DO UPDATE SET
                            username = excluded.username,
                            full_name = excluded.full_name
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
        goal = self.book_service.get_user_daily_goal(query.from_user.id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Start Reading", callback_data="ind_books"), InlineKeyboardButton("➕ Add My Book", callback_data="ind_add_book")],
            [InlineKeyboardButton("📖 Update Progress", callback_data="ind_progress")],
            [InlineKeyboardButton(f"🎯 Daily Goal: {goal}p", callback_data="ind_set_goal"), InlineKeyboardButton("⏰ Reminders", callback_data="ind_reminder")],
            [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats")],
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
        elif action == 'ind_add_book':
            # Start step-by-step add flow
            context.user_data['add_book'] = {}
            context.user_data['add_book_step'] = 'title'
            await q.edit_message_text("📘 What's the book title?")
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
        elif action == 'ind_set_goal':
            goal = self.book_service.get_user_daily_goal(q.from_user.id)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("10", callback_data="goal_10"), InlineKeyboardButton("15", callback_data="goal_15"), InlineKeyboardButton("20", callback_data="goal_20")],
                [InlineKeyboardButton("25", callback_data="goal_25"), InlineKeyboardButton("30", callback_data="goal_30"), InlineKeyboardButton("Custom", callback_data="goal_custom")],
                [InlineKeyboardButton("Back", callback_data="mode_individual")],
            ])
            await q.edit_message_text(f"Current goal: {goal} pages/day. Choose a new goal:", reply_markup=kb)
        elif action.startswith('goal_'):
            # handled by reminder inline elsewhere; placeholder
            pass
    
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
        """Show reminder inline menu with common times and options (12-hour, Ethiopia time)."""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("8:00 PM", callback_data="rem_time_2000"), InlineKeyboardButton("9:00 PM", callback_data="rem_time_2100"), InlineKeyboardButton("9:30 PM", callback_data="rem_time_2130")],
            [InlineKeyboardButton("Custom Time", callback_data="rem_custom"), InlineKeyboardButton("Disable", callback_data="rem_disable")],
        ])
        await update.message.reply_text("Reminders — choose a time (Ethiopia time, GMT+3):", reply_markup=kb)
    
    async def handle_reminder_inline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline reminder callbacks."""
        q = update.callback_query
        await q.answer()
        data = q.data
        if data == 'rem_menu':
            return await self.reminder_command(q, context)  # type: ignore
        if data.startswith('rem_time_'):
            hhmm = data.split('_')[-1]
            hh = hhmm[:2]; mm = hhmm[2:]
            t = self.reminder_service.parse_time(f"{hh}:{mm}")
            if not t:
                await q.edit_message_text("Invalid time.")
                return
            self.reminder_service.set_reminder(q.from_user.id, t, "daily")
            pretty = self.reminder_service.format_time_12h(t)
            await q.edit_message_text(f"✅ Reminder set for {pretty} (Ethiopia time).")
            return
        if data == 'rem_disable':
            ok = self.reminder_service.remove_reminder(q.from_user.id)
            await q.edit_message_text("✅ Reminder disabled." if ok else "No reminder to disable.")
            return
        if data == 'rem_custom':
            context.user_data['awaiting_reminder_time'] = True
            await q.edit_message_text("Send a time like 9:00 PM (or 21:00). Ethiopia time.")
            return
    
    async def reminder_set(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /reminder_set 9:00 PM (or 21:00)")
            return
        t = self.reminder_service.parse_time(" ".join(args))
        if not t:
            await update.message.reply_text("Invalid time format. Use h:MM AM/PM or 24h HH:MM")
            return
        self.reminder_service.set_reminder(update.effective_user.id, t, "daily")
        pretty = self.reminder_service.format_time_12h(t)
        await update.message.reply_text(f"✅ Reminder set for {pretty} (Ethiopia time).")
    
    async def reminder_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        r = self.reminder_service.get_reminder(update.effective_user.id)
        if not r or not r["is_active"]:
            await update.message.reply_text("No active reminder.")
            return
        # r['reminder_time'] is HH:MM:SS string — parse and format 12h
        t = self.reminder_service.parse_time(str(r['reminder_time'])[:5])
        pretty = self.reminder_service.format_time_12h(t) if t else str(r['reminder_time'])[:5]
        await update.message.reply_text(
            f"Reminder: {pretty} ({r['frequency']}) — Ethiopia time"
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

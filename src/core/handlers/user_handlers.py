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
    
    PAGE_SIZE = 6

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
        # Handle admin book addition flow
        if context.user_data.get('adding_book'):
            from src.core.handlers.admin_handlers import AdminHandlers
            admin_handlers = AdminHandlers()
            await admin_handlers.handle_book_addition(update, context)
            return
        
        # Handle league creation flow
        if context.user_data.get('creating_league'):
            await self._handle_league_creation_text(update, context)
            return
        
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
        
        # Handle community reminder custom time entry
        if context.user_data.get('setting_community_reminder'):
            t = self.reminder_service.parse_time(update.message.text.strip())
            if not t:
                await update.message.reply_text("Invalid time. Use h:MM AM/PM (e.g., 9:00 PM) or 24h HH:MM")
                return
            
            league_id = context.user_data.get('community_reminder_league_id')
            if league_id:
                result = self.reminder_service.set_reminder(update.effective_user.id, t.hour, t.minute, league_id=league_id)
                if result['success']:
                    # Get league info for confirmation
                    league = self.league_handlers.league_service.get_league_by_id(league_id)
                    league_name = league.name if league else f"League {league_id}"
                    
                    pretty = self.reminder_service.format_time_12h(t)
                    message = f"✅ <b>Community Reminder Set!</b>\n\n"
                    message += f"⏰ <b>Time:</b> {pretty} (Ethiopia time)\n"
                    message += f"📚 <b>League:</b> {league_name}\n"
                    message += f"🎯 <b>Daily Goal:</b> {league.daily_goal if league else 'N/A'} pages\n\n"
                    message += "You'll receive daily reminders to read your league book!"
                    
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Back to Reminders", callback_data="com_reminder")],
                        [InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")]
                    ])
                    
                    await update.message.reply_text(message, reply_markup=keyboard)
                else:
                    await update.message.reply_text(f"❌ {result['error']}")
            else:
                await update.message.reply_text("❌ Error: League ID not found.")
            
            # Clean up context
            context.user_data.pop('setting_community_reminder', None)
            context.user_data.pop('community_reminder_league_id', None)
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
            # Show individual menu next
            class Dummy: pass
            d = Dummy(); d.edit_message_text = update.message.reply_text  # type: ignore
            d.from_user = update.effective_user  # type: ignore
            await self._show_individual_menu(d)
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
            # Clear community mode context
            context.user_data.pop('current_league_id', None)
            context.user_data.pop('community_mode', None)
            await self._show_individual_menu(query)
        else:
            # Set community mode context
            context.user_data['community_mode'] = True
            # Preserve league context - don't clear current_league_id
            # This allows users to maintain their league context when navigating
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
            [InlineKeyboardButton("📚 My Books", callback_data="ind_my_books"), InlineKeyboardButton("➕ Add My Book", callback_data="ind_add_book")],
            [InlineKeyboardButton("📖 Update Progress", callback_data="ind_progress")],
            [InlineKeyboardButton(f"🎯 Daily Goal: {goal}p", callback_data="ind_set_goal"), InlineKeyboardButton("⏰ Reminders", callback_data="ind_reminder")],
            [InlineKeyboardButton("📊 My Stats", callback_data="ind_stats"), InlineKeyboardButton("🏆 Achievements", callback_data="achievement_menu")],
        ])
        await query.edit_message_text("Individual Mode — choose an option:", reply_markup=keyboard)
    
    async def _show_community_menu(self, query):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Browse Leagues", callback_data="com_browse"), InlineKeyboardButton("👥 My Leagues", callback_data="com_my")],
            [InlineKeyboardButton("📖 Update Progress", callback_data="com_progress"), InlineKeyboardButton("🏆 Leaderboard", callback_data="com_leaderboard")],
            [InlineKeyboardButton("⏰ Reminders", callback_data="com_reminder"), InlineKeyboardButton("📊 My Stats", callback_data="com_stats")],
            [InlineKeyboardButton("🏆 Achievements", callback_data="achievement_menu")],
        ])
        await query.edit_message_text("Community Mode — choose an option:", reply_markup=keyboard)
    
    async def handle_individual_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        action = q.data
        if action == 'ind_my_books':
            await self._show_my_books(q, context, page=0)
        elif action == 'ind_add_book':
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
            pass
    
    async def handle_community_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        action = q.data
        
        # Ensure community mode context is set for all community actions
        context.user_data['community_mode'] = True
        if action == 'com_browse':
            await self.league_handlers.handle_league_browse(update, context)
        elif action == 'com_my':
            await self.league_handlers.handle_league_my_leagues(update, context)
        elif action == 'com_progress':
            await self._handle_community_progress(q, context)
        elif action == 'com_leaderboard':
            await self.league_handlers.handle_leaderboard_command(update, context)
        elif action == 'com_reminder':
            await self._handle_community_reminder(q, context)
        elif action == 'com_stats':
            await self._handle_community_stats(q, context)
    
    async def _handle_community_progress(self, query, context):
        """Handle community progress update."""
        try:
            # Get user's leagues
            user_leagues = self.league_handlers.league_service.get_user_leagues(query.from_user.id)
            
            if not user_leagues:
                await query.edit_message_text(
                    "📖 <b>Community Progress</b>\n\n"
                    "You're not in any leagues yet. Join a league to start tracking community progress!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔎 Browse Leagues", callback_data="com_browse")],
                        [InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")]
                    ])
                )
                return
            
            # Show leagues for progress update
            keyboard = []
            for league in user_leagues:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📖 {league.name}",
                        callback_data=f"com_progress_league_{league.league_id}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")])
            
            await query.edit_message_text(
                "📖 <b>Community Progress Update</b>\n\n"
                "Choose a league to update your progress:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            self.logger.error(f"Error handling community progress: {e}")
            await query.edit_message_text("❌ Error loading community progress.")
    
    async def handle_community_progress_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle community progress update for a specific league."""
        try:
            query = update.callback_query
            await query.answer()
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Get league info
            league = self.league_handlers.league_service.league_repo.get_league_by_id(league_id)
            if not league:
                await query.edit_message_text("❌ League not found.")
                return
            
            # Check if user is a member of this league
            user_id = query.from_user.id
            is_member = self.league_handlers.league_service.league_repo.is_user_member(league_id, user_id)
            
            if not is_member:
                await query.edit_message_text(
                    "❌ You're not a member of this league.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
                    ]])
                )
                return
            
            # Get user's books for this league
            user_books = self.book_service.get_user_books_with_status(user_id)
            league_books = [book for book in user_books if book.get('book_id') == league.current_book_id]
            
            if not league_books:
                # User hasn't started reading the league book yet, start it automatically
                success = self.book_service.start_reading(user_id, league.current_book_id)
                if success:
                    # Get the book details from database
                    from src.database.database import db_manager
                    with db_manager.get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT title, author, total_pages FROM books WHERE book_id = ?",
                            (league.current_book_id,)
                        )
                        book_data = cur.fetchone()
                    
                    if book_data:
                        # Create a book object for the progress update
                        book = {
                            'book_id': league.current_book_id,
                            'title': book_data[0],
                            'author': book_data[1],
                            'total_pages': book_data[2],
                            'pages_read': 0,
                            'status': 'active'
                        }
                        league_books = [book]
                    else:
                        await query.edit_message_text(
                            f"❌ Error: League book not found.",
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
                            ]])
                        )
                        return
                else:
                    await query.edit_message_text(
                        f"❌ Error: Could not start reading the league book.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
                        ]])
                    )
                    return
            
            if not league_books:
                await query.edit_message_text(
                    f"❌ Error: Could not load league book information.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
                    ]])
                )
                return
            
            # Show progress update options for the league book
            book = league_books[0]
            progress_percent = (book['pages_read'] / book['total_pages']) * 100 if book['total_pages'] > 0 else 0
            
            # Set context data for progress submit handlers
            context.user_data['current_book_id'] = book['book_id']
            context.user_data['adjust_amount'] = league.daily_goal
            context.user_data['current_league_id'] = league_id
            context.user_data['community_mode'] = True  # Ensure community mode is set
            
            message = f"📖 <b>Progress Update: {league.name}</b>\n\n"
            message += f"📚 <b>Book:</b> {book['title']}\n"
            message += f"👤 <b>Author:</b> {book['author']}\n"
            message += f"📊 <b>Current Progress:</b> {book['pages_read']}/{book['total_pages']} pages ({progress_percent:.1f}%)\n"
            message += f"🎯 <b>Daily Goal:</b> {league.daily_goal} pages\n\n"
            message += "How many pages did you read today?"
            
            # Create progress update keyboard
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(f"+{league.daily_goal}", callback_data=f"progress_add_{league.daily_goal}"),
                    InlineKeyboardButton("+5", callback_data="progress_add_5"),
                    InlineKeyboardButton("+10", callback_data="progress_add_10")
                ],
                [
                    InlineKeyboardButton("[-]", callback_data="progress_add_-1"),
                    InlineKeyboardButton(f"[{league.daily_goal}]", callback_data="progress_counter"),
                    InlineKeyboardButton("[+]", callback_data="progress_add_1")
                ],
                [
                    InlineKeyboardButton("Submit", callback_data="progress_submit")
                ],
                [
                    InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")
                ]
            ])
            
            await query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error handling community progress league: {e}")
            await query.edit_message_text("❌ Error loading league progress update.")
    
    async def _handle_community_reminder(self, query, context):
        """Handle community reminders."""
        try:
            # Get user's leagues
            user_leagues = self.league_handlers.league_service.get_user_leagues(query.from_user.id)
            
            if not user_leagues:
                await query.edit_message_text(
                    "⏰ <b>Community Reminders</b>\n\n"
                    "You're not in any leagues yet. Join a league to set community reminders!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔎 Browse Leagues", callback_data="com_browse")],
                        [InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")]
                    ])
                )
                return
            
            # Show reminder options for leagues
            keyboard = []
            for league in user_leagues:
                keyboard.append([
                    InlineKeyboardButton(
                        f"⏰ {league.name}",
                        callback_data=f"com_reminder_league_{league.league_id}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")])
            
            await query.edit_message_text(
                "⏰ <b>Community Reminders</b>\n\n"
                "Choose a league to set reminders:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            self.logger.error(f"Error handling community reminders: {e}")
            await query.edit_message_text("❌ Error loading community reminders.")
    
    async def handle_community_reminder_league(self, update, context):
        """Handle community reminder league selection."""
        query = update.callback_query
        await query.answer()
        
        # Ensure community mode context is set
        context.user_data['community_mode'] = True
        
        try:
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Get league information
            league = self.league_handlers.league_service.get_league_by_id(league_id)
            if not league:
                await query.edit_message_text("❌ League not found.")
                return
            
            # Check if user is a member of this league
            user_id = query.from_user.id
            if not self.league_handlers.league_service.is_user_member(user_id, league_id):
                await query.edit_message_text("❌ You are not a member of this league.")
                return
            
            # Show reminder options for this league
            message = f"⏰ <b>Set Reminder for {league.name}</b>\n\n"
            message += f"📚 <b>Book:</b> {league.book_title}\n"
            message += f"🎯 <b>Daily Goal:</b> {league.daily_goal} pages\n\n"
            message += "Choose when you'd like to be reminded to read:"
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌅 Morning (8:00 AM)", callback_data=f"com_reminder_time_{league_id}_0800"),
                    InlineKeyboardButton("🌞 Afternoon (2:00 PM)", callback_data=f"com_reminder_time_{league_id}_1400")
                ],
                [
                    InlineKeyboardButton("🌆 Evening (6:00 PM)", callback_data=f"com_reminder_time_{league_id}_1800"),
                    InlineKeyboardButton("🌙 Night (9:00 PM)", callback_data=f"com_reminder_time_{league_id}_2100")
                ],
                [
                    InlineKeyboardButton("⏰ Custom Time", callback_data=f"com_reminder_custom_{league_id}")
                ],
                [
                    InlineKeyboardButton("🔕 Disable Reminder", callback_data=f"com_reminder_disable_{league_id}")
                ],
                [
                    InlineKeyboardButton("⬅️ Back to Reminders", callback_data="com_reminder")
                ]
            ])
            
            await query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error handling community reminder league: {e}")
            await query.edit_message_text("❌ Error loading league reminder options.")
    
    async def handle_community_reminder_time(self, update, context):
        """Handle community reminder time selection."""
        query = update.callback_query
        await query.answer()
        
        # Ensure community mode context is set
        context.user_data['community_mode'] = True
        
        try:
            # Extract league ID and time from callback data
            parts = query.data.split('_')
            league_id = int(parts[3])
            time_str = parts[4]  # Format: HHMM
            
            # Parse time
            hour = int(time_str[:2])
            minute = int(time_str[2:])
            
            # Set reminder for the league
            user_id = query.from_user.id
            result = self.reminder_service.set_reminder(user_id, hour, minute, league_id=league_id)
            
            if result['success']:
                # Get league info for confirmation
                league = self.league_handlers.league_service.get_league_by_id(league_id)
                league_name = league.name if league else f"League {league_id}"
                
                message = f"✅ <b>Reminder Set!</b>\n\n"
                message += f"⏰ <b>Time:</b> {hour:02d}:{minute:02d} (Ethiopia time)\n"
                message += f"📚 <b>League:</b> {league_name}\n"
                message += f"🎯 <b>Daily Goal:</b> {league.daily_goal if league else 'N/A'} pages\n\n"
                message += "You'll receive daily reminders to read your league book!"
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Reminders", callback_data="com_reminder")],
                    [InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")]
                ])
                
                await query.edit_message_text(message, reply_markup=keyboard)
            else:
                await query.edit_message_text(f"❌ {result['error']}")
                
        except Exception as e:
            self.logger.error(f"Error setting community reminder time: {e}")
            await query.edit_message_text("❌ Error setting reminder.")
    
    async def handle_community_reminder_custom(self, update, context):
        """Handle community reminder custom time input."""
        query = update.callback_query
        await query.answer()
        
        # Ensure community mode context is set
        context.user_data['community_mode'] = True
        
        try:
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Set context for custom time input
            context.user_data['setting_community_reminder'] = True
            context.user_data['community_reminder_league_id'] = league_id
            
            # Get league info
            league = self.league_handlers.league_service.get_league_by_id(league_id)
            league_name = league.name if league else f"League {league_id}"
            
            message = f"⏰ <b>Custom Reminder Time for {league_name}</b>\n\n"
            message += "Please enter your preferred reminder time in one of these formats:\n\n"
            message += "• <b>24-hour format:</b> 14:30 (2:30 PM)\n"
            message += "• <b>12-hour format:</b> 2:30 PM or 2:30pm\n\n"
            message += "⏰ <b>Note:</b> All times are in Ethiopia time (GMT+3)"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Reminders", callback_data="com_reminder")]
            ])
            
            await query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error handling community reminder custom: {e}")
            await query.edit_message_text("❌ Error setting up custom reminder.")
    
    async def handle_community_reminder_disable(self, update, context):
        """Handle community reminder disable."""
        query = update.callback_query
        await query.answer()
        
        # Ensure community mode context is set
        context.user_data['community_mode'] = True
        
        try:
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Disable reminder for the league
            user_id = query.from_user.id
            result = self.reminder_service.disable_reminder(user_id, league_id=league_id)
            
            if result['success']:
                # Get league info for confirmation
                league = self.league_handlers.league_service.get_league_by_id(league_id)
                league_name = league.name if league else f"League {league_id}"
                
                message = f"🔕 <b>Reminder Disabled</b>\n\n"
                message += f"📚 <b>League:</b> {league_name}\n\n"
                message += "You will no longer receive daily reminders for this league."
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Reminders", callback_data="com_reminder")],
                    [InlineKeyboardButton("🏠 Community Menu", callback_data="mode_community")]
                ])
                
                await query.edit_message_text(message, reply_markup=keyboard)
            else:
                await query.edit_message_text(f"❌ {result['error']}")
                
        except Exception as e:
            self.logger.error(f"Error disabling community reminder: {e}")
            await query.edit_message_text("❌ Error disabling reminder.")
    
    async def _handle_community_stats(self, query, context):
        """Handle community statistics."""
        try:
            # Get user's leagues
            user_leagues = self.league_handlers.league_service.get_user_leagues(query.from_user.id)
            
            if not user_leagues:
                await query.edit_message_text(
                    "📊 <b>Community Stats</b>\n\n"
                    "You're not in any leagues yet. Join a league to see community statistics!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔎 Browse Leagues", callback_data="com_browse")],
                        [InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")]
                    ])
                )
                return
            
            # Show stats for each league
            text = "📊 <b>Community Statistics</b>\n\n"
            
            for league in user_leagues:
                # Get league leaderboard
                leaderboard = self.league_handlers.league_service.get_league_leaderboard(league.league_id)
                
                text += f"<b>🏆 {league.name}</b>\n"
                text += f"   Status: {league.status}\n"
                text += f"   Members: {len(leaderboard)}\n"
                
                if leaderboard:
                    # Find user's position
                    user_position = None
                    for i, member in enumerate(leaderboard):
                        if member['user_id'] == query.from_user.id:
                            user_position = i + 1
                            text += f"   Your Rank: #{user_position}\n"
                            text += f"   Your Progress: {member['progress_percent']:.1f}%\n"
                            break
                    
                    if user_position is None:
                        text += "   Your Progress: Not started\n"
                else:
                    text += "   No progress data yet\n"
                
                text += "\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Community", callback_data="mode_community")]
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error handling community stats: {e}")
            await query.edit_message_text("❌ Error loading community statistics.")
    
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
            # Add inline keyboard for progress update options
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{active[0]['book_id']}")],
                [InlineKeyboardButton("🏠 Individual Menu", callback_data="mode_individual")]
            ])
            await update.message.reply_text(PROGRESS_UPDATE_MESSAGE, reply_markup=keyboard)
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
        """Show reminder inline menu with common times and options"""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("8:00 PM", callback_data="rem_time_2000"), InlineKeyboardButton("9:00 PM", callback_data="rem_time_2100"), InlineKeyboardButton("9:30 PM", callback_data="rem_time_2130")],
            [InlineKeyboardButton("Custom Time", callback_data="rem_custom"), InlineKeyboardButton("Disable", callback_data="rem_disable")],
        ])
        await update.message.reply_text("Reminders — choose a time", reply_markup=kb)
    
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
            await q.edit_message_text("Send a time like 9:00 PM ")
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
            f"Reminder: {pretty} ({r['frequency']}) "
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

    async def handle_goal_inline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline callbacks for setting individual daily goal."""
        q = update.callback_query
        await q.answer()
        data = q.data
        if not data.startswith('goal_'):
            return
        if data == 'goal_custom':
            context.user_data['awaiting_goal_custom'] = True
            await q.edit_message_text("Enter pages per day (number), e.g., 18")
            return
        try:
            val = int(data.split('_')[-1])
            if val <= 0:
                raise ValueError()
        except Exception:
            await q.edit_message_text("Invalid goal value.")
            return
        self.book_service.set_user_daily_goal(q.from_user.id, val)
        await self._show_individual_menu(q)

    async def _show_my_books(self, query, context, page: int = 0):
        user_id = query.from_user.id
        all_books = self.book_service.get_user_books_with_status(user_id)
        total = len(all_books)
        if total == 0:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add My Book", callback_data="ind_add_book"), InlineKeyboardButton("🏠 Menu", callback_data="mode_individual")]])
            await query.edit_message_text("You have no books yet.", reply_markup=kb)
            return
        start = page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        books = all_books[start:end]
        keyboard = []
        for b in books:
            title = f"{b['title']} ({b['display_status']})"
            keyboard.append([InlineKeyboardButton(title, callback_data=f"ind_book_{b['book_id']}")])
        nav = []
        if start > 0:
            nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"ind_my_books_page_{page-1}"))
        if end < total:
            nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"ind_my_books_page_{page+1}"))
        if nav:
            keyboard.append(nav)
        keyboard.append([InlineKeyboardButton("🏠 Menu", callback_data="mode_individual")])
        await query.edit_message_text(f"📚 My Books (Page {page+1}/{(total-1)//self.PAGE_SIZE+1}):", reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_my_books_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        page = int(q.data.split('_')[-1])
        await self._show_my_books(q, context, page=page)

    async def handle_my_book_open(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        book_id = int(q.data.split('_')[-1])
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Update Progress", callback_data=f"progress_select_{book_id}")],
            [InlineKeyboardButton("🗑️ Delete", callback_data=f"ind_del_{book_id}")],
            [InlineKeyboardButton("⬅️ Back to My Books", callback_data="ind_my_books")],
        ])
        await q.edit_message_text("Choose an action:", reply_markup=kb)

    async def handle_delete_book_inline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        data = q.data
        if data.startswith('ind_del_') and not data.startswith('ind_del_confirm_'):
            book_id = int(data.split('_')[-1])
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Delete", callback_data=f"ind_del_confirm_{book_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="ind_my_books")],
            ])
            await q.edit_message_text("Are you sure you want to delete this book? This will remove your progress.", reply_markup=kb)
            return
        if data.startswith('ind_del_confirm_'):
            book_id = int(data.split('_')[-1])
            ok = self.book_service.delete_user_book(q.from_user.id, book_id)
            if ok:
                await self._show_my_books(q, context, page=0)
            else:
                await q.edit_message_text("Could not delete this book.")
    
    async def _handle_league_creation_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input during league creation."""
        from src.core.handlers.admin_league_handlers import AdminLeagueHandlers
        from src.services.factory import get_league_service
        
        league_service = get_league_service()
        league_handlers = AdminLeagueHandlers(league_service)
        
        # Route to appropriate league creation handler based on current step
        if context.user_data.get('awaiting_description'):
            await league_handlers.handle_league_description_input(update, context)
        elif context.user_data.get('awaiting_book_selection'):
            # This is handled by callback handlers, not text input
            pass
        elif context.user_data.get('awaiting_duration'):
            await league_handlers.handle_league_duration_input(update, context)
        elif context.user_data.get('awaiting_daily_goal'):
            await league_handlers.handle_league_daily_goal_input(update, context)
        elif context.user_data.get('awaiting_max_members'):
            await league_handlers.handle_league_max_members_input(update, context)
        else:
            # Default to name input
            await league_handlers.handle_league_name_input(update, context)

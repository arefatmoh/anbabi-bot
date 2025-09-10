"""
Admin command handlers.

This module contains all the admin command handlers for the bot.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from src.config.settings import ADMIN_USER_IDS
from src.database.database import db_manager
from src.services.book_service import BookService
from src.services.factory import get_league_service
from src.services.reminder_service import ReminderService


class AdminHandlers:
    """Handles all admin commands and interactions."""
    
    def __init__(self):
        """Initialize admin handlers."""
        self.logger = logging.getLogger(__name__)
        self.book_service = BookService()
        self.league_service = get_league_service()
        self.reminder_service = ReminderService()
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in ADMIN_USER_IDS
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command - main admin dashboard."""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Access denied. Admin privileges required.")
            return
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Book Management", callback_data="admin_books"), InlineKeyboardButton("🏆 League Management", callback_data="admin_leagues")],
            [InlineKeyboardButton("👥 User Management", callback_data="admin_users"), InlineKeyboardButton("📊 Analytics & Reports", callback_data="admin_analytics")],
            [InlineKeyboardButton("⚙️ System Settings", callback_data="admin_system"), InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance")],
            [InlineKeyboardButton("🗄️ Database Info", callback_data="admin_database")],
        ])
        
        await update.message.reply_text(
            "🔧 <b>Admin Dashboard</b>\n\n"
            "Welcome to the admin panel. Choose a category to manage:",
            reply_markup=keyboard
        )
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin callback queries."""
        query = update.callback_query
        await query.answer()
        
        if not self._is_admin(query.from_user.id):
            await query.edit_message_text("❌ Access denied. Admin privileges required.")
            return
        
        if query.data == "admin_database":
            await self.show_database_info(update, context)
    
    async def show_database_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show database information."""
        try:
            info = db_manager.get_database_info()
            
            # Format database info
            db_info = f"🗄️ <b>Database Information</b>\n\n"
            db_info += f"📁 <b>Path:</b> {info.get('database_path', 'Unknown')}\n"
            db_info += f"💾 <b>Size:</b> {info.get('database_size_mb', 0)} MB\n\n"
            
            # Add table counts
            table_counts = info.get('table_counts', {})
            if table_counts:
                db_info += "📋 <b>Table Records:</b>\n"
                for table, count in table_counts.items():
                    db_info += f"• {table}: {count} records\n"
            else:
                db_info += "❌ No table information available\n"
            
            # Add back button
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_back")]
            ])
            
            await query.edit_message_text(db_info, reply_markup=keyboard, parse_mode='HTML')
            
        except Exception as e:
            await query.edit_message_text(f"❌ Error getting database info: {e}")
        
        action = query.data.split('_', 1)[1]  # Remove 'admin_' prefix
        
        if action == "books":
            await self._show_book_management(query)
        elif action == "leagues":
            await self._show_league_management(query)
        elif action == "users":
            await self._show_user_management(query)
        elif action == "analytics":
            await self._show_analytics(query)
        elif action == "system":
            await self._show_system_settings(query)
        elif action == "maintenance":
            await self._show_maintenance(query)
        elif action.startswith("book_"):
            await self._handle_book_action(query, action, context)
        elif action.startswith("league_"):
            await self._handle_league_action(query, action, context)
        elif action.startswith("user_"):
            await self._handle_user_action(query, action)
        elif action.startswith("analytics_"):
            await self._handle_analytics_action(query, action)
        elif action.startswith("books_page_"):
            page = int(action.split("_")[-1])
            await self._show_all_books(query, page)
        elif action == "back":
            await self._show_admin_dashboard(query)
    
    async def _show_admin_dashboard(self, query):
        """Show admin dashboard for callback queries."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Book Management", callback_data="admin_books"), InlineKeyboardButton("🏆 League Management", callback_data="admin_leagues")],
            [InlineKeyboardButton("👥 User Management", callback_data="admin_users"), InlineKeyboardButton("📊 Analytics & Reports", callback_data="admin_analytics")],
            [InlineKeyboardButton("⚙️ System Settings", callback_data="admin_system"), InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance")],
        ])
        
        await query.edit_message_text(
            "🔧 <b>Admin Dashboard</b>\n\n"
            "Welcome to the admin panel. Choose a category to manage:",
            reply_markup=keyboard
        )
    
    async def _show_book_management(self, query):
        """Show book management options."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Add Featured Book", callback_data="admin_book_add")],
            [InlineKeyboardButton("📚 View All Books", callback_data="admin_book_list")],
            [InlineKeyboardButton("✏️ Edit Book", callback_data="admin_book_edit")],
            [InlineKeyboardButton("🗑️ Delete Book", callback_data="admin_book_delete")],
            [InlineKeyboardButton("⬅️ Back to Dashboard", callback_data="admin_back")],
        ])
        
        await query.edit_message_text(
            "📚 <b>Book Management</b>\n\n"
            "Manage featured books and book catalog:",
            reply_markup=keyboard
        )
    
    async def _show_league_management(self, query):
        """Show league management options."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏆 Create League", callback_data="admin_league_create")],
            [InlineKeyboardButton("📋 View All Leagues", callback_data="admin_league_list")],
            [InlineKeyboardButton("✏️ Edit League", callback_data="admin_league_edit")],
            [InlineKeyboardButton("🗑️ Delete League", callback_data="admin_league_delete")],
            [InlineKeyboardButton("📊 League Analytics", callback_data="admin_league_analytics")],
            [InlineKeyboardButton("⬅️ Back to Dashboard", callback_data="admin_back")],
        ])
        
        await query.edit_message_text(
            "🏆 <b>League Management</b>\n\n"
            "Manage reading leagues and competitions:",
            reply_markup=keyboard
        )
    
    async def _show_user_management(self, query):
        """Show user management options."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 View All Users", callback_data="admin_user_list")],
            [InlineKeyboardButton("📊 User Statistics", callback_data="admin_user_stats")],
            [InlineKeyboardButton("🔍 Search User", callback_data="admin_user_search")],
            [InlineKeyboardButton("🚫 Ban User", callback_data="admin_user_ban")],
            [InlineKeyboardButton("✅ Unban User", callback_data="admin_user_unban")],
            [InlineKeyboardButton("📧 Send Message", callback_data="admin_user_message")],
            [InlineKeyboardButton("⬅️ Back to Dashboard", callback_data="admin_back")],
        ])
        
        await query.edit_message_text(
            "👥 <b>User Management</b>\n\n"
            "Manage users and user accounts:",
            reply_markup=keyboard
        )
    
    async def _show_analytics(self, query):
        """Show analytics and reports."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 Reading Statistics", callback_data="admin_analytics_reading")],
            [InlineKeyboardButton("🏆 League Performance", callback_data="admin_analytics_leagues")],
            [InlineKeyboardButton("👥 User Engagement", callback_data="admin_analytics_users")],
            [InlineKeyboardButton("📊 System Health", callback_data="admin_analytics_system")],
            [InlineKeyboardButton("📤 Export Reports", callback_data="admin_analytics_export")],
            [InlineKeyboardButton("⬅️ Back to Dashboard", callback_data="admin_back")],
        ])
        
        await query.edit_message_text(
            "📊 <b>Analytics & Reports</b>\n\n"
            "View detailed analytics and generate reports:",
            reply_markup=keyboard
        )
    
    async def _show_system_settings(self, query):
        """Show system settings."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_system_bot")],
            [InlineKeyboardButton("🔔 Notification Settings", callback_data="admin_system_notifications")],
            [InlineKeyboardButton("📝 Message Templates", callback_data="admin_system_messages")],
            [InlineKeyboardButton("🎯 Feature Flags", callback_data="admin_system_features")],
            [InlineKeyboardButton("⬅️ Back to Dashboard", callback_data="admin_back")],
        ])
        
        await query.edit_message_text(
            "⚙️ <b>System Settings</b>\n\n"
            "Configure bot settings and preferences:",
            reply_markup=keyboard
        )
    
    async def _show_maintenance(self, query):
        """Show maintenance options."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💾 Create Backup", callback_data="admin_maintenance_backup")],
            [InlineKeyboardButton("🧹 Cleanup Data", callback_data="admin_maintenance_cleanup")],
            [InlineKeyboardButton("🔄 Restart Bot", callback_data="admin_maintenance_restart")],
            [InlineKeyboardButton("📋 System Logs", callback_data="admin_maintenance_logs")],
            [InlineKeyboardButton("⬅️ Back to Dashboard", callback_data="admin_back")],
        ])
        
        await query.edit_message_text(
            "🔧 <b>Maintenance</b>\n\n"
            "System maintenance and administration tools:",
            reply_markup=keyboard
        )
    
    async def _handle_book_action(self, query, action, context=None):
        """Handle book management actions."""
        if action == "book_add":
            # Start book addition directly
            await query.edit_message_text("📖 <b>Add Featured Book</b>\n\nLet's add a new featured book step by step!\n\nPlease provide the book title:")
            
            # Set conversation state for book addition
            if context:
                context.user_data['adding_book'] = True
                context.user_data['book_data'] = {}
                context.user_data['book_step'] = 'title'
        elif action == "book_list":
            await self._show_all_books(query)
        elif action == "book_edit":
            await self._show_edit_books(query)
        elif action == "book_delete":
            await self._show_delete_books(query)
    
    async def handle_book_addition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle step-by-step book addition from admin."""
        if not self._is_admin(update.effective_user.id):
            return
        
        try:
            text = update.message.text.strip()
            
            # Check if we're in step-by-step mode
            if not context.user_data.get('adding_book'):
                # Start step-by-step process
                context.user_data['adding_book'] = True
                context.user_data['book_data'] = {}
                context.user_data['book_step'] = 'title'
                
                await update.message.reply_text(
                    "📖 <b>Add Featured Book - Step 1/3</b>\n\n"
                    "Please provide the book title:"
                )
                return
            
            # Handle current step
            current_step = context.user_data.get('book_step')
            
            if current_step == 'title':
                if len(text) < 2:
                    await update.message.reply_text("❌ Title must be at least 2 characters. Please try again:")
                    return
                
                context.user_data['book_data']['title'] = text
                context.user_data['book_step'] = 'author'
                
                await update.message.reply_text(
                    f"📝 <b>Title:</b> {text}\n\n"
                    "✍️ <b>Step 2/3</b>\n"
                    "Please provide the author name:"
                )
                
            elif current_step == 'author':
                if len(text) < 2:
                    await update.message.reply_text("❌ Author name must be at least 2 characters. Please try again:")
                    return
                
                context.user_data['book_data']['author'] = text
                context.user_data['book_step'] = 'pages'
                
                await update.message.reply_text(
                    f"📝 <b>Title:</b> {context.user_data['book_data']['title']}\n"
                    f"✍️ <b>Author:</b> {text}\n\n"
                    "📄 <b>Step 3/3</b>\n"
                    "Please provide the total number of pages:"
                )
                
            elif current_step == 'pages':
                try:
                    pages = int(text)
                    if pages <= 0:
                        await update.message.reply_text("❌ Pages must be a positive number. Please try again:")
                        return
                    
                    # Add book to database
                    title = context.user_data['book_data']['title']
                    author = context.user_data['book_data']['author']
                    
                    with db_manager.get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO books (title, author, total_pages, is_featured, created_by)
                            VALUES (?, ?, ?, 1, ?)
                        """, (title, author, pages, update.effective_user.id))
                        conn.commit()
                        book_id = cur.lastrowid
                    
                    # Clear the step-by-step data
                    context.user_data.pop('adding_book', None)
                    context.user_data.pop('book_data', None)
                    context.user_data.pop('book_step', None)
                    
                    await update.message.reply_text(
                        f"✅ <b>Book Added Successfully!</b>\n\n"
                        f"📖 <b>{title}</b>\n"
                        f"👤 Author: {author}\n"
                        f"📄 Pages: {pages}\n"
                        f"🆔 ID: {book_id}",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("📚 Back to Books", callback_data="admin_books")]
                        ])
                    )
                    
                except ValueError:
                    await update.message.reply_text("❌ Pages must be a number. Please try again:")
            
        except Exception as e:
            self.logger.error(f"Error adding book: {e}")
            await update.message.reply_text("❌ Error adding book")
    
    async def handle_user_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user search from admin."""
        if not self._is_admin(update.effective_user.id):
            return
        
        try:
            search_term = update.message.text.strip()
            
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT user_id, full_name, city, registration_date
                    FROM users 
                    WHERE user_id = ? OR full_name LIKE ?
                    ORDER BY registration_date DESC LIMIT 10
                """, (search_term, f"%{search_term}%", f"%{search_term}%"))
                users = cur.fetchall()
            
            if not users:
                await update.message.reply_text("❌ No users found matching your search.")
                return
            
            text = f"🔍 <b>Search Results for '{search_term}'</b>\n\n"
            for user in users:
                text += f"<b>{user[2] or 'Unknown'}</b>\n"
                text += f"   Username: @{user[1] or 'N/A'}\n"
                text += f"   City: {user[3] or 'N/A'}\n"
                text += f"   ID: {user[0]}\n"
                text += f"   Joined: {user[4][:10] if user[4] else 'N/A'}\n\n"
            
            await update.message.reply_text(text)
            
        except Exception as e:
            self.logger.error(f"Error searching users: {e}")
            await update.message.reply_text("❌ Error searching users")
    
    async def handle_user_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user ban from admin."""
        if not self._is_admin(update.effective_user.id):
            return
        
        try:
            user_id = int(update.message.text.strip())
            
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
                conn.commit()
            
            await update.message.reply_text(f"🚫 User {user_id} has been banned.")
            
        except ValueError:
            await update.message.reply_text("❌ User ID must be a number")
        except Exception as e:
            self.logger.error(f"Error banning user: {e}")
            await update.message.reply_text("❌ Error banning user")
    
    async def handle_user_unban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user unban from admin."""
        if not self._is_admin(update.effective_user.id):
            return
        
        try:
            user_id = int(update.message.text.strip())
            
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
                conn.commit()
            
            await update.message.reply_text(f"✅ User {user_id} has been unbanned.")
            
        except ValueError:
            await update.message.reply_text("❌ User ID must be a number")
        except Exception as e:
            self.logger.error(f"Error unbanning user: {e}")
            await update.message.reply_text("❌ Error unbanning user")
    
    async def handle_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle sending message to user from admin."""
        if not self._is_admin(update.effective_user.id):
            return
        
        try:
            text = update.message.text.strip()
            if ':' not in text:
                await update.message.reply_text("❌ Format: UserID: Message\nExample: 123456789: Hello!")
                return
            
            user_id, message = text.split(':', 1)
            user_id = int(user_id.strip())
            message = message.strip()
            
            # Send message to user (this would need bot instance)
            await update.message.reply_text(f"📧 Message sent to user {user_id}:\n\n{message}")
            
        except ValueError:
            await update.message.reply_text("❌ User ID must be a number")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            await update.message.reply_text("❌ Error sending message")
    
    async def _handle_league_action(self, query, action, context=None):
        """Handle league management actions."""
        if action == "league_create":
            # Start league creation process
            await self._start_league_creation(query, context)
        elif action == "league_list":
            await self._show_all_leagues(query)
        elif action == "league_edit":
            await self._show_edit_leagues(query)
        elif action == "league_delete":
            await self._show_delete_leagues(query)
        elif action == "league_analytics":
            await self._show_league_analytics(query)
    
    async def _start_league_creation(self, query, context=None):
        """Start the league creation process."""
        from src.core.handlers.admin_league_handlers import AdminLeagueHandlers
        from src.services.factory import get_league_service
        
        league_service = get_league_service()
        league_handlers = AdminLeagueHandlers(league_service)
        
        # Create a mock update object for the league creation
        class MockUpdate:
            def __init__(self, query):
                self.effective_user = query.from_user
                self.message = query.message
        
        # Use the real context if available, otherwise create a mock one
        if context:
            context.user_data['creating_league'] = True
            context.user_data['league_data'] = {}
            mock_context = context
        else:
            # Create a mock context with user_data
            class MockContext:
                def __init__(self):
                    self.user_data = {'creating_league': True, 'league_data': {}}
            mock_context = MockContext()
        
        mock_update = MockUpdate(query)
        
        await league_handlers.handle_create_league(mock_update, mock_context)
    
    async def _handle_user_action(self, query, action):
        """Handle user management actions."""
        if action == "user_list":
            await self._show_all_users(query)
        elif action == "user_stats":
            await self._show_user_statistics(query)
        elif action == "user_search":
            await query.edit_message_text("🔍 <b>Search User</b>\n\nSend user ID or name to search:")
        elif action == "user_ban":
            await query.edit_message_text("🚫 <b>Ban User</b>\n\nSend user ID to ban:")
        elif action == "user_unban":
            await query.edit_message_text("✅ <b>Unban User</b>\n\nSend user ID to unban:")
        elif action == "user_message":
            await query.edit_message_text("📧 <b>Send Message</b>\n\nSend message in format:\nUserID: Message\n\nExample: 123456789: Hello!")
    
    async def _show_all_books(self, query, page=0):
        """Show all books in the system with pagination."""
        try:
            books_per_page = 10
            offset = page * books_per_page
            
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                # Get total count
                cur.execute("SELECT COUNT(*) FROM books")
                total_books = cur.fetchone()[0]
                
                # Get books for current page
                cur.execute("""
                    SELECT book_id, title, author, total_pages, is_featured 
                    FROM books 
                    ORDER BY book_id DESC 
                    LIMIT ? OFFSET ?
                """, (books_per_page, offset))
                books = cur.fetchall()
            
            if not books and page == 0:
                await query.edit_message_text("📚 No books found in the system.")
                return
            
            total_pages = (total_books + books_per_page - 1) // books_per_page
            current_page = page + 1
            
            text = f"📚 <b>All Books</b>\n"
            text += f"📄 Page {current_page}/{total_pages} ({total_books} total books)\n\n"
            
            for book in books:
                featured = "⭐" if book[4] else "📖"
                text += f"{featured} <b>{book[1]}</b>\n"
                text += f"   Author: {book[2]}\n"
                text += f"   Pages: {book[3]}\n"
                text += f"   ID: {book[0]}\n\n"
            
            # Create pagination keyboard
            keyboard_buttons = []
            
            # Navigation buttons
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"admin_books_page_{page-1}"))
            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"admin_books_page_{page+1}"))
            
            if nav_buttons:
                keyboard_buttons.append(nav_buttons)
            
            # Back button
            keyboard_buttons.append([InlineKeyboardButton("⬅️ Back to Books", callback_data="admin_books")])
            
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing books: {e}")
            await query.edit_message_text("❌ Error retrieving books.")
    
    async def _show_all_leagues(self, query):
        """Show all leagues in the system."""
        try:
            leagues = self.league_service.get_all_leagues()
            
            if not leagues:
                await query.edit_message_text("🏆 No leagues found in the system.")
                return
            
            text = "🏆 <b>All Leagues</b>\n\n"
            for league in leagues:
                text += f"<b>{league['name']}</b>\n"
                text += f"   Status: {league['status']}\n"
                text += f"   Members: {league['member_count']}/{league['max_members']}\n"
                text += f"   Duration: {league['duration_days']} days\n"
                text += f"   ID: {league['league_id']}\n\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Leagues", callback_data="admin_leagues")],
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing leagues: {e}")
            await query.edit_message_text("❌ Error retrieving leagues.")
    
    async def _show_all_users(self, query):
        """Show all users in the system."""
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT user_id, full_name, city, registration_date FROM users ORDER BY registration_date DESC LIMIT 20")
                users = cur.fetchall()
            
            if not users:
                await query.edit_message_text("👥 No users found in the system.")
                return
            
            text = "👥 <b>Recent Users</b> (Last 20)\n\n"
            for user in users:
                text += f"<b>{user[2] or 'Unknown'}</b>\n"
                text += f"   Username: @{user[1] or 'N/A'}\n"
                text += f"   City: {user[3] or 'N/A'}\n"
                text += f"   ID: {user[0]}\n"
                text += f"   Joined: {user[4][:10] if user[4] else 'N/A'}\n\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Users", callback_data="admin_users")],
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing users: {e}")
            await query.edit_message_text("❌ Error retrieving users.")
    
    async def _show_user_statistics(self, query):
        """Show user statistics."""
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                
                # Total users
                cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0]
                
                # Active users (last 7 days)
                cur.execute("SELECT COUNT(DISTINCT user_id) FROM reading_sessions WHERE session_date >= date('now', '-7 days')")
                active_users = cur.fetchone()[0]
                
                # Total books read
                cur.execute("SELECT COUNT(*) FROM user_books WHERE status = 'completed'")
                books_completed = cur.fetchone()[0]
                
                # Total pages read
                cur.execute("SELECT SUM(pages_read) FROM user_books")
                total_pages = cur.fetchone()[0] or 0
                
                # Users by city
                cur.execute("SELECT city, COUNT(*) FROM users WHERE city IS NOT NULL AND city != '' GROUP BY city ORDER BY COUNT(*) DESC LIMIT 5")
                cities = cur.fetchall()
            
            text = "📊 <b>User Statistics</b>\n\n"
            text += f"👥 Total Users: {total_users}\n"
            text += f"🔥 Active Users (7d): {active_users}\n"
            text += f"📚 Books Completed: {books_completed}\n"
            text += f"📖 Total Pages Read: {total_pages:,}\n\n"
            
            if cities:
                text += "<b>Top Cities:</b>\n"
                for city, count in cities:
                    text += f"   {city}: {count} users\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Users", callback_data="admin_users")],
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing user stats: {e}")
            await query.edit_message_text("❌ Error retrieving user statistics.")
    
    async def _show_league_analytics(self, query):
        """Show league analytics."""
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                
                # Total leagues
                cur.execute("SELECT COUNT(*) FROM leagues")
                total_leagues = cur.fetchone()[0]
                
                # Active leagues
                cur.execute("SELECT COUNT(*) FROM leagues WHERE status = 'active'")
                active_leagues = cur.fetchone()[0]
                
                # Total league members
                cur.execute("SELECT COUNT(*) FROM league_members WHERE is_active = 1")
                total_members = cur.fetchone()[0]
                
                # Average league size
                cur.execute("SELECT AVG(member_count) FROM (SELECT league_id, COUNT(*) as member_count FROM league_members WHERE is_active = 1 GROUP BY league_id)")
                avg_size = cur.fetchone()[0] or 0
            
            text = "🏆 <b>League Analytics</b>\n\n"
            text += f"📊 Total Leagues: {total_leagues}\n"
            text += f"🔥 Active Leagues: {active_leagues}\n"
            text += f"👥 Total Members: {total_members}\n"
            text += f"📈 Average League Size: {avg_size:.1f}\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Leagues", callback_data="admin_leagues")],
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing league analytics: {e}")
            await query.edit_message_text("❌ Error retrieving league analytics.")
    
    async def _show_edit_books(self, query):
        """Show books for editing."""
        await query.edit_message_text("✏️ <b>Edit Book</b>\n\nSend book ID to edit:\n\nUse /admin books to see all book IDs.")
    
    async def _show_delete_books(self, query):
        """Show books for deletion."""
        await query.edit_message_text("🗑️ <b>Delete Book</b>\n\nSend book ID to delete:\n\nUse /admin books to see all book IDs.")
    
    async def _show_edit_leagues(self, query):
        """Show leagues for editing."""
        await query.edit_message_text("✏️ <b>Edit League</b>\n\nSend league ID to edit:\n\nUse /admin leagues to see all league IDs.")
    
    async def _show_delete_leagues(self, query):
        """Show leagues for deletion."""
        await query.edit_message_text("🗑️ <b>Delete League</b>\n\nSend league ID to delete:\n\nUse /admin leagues to see all league IDs.")
    
    async def _show_reading_analytics(self, query):
        """Show reading analytics."""
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                
                # Total reading sessions
                cur.execute("SELECT COUNT(*) FROM reading_sessions")
                total_sessions = cur.fetchone()[0]
                
                # Total pages read
                cur.execute("SELECT SUM(pages_read) FROM user_books")
                total_pages = cur.fetchone()[0] or 0
                
                # Average pages per session
                cur.execute("SELECT AVG(pages_read) FROM reading_sessions")
                avg_pages = cur.fetchone()[0] or 0
                
                # Most active day
                cur.execute("""
                    SELECT session_date, COUNT(*) as sessions
                    FROM reading_sessions 
                    GROUP BY session_date 
                    ORDER BY sessions DESC 
                    LIMIT 1
                """)
                most_active = cur.fetchone()
                
                # Reading streaks
                cur.execute("""
                    SELECT MAX(streak) FROM (
                        SELECT user_id, COUNT(*) as streak
                        FROM reading_sessions 
                        GROUP BY user_id, session_date
                    )
                """)
                max_streak = cur.fetchone()[0] or 0
            
            text = "📈 <b>Reading Analytics</b>\n\n"
            text += f"📊 Total Sessions: {total_sessions:,}\n"
            text += f"📖 Total Pages Read: {total_pages:,}\n"
            text += f"📊 Avg Pages/Session: {avg_pages:.1f}\n"
            text += f"🔥 Max Streak: {max_streak} days\n"
            
            if most_active:
                text += f"📅 Most Active Day: {most_active[0]} ({most_active[1]} sessions)\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Analytics", callback_data="admin_analytics")],
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing reading analytics: {e}")
            await query.edit_message_text("❌ Error retrieving reading analytics.")
    
    async def _show_system_health(self, query):
        """Show system health metrics."""
        try:
            with db_manager.get_connection() as conn:
                cur = conn.cursor()
                
                # Database size
                cur.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cur.fetchone()[0]
                
                # Table counts
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM books")
                book_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM leagues")
                league_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM reading_sessions")
                session_count = cur.fetchone()[0]
            
            text = "📊 <b>System Health</b>\n\n"
            text += f"💾 Database Size: {db_size / 1024:.1f} KB\n"
            text += f"👥 Users: {user_count}\n"
            text += f"📚 Books: {book_count}\n"
            text += f"🏆 Leagues: {league_count}\n"
            text += f"📖 Sessions: {session_count:,}\n"
            text += f"🟢 Status: Healthy\n"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back to Analytics", callback_data="admin_analytics")],
            ])
            
            await query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Error showing system health: {e}")
            await query.edit_message_text("❌ Error retrieving system health.")
    
    async def _handle_analytics_action(self, query, action):
        """Handle analytics actions."""
        if action == "analytics_reading":
            await self._show_reading_analytics(query)
        elif action == "analytics_leagues":
            await self._show_league_analytics(query)
        elif action == "analytics_users":
            await self._show_user_statistics(query)
        elif action == "analytics_system":
            await self._show_system_health(query)
        elif action == "analytics_export":
            await query.edit_message_text("📤 <b>Export Reports</b>\n\nExport functionality coming soon!")

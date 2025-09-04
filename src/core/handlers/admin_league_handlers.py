"""
Admin league handlers for league management.

This module handles all admin league management operations.
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from src.services.league_service import LeagueService
from src.core.keyboards.league_keyboards import (
    get_league_management_keyboard,
    get_league_edit_keyboard,
    get_league_stats_keyboard
)
from src.config.messages import (
    LEAGUE_CREATED,
    LEAGUE_MANAGEMENT_MENU,
    LEAGUE_EDIT_SUCCESS,
    LEAGUE_EDIT_FAILED
)


class AdminLeagueHandlers:
    """Handlers for admin league management."""
    
    def __init__(self, league_service: LeagueService):
        """Initialize admin league handlers."""
        self.league_service = league_service
        self.logger = logging.getLogger(__name__)
    
    async def handle_create_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league creation command."""
        try:
            # Check if user is admin
            user_id = update.effective_user.id
            if not self._is_admin(user_id):
                await update.message.reply_text(
                    "❌ You don't have permission to create leagues."
                )
                return
            
            # Start league creation conversation
            await update.message.reply_text(
                "🏆 **Create New Reading League**\n\n"
                "Let's create a new community reading league!\n\n"
                "Please provide the league name:"
            )
            
            # Set conversation state
            context.user_data['creating_league'] = True
            context.user_data['league_data'] = {}
            
        except Exception as e:
            self.logger.error(f"Failed to start league creation: {e}")
            await update.message.reply_text("❌ Failed to start league creation")
    
    async def handle_league_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league name input."""
        try:
            if not context.user_data.get('creating_league'):
                return
            
            league_name = update.message.text.strip()
            if len(league_name) < 3:
                await update.message.reply_text(
                    "❌ League name must be at least 3 characters long.\n"
                    "Please try again:"
                )
                return
            
            context.user_data['league_data']['name'] = league_name
            
            await update.message.reply_text(
                f"📝 **League Name:** {league_name}\n\n"
                "Now please provide a description (optional):\n"
                "Or send 'skip' to continue without description."
            )
            
            context.user_data['awaiting_description'] = True
            
        except Exception as e:
            self.logger.error(f"Failed to process league name: {e}")
            await update.message.reply_text("❌ Failed to process league name")
    
    async def handle_league_description_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league description input."""
        try:
            if not context.user_data.get('awaiting_description'):
                return
            
            description = update.message.text.strip()
            if description.lower() == 'skip':
                description = None
            
            context.user_data['league_data']['description'] = description
            
            await update.message.reply_text(
                "📚 Now please provide the book ID for this league:\n\n"
                "You can use /books to see available books."
            )
            
            context.user_data['awaiting_book_id'] = True
            context.user_data['awaiting_description'] = False
            
        except Exception as e:
            self.logger.error(f"Failed to process league description: {e}")
            await update.message.reply_text("❌ Failed to process league description")
    
    async def handle_league_book_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league book ID input."""
        try:
            if not context.user_data.get('awaiting_book_id'):
                return
            
            try:
                book_id = int(update.message.text.strip())
            except ValueError:
                await update.message.reply_text(
                    "❌ Please provide a valid book ID (number).\n"
                    "Try again:"
                )
                return
            
            context.user_data['league_data']['book_id'] = book_id
            
            await update.message.reply_text(
                "📅 Now please provide the league duration in days:\n\n"
                "Recommended: 14-30 days for most books.\n"
                "Default: 20 days"
            )
            
            context.user_data['awaiting_duration'] = True
            context.user_data['awaiting_book_id'] = False
            
        except Exception as e:
            self.logger.error(f"Failed to process league book ID: {e}")
            await update.message.reply_text("❌ Failed to process league book ID")
    
    async def handle_league_duration_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league duration input."""
        try:
            if not context.user_data.get('awaiting_duration'):
                return
            
            try:
                duration = int(update.message.text.strip())
                if duration < 1 or duration > 365:
                    await update.message.reply_text(
                        "❌ Duration must be between 1 and 365 days.\n"
                        "Please try again:"
                    )
                    return
            except ValueError:
                await update.message.reply_text(
                    "❌ Please provide a valid number of days.\n"
                    "Try again:"
                )
                return
            
            context.user_data['league_data']['duration'] = duration
            
            await update.message.reply_text(
                "🎯 Now please provide the daily reading goal in pages:\n\n"
                "Recommended: 15-25 pages per day\n"
                "Default: 20 pages"
            )
            
            context.user_data['awaiting_daily_goal'] = True
            context.user_data['awaiting_duration'] = False
            
        except Exception as e:
            self.logger.error(f"Failed to process league duration: {e}")
            await update.message.reply_text("❌ Failed to process league duration")
    
    async def handle_league_daily_goal_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league daily goal input."""
        try:
            if not context.user_data.get('awaiting_daily_goal'):
                return
            
            try:
                daily_goal = int(update.message.text.strip())
                if daily_goal < 1 or daily_goal > 100:
                    await update.message.reply_text(
                        "❌ Daily goal must be between 1 and 100 pages.\n"
                        "Please try again:"
                    )
                    return
            except ValueError:
                await update.message.reply_text(
                    "❌ Please provide a valid number of pages.\n"
                    "Try again:"
                )
                return
            
            context.user_data['league_data']['daily_goal'] = daily_goal
            
            await update.message.reply_text(
                "👥 Finally, please provide the maximum number of members:\n\n"
                "Recommended: 20-50 members\n"
                "Default: 50 members"
            )
            
            context.user_data['awaiting_max_members'] = True
            context.user_data['awaiting_daily_goal'] = False
            
        except Exception as e:
            self.logger.error(f"Failed to process league daily goal: {e}")
            await update.message.reply_text("❌ Failed to process league daily goal")
    
    async def handle_league_max_members_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league max members input with confirmation step."""
        try:
            if not context.user_data.get('awaiting_max_members'):
                return
            
            try:
                max_members = int(update.message.text.strip())
                if max_members < 2 or max_members > 200:
                    await update.message.reply_text(
                        "❌ Max members must be between 2 and 200.\n"
                        "Please try again:"
                    )
                    return
            except ValueError:
                await update.message.reply_text(
                    "❌ Please provide a valid number of members.\n"
                    "Try again:"
                )
                return
            
            league_data = context.user_data['league_data']
            league_data['max_members'] = max_members
            
            # Confirmation step
            summary = (
                "Please confirm the league details:\n\n"
                f"Name: {league_data['name']}\n"
                f"Description: {league_data.get('description') or '-'}\n"
                f"Book ID: {league_data['book_id']}\n"
                f"Duration: {league_data.get('duration', 20)} days\n"
                f"Daily Goal: {league_data.get('daily_goal', 20)} pages\n"
                f"Max Members: {league_data['max_members']}\n\n"
                "Send 'confirm' to create or 'cancel' to abort."
            )
            context.user_data['awaiting_confirm'] = True
            context.user_data['awaiting_max_members'] = False
            await update.message.reply_text(summary)
        except Exception as e:
            self.logger.error(f"Failed to process league max members: {e}")
            await update.message.reply_text("❌ Failed to process league max members")

    async def handle_league_manage(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league management menu."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Check if user is admin of this league
            league = self.league_service.league_repo.get_league_by_id(league_id)
            if not league or league.admin_id != user_id:
                await query.answer("❌ You don't have permission to manage this league")
                return
            
            keyboard = get_league_management_keyboard(league_id)
            
            await query.edit_message_text(
                LEAGUE_MANAGEMENT_MENU.format(name=league.name),
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show league management: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to load league management"
            )
    
    async def handle_confirm_or_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            if not context.user_data.get('awaiting_confirm'):
                return
            txt = update.message.text.strip().lower()
            if txt not in ("confirm", "cancel"):
                await update.message.reply_text("Type 'confirm' or 'cancel'.")
                return
            if txt == 'cancel':
                await update.message.reply_text("❌ League creation cancelled.")
                self._clear_league_creation_state(context)
                return
            # confirm
            league_data = context.user_data['league_data']
            user_id = update.effective_user.id
            success, message, league_id = self.league_service.create_league(
                name=league_data['name'],
                admin_id=user_id,
                book_id=league_data['book_id'],
                duration_days=league_data.get('duration', 20),
                daily_goal=league_data.get('daily_goal', 20),
                max_members=league_data['max_members'],
                description=league_data.get('description')
            )
            if success:
                await update.message.reply_text(
                    LEAGUE_CREATED.format(
                        name=league_data['name'], league_id=league_id, message=message
                    )
                )
            else:
                await update.message.reply_text(f"❌ Failed to Create League\n\n{message}")
            self._clear_league_creation_state(context)
        except Exception as e:
            self.logger.error(f"Confirm error: {e}")
            await update.message.reply_text("❌ Error during confirmation")
            self._clear_league_creation_state(context)

    # Simple edit commands (admin only): /league_edit_goal <league_id> <daily_goal>, etc.
    async def edit_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) != 2:
                await update.message.reply_text("Usage: /league_edit_goal <league_id> <daily_goal>")
                return
            lid = int(args[0]); goal = int(args[1])
            league = self.league_service.league_repo.get_league_by_id(lid)
            if not league or league.admin_id != update.effective_user.id:
                await update.message.reply_text("❌ Not allowed")
                return
            ok = self.league_service.league_repo.update_goal(lid, goal)
            await update.message.reply_text("✅ Updated" if ok else "❌ Update failed")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}")

    async def edit_dates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) != 3:
                await update.message.reply_text("Usage: /league_edit_dates <league_id> <YYYY-MM-DD> <YYYY-MM-DD>")
                return
            lid = int(args[0])
            from datetime import datetime
            sd = date.fromisoformat(args[1])
            ed = date.fromisoformat(args[2])
            league = self.league_service.league_repo.get_league_by_id(lid)
            if not league or league.admin_id != update.effective_user.id:
                await update.message.reply_text("❌ Not allowed")
                return
            ok = self.league_service.league_repo.update_dates(lid, sd, ed)
            await update.message.reply_text("✅ Updated" if ok else "❌ Update failed")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}")

    async def edit_max(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) != 2:
                await update.message.reply_text("Usage: /league_edit_max <league_id> <max_members>")
                return
            lid = int(args[0]); mm = int(args[1])
            league = self.league_service.league_repo.get_league_by_id(lid)
            if not league or league.admin_id != update.effective_user.id:
                await update.message.reply_text("❌ Not allowed")
                return
            ok = self.league_service.league_repo.update_max_members(lid, mm)
            await update.message.reply_text("✅ Updated" if ok else "❌ Update failed")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}")

    async def export_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) != 1:
                await update.message.reply_text("Usage: /league_export <league_id>")
                return
            lid = int(args[0])
            league = self.league_service.league_repo.get_league_by_id(lid)
            if not league or league.admin_id != update.effective_user.id:
                await update.message.reply_text("❌ Not allowed")
                return
            rows = self.league_service.league_repo.export_league_rows(lid)
            if not rows:
                await update.message.reply_text("No data to export.")
                return
            # Simple CSV inline
            import csv
            from io import StringIO
            buf = StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
            writer.writeheader(); writer.writerows(rows)
            buf.seek(0)
            await update.message.reply_document(document=buf.getvalue().encode('utf-8'), filename=f"league_{lid}_export.csv")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}")
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        # This should check against the admin list from config
        # For now, return True for testing
        return True
    
    def _clear_league_creation_state(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Clear league creation conversation state."""
        context.user_data.pop('creating_league', None)
        context.user_data.pop('league_data', None)
        context.user_data.pop('awaiting_description', None)
        context.user_data.pop('awaiting_book_id', None)
        context.user_data.pop('awaiting_duration', None)
        context.user_data.pop('awaiting_daily_goal', None)
        context.user_data.pop('awaiting_max_members', None)
        context.user_data.pop('awaiting_confirm', None)

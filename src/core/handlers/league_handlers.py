"""
League handlers for user interactions.

This module handles all league-related user interactions and commands.
"""

import logging
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.services.league_service import LeagueService
from src.core.keyboards.league_keyboards import (
    get_league_main_menu_keyboard,
    get_league_browse_keyboard,
    get_league_detail_keyboard,
    get_league_join_confirmation_keyboard,
    get_league_leave_confirmation_keyboard
)
from src.config.messages import (
    LEAGUE_WELCOME_MESSAGE,
    LEAGUE_BROWSE_MESSAGE,
    LEAGUE_JOIN_SUCCESS,
    LEAGUE_JOIN_FAILED,
    LEAGUE_LEAVE_SUCCESS,
    LEAGUE_LEAVE_FAILED,
    LEAGUE_NOT_FOUND,
    LEAGUE_ALREADY_MEMBER,
    LEAGUE_FULL_MESSAGE
)


class LeagueHandlers:
    """Handlers for league-related user interactions."""
    
    def __init__(self, league_service: LeagueService):
        """Initialize league handlers."""
        self.league_service = league_service
        self.logger = logging.getLogger(__name__)
    
    async def handle_league_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league main menu command."""
        try:
            keyboard = get_league_main_menu_keyboard()
            
            if update.message:
                await update.message.reply_text(
                    LEAGUE_WELCOME_MESSAGE,
                    reply_markup=keyboard
                )
            else:
                await update.callback_query.edit_message_text(
                    LEAGUE_WELCOME_MESSAGE,
                    reply_markup=keyboard
                )
            
        except Exception as e:
            self.logger.error(f"Failed to show league menu: {e}")
            if update.message:
                await update.message.reply_text("❌ Failed to load league menu")
            else:
                await update.callback_query.edit_message_text("❌ Failed to load league menu")
    
    async def handle_league_browse(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league browsing."""
        try:
            user_id = update.effective_user.id
            
            # Get available leagues
            available_leagues = self.league_service.get_available_leagues(user_id)
            
            if not available_leagues:
                await update.callback_query.edit_message_text(
                    "📚 No leagues available to join at the moment.\n\n"
                    "Check back later or ask an admin to create a new league!",
                    reply_markup=get_league_main_menu_keyboard()
                )
                return
            
            # Prepare league data for display
            league_data = []
            for league in available_leagues:
                member_count = self.league_service.league_repo.get_league_member_count(
                    league.league_id
                )
                league_data.append({
                    'league_id': league.league_id,
                    'name': league.name,
                    'member_count': member_count,
                    'max_members': league.max_members
                })
            
            keyboard = get_league_browse_keyboard(league_data)
            
            await update.callback_query.edit_message_text(
                LEAGUE_BROWSE_MESSAGE.format(count=len(available_leagues)),
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Failed to browse leagues: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to load leagues"
            )
    
    async def handle_league_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle viewing league details."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Get league information
            league_info = self.league_service.get_league_info(league_id, user_id)
            
            if not league_info:
                await query.edit_message_text(
                    LEAGUE_NOT_FOUND,
                    reply_markup=get_league_main_menu_keyboard()
                )
                return
            
            # Format league details message
            league = league_info['league']
            message = self._format_league_details(league_info)
            
            # Get appropriate keyboard
            keyboard = get_league_detail_keyboard(league_info)
            
            await query.edit_message_text(
                message,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Failed to view league: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to load league details"
            )
    
    async def handle_league_join(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league join request."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Show confirmation keyboard
            keyboard = get_league_join_confirmation_keyboard(league_id)
            
            await query.edit_message_text(
                "🤔 Are you sure you want to join this league?\n\n"
                "You'll be able to track your reading progress alongside other members!",
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show join confirmation: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to process join request"
            )
    
    async def handle_league_join_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle confirmed league join."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Join the league
            success, message = self.league_service.join_league(league_id, user_id)
            
            if success:
                await query.edit_message_text(
                    LEAGUE_JOIN_SUCCESS.format(message=message),
                    reply_markup=get_league_main_menu_keyboard()
                )
            else:
                await query.edit_message_text(
                    LEAGUE_JOIN_FAILED.format(message=message),
                    reply_markup=get_league_main_menu_keyboard()
                )
                
        except Exception as e:
            self.logger.error(f"Failed to join league: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to join league"
            )
    
    async def handle_league_leave(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league leave request."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Show confirmation keyboard
            keyboard = get_league_leave_confirmation_keyboard(league_id)
            
            await query.edit_message_text(
                "🤔 Are you sure you want to leave this league?\n\n"
                "You'll lose access to league features and progress tracking.",
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show leave confirmation: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to process leave request"
            )
    
    async def handle_league_leave_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle confirmed league leave."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID from callback data
            league_id = int(query.data.split('_')[-1])
            
            # Leave the league
            success, message = self.league_service.leave_league(league_id, user_id)
            
            if success:
                await query.edit_message_text(
                    LEAGUE_LEAVE_SUCCESS.format(message=message),
                    reply_markup=get_league_main_menu_keyboard()
                )
            else:
                await query.edit_message_text(
                    LEAGUE_LEAVE_FAILED.format(message=message),
                    reply_markup=get_league_main_menu_keyboard()
                )
                
        except Exception as e:
            self.logger.error(f"Failed to leave league: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to leave league"
            )
    
    async def handle_league_my_leagues(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle viewing user's leagues."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Get user's leagues
            user_leagues = self.league_service.get_user_leagues(user_id)
            
            if not user_leagues:
                await query.edit_message_text(
                    "📚 You're not a member of any leagues yet.\n\n"
                    "Browse available leagues to join one!",
                    reply_markup=get_league_main_menu_keyboard()
                )
                return
            
            # Format leagues list
            message = "🏆 **Your Leagues:**\n\n"
            for league in user_leagues:
                member_count = self.league_service.league_repo.get_league_member_count(
                    league.league_id
                )
                message += (
                    f"📚 **{league.name}**\n"
                    f"   👥 Members: {member_count}/{league.max_members}\n"
                    f"   📅 Duration: {league.duration_days} days\n"
                    f"   🎯 Daily Goal: {league.daily_goal} pages\n"
                    f"   📊 Progress: {league.progress_percentage:.1f}%\n\n"
                )
            
            # Add navigation
            message += "Use the buttons below to manage your leagues."
            
            # Create keyboard for user's leagues
            keyboard = self._get_my_leagues_keyboard(user_leagues)
            
            await query.edit_message_text(
                message,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show user leagues: {e}")
            await update.callback_query.edit_message_text(
                "❌ Failed to load your leagues"
            )
    
    async def handle_leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show leaderboard for the user's most recent league (simple default)."""
        user_id = update.effective_user.id
        # pick first league for user
        leagues = self.league_service.get_user_leagues(user_id)
        if not leagues:
            await update.message.reply_text("You are not in any leagues. Use /league to join one.")
            return
        league = leagues[0]
        text = self._format_leaderboard(league.league_id, league.name)
        await update.message.reply_text(text)

    async def handle_leaderboard_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle leaderboard view from inline button: league_lb_{id}."""
        query = update.callback_query
        await query.answer()
        league_id = int(query.data.split('_')[-1])
        league = self.league_service.league_repo.get_league_by_id(league_id)
        if not league:
            await query.edit_message_text("❌ League not found.")
            return
        text = self._format_leaderboard(league_id, league.name)
        await query.edit_message_text(text)

    def _format_league_details(self, league_info: Dict[str, Any]) -> str:
        """Format league details for display."""
        league = league_info['league']
        
        message = f"📚 **{league['name']}**\n\n"
        
        if league['description']:
            message += f"📝 {league['description']}\n\n"
        
        message += (
            f"👥 **Members:** {league_info['member_count']}/{league['max_members']}\n"
            f"📅 **Duration:** {league['duration_days']} days\n"
            f"🎯 **Daily Goal:** {league['daily_goal']} pages\n"
            f"📊 **Progress:** {league['progress_percentage']:.1f}%\n"
            f"🏁 **Status:** {league['status']}\n\n"
        )
        
        if league_info['is_member']:
            message += "✅ You are a member of this league!\n"
            if league_info['is_admin']:
                message += "👑 You are the league admin.\n"
        else:
            if league_info['can_join']:
                message += "🎯 You can join this league!\n"
            else:
                message += "❌ This league is full.\n"
        
        return message
    
    def _get_my_leagues_keyboard(self, leagues: list) -> InlineKeyboardMarkup:
        """Get keyboard for user's leagues."""
        from src.core.keyboards.league_keyboards import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        
        for league in leagues:
            keyboard.append([
                InlineKeyboardButton(
                    f"📚 {league.name}",
                    callback_data=f"league_view_{league.league_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back to League Menu", callback_data="league_main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)

    def _format_leaderboard(self, league_id: int, league_name: str) -> str:
        lb = self.league_service.get_league_leaderboard(league_id)
        if not lb:
            return f"🏆 Leaderboard for {league_name}\n\nNo progress yet. Be the first to read!"
        lines: List[str] = [f"🏆 Leaderboard for {league_name}", ""]
        for row in lb[:20]:
            name = row["full_name"] or ("@" + row["username"] if row["username"] else str(row["user_id"]))
            lines.append(
                f"{row['rank']}. {name} — {row['progress_percent']}% ({row['pages_read']}/{row['total_pages']} pages)"
            )
        return "\n".join(lines)

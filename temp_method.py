
    async def handle_league_members_view(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle viewing league members."""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Extract league ID
            league_id = int(query.data.split('_')[-1])
            
            # Get league info
            league = self.league_service.get_league_by_id(league_id)
            if not league:
                await query.edit_message_text("❌ League not found.")
                return
            
            # Get members
            # We can use the leaderboard logic or fetch raw members
            # Let's use leaderboard to show progress too
            leaderboard = self.league_service.get_league_leaderboard(league_id)
            
            message = f"👥 <b>Members of {league.name}</b>\n\n"
            
            if not leaderboard:
                message += "No members yet."
            else:
                for idx, member in enumerate(leaderboard, 1):
                    name = member['full_name'] or f"User {member['user_id']}"
                    progress = member['progress_percent']
                    message += f"{idx}. <b>{name}</b> - {progress}%\n"
            
            from src.core.keyboards.league_keyboards import get_league_members_keyboard    
            # Is user admin?
            is_admin = (league.admin_id == user_id)
            keyboard = get_league_members_keyboard(league_id, is_admin)
            
            await query.edit_message_text(message, reply_markup=keyboard)
            
        except Exception as e:
            self.logger.error(f"Failed to view league members: {e}")
            await update.callback_query.edit_message_text("❌ Failed to load members")

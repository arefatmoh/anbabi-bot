"""
League management keyboards.

This module contains all inline keyboards for league-related interactions.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict


def get_league_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the main league menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("🏆 My Leagues", callback_data="league_my_leagues"),
            InlineKeyboardButton("🔍 Browse Leagues", callback_data="league_browse")
        ],
        [
            InlineKeyboardButton("📊 League Stats", callback_data="league_stats"),
            InlineKeyboardButton("🏅 Leaderboard", callback_data="league_leaderboard")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_league_browse_keyboard(leagues: List[Dict]) -> InlineKeyboardMarkup:
    """Get keyboard for browsing available leagues."""
    keyboard = []
    
    for league in leagues:
        # Create button text with league info
        button_text = f"📚 {league['name']} ({league['member_count']}/{league['max_members']})"
        callback_data = f"league_view_{league['league_id']}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("🔙 Back to League Menu", callback_data="league_main_menu")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_league_detail_keyboard(league_info: Dict) -> InlineKeyboardMarkup:
    """Get keyboard for league details."""
    keyboard = []
    league = league_info['league']
    
    # Show different buttons based on user status
    if league_info['is_member']:
        # User is already a member
        keyboard.append([
            InlineKeyboardButton("📊 My Progress", callback_data=f"league_progress_{league['league_id']}")
        ])
        
        if league_info['is_admin']:
            # Admin controls
            keyboard.append([
                InlineKeyboardButton("⚙️ Manage League", callback_data=f"league_manage_{league['league_id']}"),
                InlineKeyboardButton("👥 View Members", callback_data=f"league_members_{league['league_id']}")
            ])
        else:
            # Regular member
            keyboard.append([
                InlineKeyboardButton("👥 View Members", callback_data=f"league_members_{league['league_id']}"),
                InlineKeyboardButton("❌ Leave League", callback_data=f"league_leave_{league['league_id']}")
            ])
    else:
        # User can join
        if league_info['can_join']:
            keyboard.append([
                InlineKeyboardButton("✅ Join League", callback_data=f"league_join_{league['league_id']}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("❌ League Full", callback_data="league_full")
            ])
    
    # Navigation buttons
    keyboard.append([
        InlineKeyboardButton("🔙 Back to Browse", callback_data="league_browse"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_league_management_keyboard(league_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for league management (admin only)."""
    keyboard = [
        [
            InlineKeyboardButton("👥 Manage Members", callback_data=f"league_members_{league_id}"),
            InlineKeyboardButton("📊 League Stats", callback_data=f"league_stats_{league_id}")
        ],
        [
            InlineKeyboardButton("⚙️ Edit Settings", callback_data=f"league_edit_{league_id}"),
            InlineKeyboardButton("🏁 End League", callback_data=f"league_end_{league_id}")
        ],
        [
            InlineKeyboardButton("📤 Export Data", callback_data=f"league_export_{league_id}"),
            InlineKeyboardButton("🔔 Send Message", callback_data=f"league_message_{league_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to League", callback_data=f"league_view_{league_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_league_members_keyboard(league_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    """Get keyboard for viewing league members."""
    keyboard = []
    
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("➕ Invite Members", callback_data=f"league_invite_{league_id}"),
            InlineKeyboardButton("❌ Remove Member", callback_data=f"league_remove_{league_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔙 Back to League", callback_data=f"league_view_{league_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_league_join_confirmation_keyboard(league_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for confirming league join."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Join League", callback_data=f"league_join_confirm_{league_id}"),
            InlineKeyboardButton("❌ No, Cancel", callback_data="league_browse")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_league_leave_confirmation_keyboard(league_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for confirming league leave."""
    keyboard = [
        [
            InlineKeyboardButton("❌ Yes, Leave League", callback_data=f"league_leave_confirm_{league_id}"),
            InlineKeyboardButton("✅ No, Stay", callback_data=f"league_view_{league_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_league_edit_keyboard(league_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for editing league settings."""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Edit Name", callback_data=f"league_edit_name_{league_id}"),
            InlineKeyboardButton("📝 Edit Description", callback_data=f"league_edit_desc_{league_id}")
        ],
        [
            InlineKeyboardButton("📅 Edit Dates", callback_data=f"league_edit_dates_{league_id}"),
            InlineKeyboardButton("🎯 Edit Daily Goal", callback_data=f"league_edit_goal_{league_id}")
        ],
        [
            InlineKeyboardButton("👥 Edit Max Members", callback_data=f"league_edit_members_{league_id}"),
            InlineKeyboardButton("📚 Change Book", callback_data=f"league_edit_book_{league_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Management", callback_data=f"league_manage_{league_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_league_stats_keyboard(league_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for league statistics."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Overall Progress", callback_data=f"league_stats_overall_{league_id}"),
            InlineKeyboardButton("👥 Member Progress", callback_data=f"league_stats_members_{league_id}")
        ],
        [
            InlineKeyboardButton("📈 Daily Trends", callback_data=f"league_stats_daily_{league_id}"),
            InlineKeyboardButton("🏆 Achievements", callback_data=f"league_stats_achievements_{league_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to League", callback_data=f"league_view_{league_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

"""
Bot messages and text content configuration.

This module contains all the messages, prompts, and text content used by the bot.
"""

# Welcome and Registration Messages
WELCOME_MESSAGE = """
🌟 Welcome to Read & Revive (አንባቢ)! 🌟

Your personal reading companion to make reading more engaging and rewarding.

Choose your reading mode:
"""

REGISTRATION_MESSAGE = """
📝 Let's get you registered!

Please provide the following information:
1. Your full name
2. Your city
3. Your phone number or email (optional)

Send your information in this format:
Name: [Your Name]
City: [Your City]
Contact: [Phone or Email]
"""

REGISTRATION_SUCCESS = """
✅ Registration successful! Welcome to Read & Revive!

Now let's choose your reading mode:
"""

# Reading Mode Selection
MODE_SELECTION_MESSAGE = """
📚 Choose your reading mode:

🆕 **Individual Mode**
• Read at your own pace
• Choose any book you want
• Personal progress tracking

👥 **Community Mode**
• Join reading leagues
• Read together with others
• Compete and encourage peers

Which mode would you prefer?
"""

# Book Selection Messages
INDIVIDUAL_BOOK_SELECTION = """
📚 Choose a book to start reading:

You can either:
1. Select from our featured books
2. Add your own book
"""

FEATURED_BOOKS_MESSAGE = """
📚 Our Featured Books:

{books_list}

Reply with the book number (1-{total_books}) to select.
"""

ADD_CUSTOM_BOOK_MESSAGE = """
📝 Add Your Own Book

Please provide:
Title: [Book Title]
Author: [Author Name]
Pages: [Total Pages]

Example:
Title: The Power of Habit
Author: Charles Duhigg
Pages: 371
"""

# Community League Messages
LEAGUE_INVITATION = """
👥 You've been invited to join:

**{league_name}**
📖 Reading: {book_title}
📅 Duration: {duration} days
🎯 Daily Goal: {daily_goal} pages
👥 Members: {member_count}/{max_members}

Would you like to join this reading league?
"""

LEAGUE_JOINED = """
🎉 Welcome to {league_name}!

📖 Book: {book_title}
📅 Start Date: {start_date}
🎯 Daily Goal: {daily_goal} pages
👥 Total Members: {member_count}

Use /progress to update your reading progress!
"""

# Progress Tracking Messages
PROGRESS_UPDATE_MESSAGE = """
📖 Progress Update

How many pages did you read today?
Please send just the number (e.g., 25)
"""

PROGRESS_UPDATED = """
📖 Progress Updated!

📚 Pages read today: {pages_read}
📊 Total progress: {current_pages}/{total_pages} pages
📈 Completion: {progress_percent}%
📖 Remaining: {remaining_pages} pages

{achievement_message}

{streak_message}
"""

BOOK_COMPLETED = """
🎉 Congratulations! You've completed this book! 🎉

📚 {book_title}
✍️ {author}
📖 Total pages: {total_pages}
📅 Completed in: {days_taken} days
🏆 Consistency: {consistency}%

{share_message}
"""

# Achievement Messages
ACHIEVEMENT_MESSAGES = {
    'first_book': '🎉 Achievement: First Book Started!',
    'halfway': '🚀 Achievement: Halfway There!',
    'completed': '🏆 Achievement: Book Completed!',
    'streak_3': '🔥 Achievement: 3-Day Reading Streak!',
    'streak_7': '🔥🔥 Achievement: 7-Day Reading Streak!',
    'streak_14': '🔥🔥🔥 Achievement: 14-Day Reading Streak!',
    'streak_30': '🔥🔥🔥🔥 Achievement: 30-Day Reading Streak!',
    'fast_reader': '⚡ Achievement: Fast Reader!',
    'consistency_star': '⭐ Achievement: Consistency Star!'
}

# Motivational Messages
MOTIVATIONAL_MESSAGES = [
    "🌟 Every page you read brings you closer to wisdom!",
    "📚 You're building a brighter future, one page at a time!",
    "💪 Consistency is the key to success - keep going!",
    "🎯 You're making amazing progress!",
    "✨ Reading is a gift you give to yourself every day!",
    "🚀 Your dedication is inspiring!",
    "📖 Knowledge is power - you're getting stronger!",
    "💡 Every book opens new doors in your mind!",
    "🌱 Small daily progress leads to big results!",
    "🎊 You're creating a habit that will last a lifetime!"
]

# Reminder Messages
REMINDER_MESSAGE = """
Hey {name} 👋 

Have you read your pages today? 
Just {daily_goal} minutes can make a difference!

📚 Current book: {book_title}
📊 Progress: {progress_percent}%
📖 Remaining: {remaining_pages} pages

Keep up the great work! 💪
"""

# Error Messages
ERROR_MESSAGES = {
    'invalid_pages': "❌ Please enter a valid number of pages (1-100).",
    'book_not_found': "❌ Book not found. Please try again.",
    'already_reading': "❌ You're already reading this book.",
    'registration_failed': "❌ Registration failed. Please try again.",
    'invalid_format': "❌ Invalid format. Please follow the example format.",
    'league_full': "❌ This league is full. Please try another one.",
    'not_league_member': "❌ You're not a member of this league.",
    'permission_denied': "❌ You don't have permission for this action."
}

# Help Messages
HELP_MESSAGE = """
🤖 Read & Revive Bot - Help

**Commands:**
/start - Start the bot and register
/help - Show this help message
/progress - Update your reading progress
/books - Show your current books
/stats - Show your reading statistics
/league - League information and management
/reminder - Set reading reminders
/profile - View and edit your profile

**Features:**
📚 Individual and community reading modes
📖 Track your reading progress
📊 View your statistics and achievements
🏆 Earn achievements and badges
💫 Get motivational messages
👥 Join reading leagues
⏰ Set reading reminders

Need help? Contact the admin.
"""

# Admin Messages
ADMIN_HELP_MESSAGE = """
🔧 Admin Commands

**League Management:**
/setbook - Set book for community league
/league - Manage league settings
/members - View league members
/export - Export reading data

**System Management:**
/report - Generate system reports
/backup - Create database backup
/cleanup - Clean old data
/stats - System statistics

**User Management:**
/users - View all users
/ban - Ban user from bot
/unban - Unban user
"""

# League Management Messages
LEAGUE_FULL_MESSAGE = """❌ **League is Full**

This league has reached its maximum member limit."""

# League Messages
LEAGUE_WELCOME_MESSAGE = """🏆 **League Management**

Welcome to the community reading leagues! Here you can:

• Join existing reading leagues
• Track your progress with others
• Compete on leaderboards
• Build reading communities

Choose an option below:"""

LEAGUE_BROWSE_MESSAGE = """🔍 **Available Leagues**

Found {count} league(s) you can join:

Select a league to view details and join!"""

LEAGUE_JOIN_SUCCESS = """✅ **League Joined Successfully!**

{message}

You can now:
• Track your reading progress
• View league leaderboards
• Participate in community challenges
• Receive league updates

Use /league to access your leagues."""

LEAGUE_JOIN_FAILED = """❌ **Failed to Join League**

{message}

Please try again or contact the league admin."""

LEAGUE_LEAVE_SUCCESS = """👋 **League Left Successfully**

{message}

You can rejoin this league later if you change your mind."""

LEAGUE_LEAVE_FAILED = """❌ **Failed to Leave League**

{message}

Please try again or contact support."""

LEAGUE_NOT_FOUND = """❌ **League Not Found**

The requested league could not be found or may have been removed."""

LEAGUE_ALREADY_MEMBER = """ℹ️ **Already a Member**

You are already a member of this league."""

# Admin League Management Messages
LEAGUE_CREATED = """🎉 **League Created Successfully!**

**League Name:** {name}
**League ID:** {league_id}

{message}

The league is now active and ready for members to join!"""

LEAGUE_MANAGEMENT_MENU = """⚙️ **League Management: {name}**

Manage your reading league with the options below:

• **Manage Members** - Add/remove members
• **League Stats** - View progress and analytics
• **Edit Settings** - Modify league parameters
• **End League** - Close the league
• **Export Data** - Download league data
• **Send Message** - Broadcast to all members"""

LEAGUE_EDIT_SUCCESS = """✅ **League Updated Successfully**

{field} has been updated to: {value}"""

LEAGUE_EDIT_FAILED = """❌ **Failed to Update League**

{error}

Please try again."""

# Export Messages
EXPORT_SUCCESS = """
📤 Data exported successfully!

📁 File: {filename}
📊 Records: {record_count}
📅 Date: {export_date}

The file has been saved to your device.
"""

# Statistics Messages
USER_STATS_MESSAGE = """
📊 Your Reading Statistics

📚 Total Books Started: {total_books}
🏆 Books Completed: {completed_books}
📖 Total Pages Read: {total_pages}
🔥 Current Reading Streak: {current_streak} days
📈 Average Daily Pages: {avg_daily_pages}
⏱️ Total Reading Time: {total_time} hours

{achievements_list}
"""

LEAGUE_STATS_MESSAGE = """
👥 League Statistics

📖 Book: {book_title}
📅 Progress: {league_progress}%
👥 Active Members: {active_members}
📊 Total Pages Read: {total_pages}
🎯 Average Daily Goal: {avg_daily_goal} pages

🏆 Top Performers:
{top_performers}
"""

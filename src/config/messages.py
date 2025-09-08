"""
Bot messages and text content configuration.

This module contains all the messages, prompts, and text content used by the bot.
"""

# Welcome and Registration Messages
WELCOME_MESSAGE = """
🌟 Welcome to Read & Revive (አንባቢ)! 🌟

Your personal reading companion to make reading more engaging and rewarding.

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

# Demo Page Message
DEMO_PAGE_MESSAGE = """
🎉 <b>Welcome to Your Reading Journey!</b> 🎉

Before we begin, I have something special for you! 

✨ <b>Discover the Full Experience</b> ✨

Want to see exactly how amazing your reading journey will be? Check out our interactive <a href="https://index-one-theta.vercel.app/">anbabi-bot demo page</a> to explore:

🎯 <b>Live Features Preview</b>
🚀 <b>See It In Action</b>
• Try the features before using them
• Understand the complete flow
• Get inspired by the possibilities
• Experience the full bot capabilities

💫 <b>Trust me, you'll love what you see!</b>
"""

# Reading Mode Selection
MODE_SELECTION_MESSAGE = """
📚 <b>Choose your reading mode:</b>

🆕 <b>Individual Mode</b>
• Read at your own pace
• Choose any book you want
• Personal progress tracking

👥 <b>Community Mode</b>
• Join reading leagues
• Read together with others
• Compete and encourage peers

<b><i>You can switch anytime between the modes. Enjoy solo reading and community challenges!</i></b>

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

<b>{league_name}</b>
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

<b>Commands:</b>
/start - Start the bot and register
/help - Show this help message
/progress - Update your reading progress
/books - Show your current books
/stats - Show your reading statistics
/league - League information and management
/reminder - Set reading reminders
/profile - View and edit your profile

<b>Features:</b>
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

<b>League Management:</b>
/setbook - Set book for community league
/league - Manage league settings
/members - View league members
/export - Export reading data

<b>System Management:</b>
/report - Generate system reports
/backup - Create database backup
/cleanup - Clean old data
/stats - System statistics

<b>User Management:</b>
/users - View all users
/ban - Ban user from bot
/unban - Unban user
"""

# League Management Messages
LEAGUE_FULL_MESSAGE = """❌ <b>League is Full</b>

This league has reached its maximum member limit."""

# League Messages
LEAGUE_WELCOME_MESSAGE = """🏆 <b>League Management</b>

Welcome to the community reading leagues! Here you can:

• Join existing reading leagues
• Track your progress with others
• Compete on leaderboards
• Build reading communities

Choose an option below:"""

LEAGUE_BROWSE_MESSAGE = """🔍 <b>Available Leagues</b>

Found {count} league(s) you can join:

Select a league to view details and join!"""

LEAGUE_JOIN_SUCCESS = """✅ <b>League Joined Successfully!</b>

{message}

You can now:
• Track your reading progress
• View league leaderboards
• Participate in community challenges
• Receive league updates

Use /league to access your leagues."""

LEAGUE_JOIN_FAILED = """❌ <b>Failed to Join League</b>

{message}

Please try again or contact the league admin."""

LEAGUE_LEAVE_SUCCESS = """👋 <b>League Left Successfully</b>

{message}

You can rejoin this league later if you change your mind."""

LEAGUE_LEAVE_FAILED = """❌ <b>Failed to Leave League</b>

{message}

Please try again or contact support."""

LEAGUE_NOT_FOUND = """❌ <b>League Not Found</b>

The requested league could not be found or may have been removed."""

LEAGUE_ALREADY_MEMBER = """ℹ️ <b>Already a Member</b>

You are already a member of this league."""

# Admin League Management Messages
LEAGUE_CREATED = """🎉 <b>League Created Successfully!</b>

<b>League Name:</b> {name}
<b>League ID:</b> {league_id}

{message}

The league is now active and ready for members to join!"""

LEAGUE_MANAGEMENT_MENU = """⚙️ <b>League Management: {name}</b>

Manage your reading league with the options below:

• <b>Manage Members</b> - Add/remove members
• <b>League Stats</b> - View progress and analytics
• <b>Edit Settings</b> - Modify league parameters
• <b>End League</b> - Close the league
• <b>Export Data</b> - Download league data
• <b>Send Message</b> - Broadcast to all members"""

LEAGUE_EDIT_SUCCESS = """✅ <b>League Updated Successfully</b>

{field} has been updated to: {value}"""

LEAGUE_EDIT_FAILED = """❌ <b>Failed to Update League</b>

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
